from concurrent.futures import thread
from math import log
import os
import threading
import time
import json

from sympy import content
from torch import log_
from utils.TaskLogsMapper import TaskLogsMapper
from utils.log_utils import setup_logging
from scripts.scrape_list import scrape  # 列表爬虫
from scripts.scrape_content import scrape_all_articles  # 内容爬虫
from scripts.scrape_ipproxy import scrape_ipproxies  # IP 代理爬虫
from config.config import Config
from flask import Flask, g
from config.db import DBConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import traceback

# 使用日志工具类设置日志
logger = setup_logging("Scheduler", "scheduler.log")

# 读取调度配置文件
def load_schedule_config():
    """加载调度配置"""
    try:
        with open(Config.SCHEDULE_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config['jobs']
    except Exception as e:
        logger.error(f"加载调度配置时出错: {str(e)}")
        # 记录完整的堆栈跟踪
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        return []

# 创建锁对象字典
locks = {
    'list': threading.Lock(),
    'content': threading.Lock(),
    'ip_proxy': threading.Lock()
}

# 列表爬虫任务
def scrape_list(logger, task_logs_mapper: TaskLogsMapper):
    if not locks["list"].acquire(blocking=False):
        logger.info("列表爬虫任务正在运行，跳过本次执行。")
        return False

    logger.info("正在运行定时抓取 scrape_list 任务...")
    log_id, start_time = task_logs_mapper.log_task_start("list_scraper")
    data_count = 0
    try:
        data_count = scrape(logger=logger)
        logger.info("文章列表任务抓取完成。")
    except Exception as e:
        # 详细记录错误信息
        logger.error(f"文章列表抓取失败: {str(e)}")
        # 记录完整的堆栈跟踪
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        # 不抛出异常，让调度器继续运行
        return False
    finally:
        task_logs_mapper.log_task_end(log_id, start_time, data_count)
        locks["list"].release()
    return True

# 内容爬虫任务
def scrape_content(logger, task_logs_mapper):
    if not locks["content"].acquire(blocking=False):
        logger.info("内容爬虫任务正在运行，跳过本次执行。")
        return False

    logger.info("正在运行定时抓取 scrape_content 任务...")
    log_id, start_time = task_logs_mapper.log_task_start("content_scraper")
    data_count = 0
    try:
        data_count = scrape_all_articles(logger)
        logger.info("文章正文抓取完成。")
    except Exception as e:
        # 详细记录错误信息
        logger.error(f"文章正文抓取失败: {str(e)}")
        # 记录完整的堆栈跟踪
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        # 不抛出异常，让调度器继续运行
        return False
    finally:
        task_logs_mapper.log_task_end(log_id, start_time, data_count)
        locks["content"].release()
    return True

# IP 代理爬虫任务
def scrape_ip_proxies(logger, task_logs_mapper):
    if not locks["ip_proxy"].acquire(blocking=False):
        logger.info("IP 代理爬虫任务正在运行，跳过本次执行。")
        return False

    logger.info("正在运行定时抓取 scrape_ip_proxies 任务...")
    log_id, start_time = task_logs_mapper.log_task_start("ip_proxy_scraper")
    data_count = 0  
    try:
        # 从代理网站获取 IP 代理
        data_count = scrape_ipproxies(logger)
        logger.info("IP 代理抓取完成。")
    except Exception as e:
        logger.error(f"IP 代理抓取失败: {str(e)}")
    finally:
        task_logs_mapper.log_task_end(log_id, start_time, data_count)
        locks["ip_proxy"].release()

# 设置定时任务
def schedule_jobs(jobs, app):
    scheduler = BackgroundScheduler()

    global logger
    task_logs_mapper = TaskLogsMapper(app.config['db'], logger)
    
    for job in jobs:
        if not job.get('enabled', True):
            continue
            
        function_map = {
            "scrape_list": lambda: with_app_context(app, lambda: scrape_list(logger, task_logs_mapper)),
            "scrape_content": lambda: with_app_context(app, lambda: scrape_content(logger, task_logs_mapper)),
            "scrape_ip_proxies": lambda: scrape_ip_proxies(logger, task_logs_mapper)
        }
        
        if job['function'] in function_map:
            scheduler.add_job(
                function_map[job['function']],
                CronTrigger.from_crontab(job['cron']),
                id=job['id']
            )
    
    scheduler.start()
    return scheduler

def with_app_context(app, func):
    """在应用上下文中执行函数"""
    with app.app_context():
        return func()

def main():
    logger.info("Scheduler started...")
    last_config_mtime = 0
    current_scheduler = None

    app = Flask(__name__)
    app.config['db'] = DBConfig()

    while True:
        try:
            # 检查配置文件是否有更新
            current_mtime = os.path.getmtime(Config.SCHEDULE_CONFIG)
            if current_mtime > last_config_mtime:
                logger.info("配置文件已更改，重新加载任务...")

                # 如果存在旧的调度器，先关闭它
                if current_scheduler:
                    current_scheduler.shutdown()

                # 加载调度配置
                jobs = load_schedule_config()

                # 设置新的定时任务
                current_scheduler = schedule_jobs(jobs, app)

                last_config_mtime = current_mtime

            # 不需要 schedule.run_pending() 了
            # APScheduler 在后台自动运行
            time.sleep(60)  # 每分钟检查一次配置文件变化
        except Exception as e:
            logger.error(f"调度器主循环中出错: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    main()
