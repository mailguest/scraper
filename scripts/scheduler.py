import os
from re import L
import threading
import time
import json

from utils.TaskLogsMapper import TaskLogsMapper
from utils.log_utils import setup_logging
from scripts.scrape_list import scrape  # 列表爬虫
from scripts.scrape_content import scrape_all_articles  # 内容爬虫
from scripts.scrape_ipproxy import scrape_ipproxies  # IP 代理爬虫
from config.config import Config
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import traceback


# 读取调度配置文件
def load_schedule_config(logger):
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

def task_wrapper(key, task_func, logger):
    """包装任务函数，处理日志记录和任务状态管理"""
    with db.get_connection() as connection:
        task_logs_mapper = TaskLogsMapper(connection, logger)
        log_id, start_time = task_logs_mapper.log_task_start(key)
        data_count = 0
        try:
            data_count = task_func(logger, connection)
            logger.info(f"{key} 任务完成。")
        except Exception as e:
            logger.error(f"{key} 任务失败: {str(e)}")
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return False
        finally:
            task_logs_mapper.log_task_end(log_id, start_time, data_count)
    return True

def run_task_with_lock(key, logger):
    """通用任务调度函数，处理锁定、任务执行和日志记录"""
    if not locks[key].acquire(blocking=False):
        logger.info(f"{key}任务正在运行，跳过本次执行。")
        return False

    def task(logger, connection):
        return funcs[key](logger=logger, db=connection)

    result = task_wrapper(key, task, logger)
    locks[key].release()
    return result


# 创建锁对象字典
locks = {
    'list_scraper': threading.Lock(),
    'content_scraper': threading.Lock(),
    'ip_proxy_scraper': threading.Lock()
}

funcs = {
    'list_scraper': scrape,
    'content_scraper': scrape_all_articles,
    'ip_proxy_scraper': scrape_ipproxies
}


# 设置定时任务
def schedule_jobs(jobs, logger):
    scheduler = BackgroundScheduler()


    for job in jobs:
        if not job.get('enabled', True):
            continue

        job_key = job.get('id', None)
        job_func = funcs.get(job_key, None)
        job_cron = job.get('cron', None)

        if not job_key or not job_func or not job_cron:
            logger.error(f"定时任务配置错误: {job}")
            continue
        
        job_trigger = CronTrigger.from_crontab(job_cron)
        job_args = [job_key, logger]

        logger.info(f"添加定时任务: {job_func.__name__}")
        scheduler.add_job(func=run_task_with_lock, trigger=job_trigger, args=job_args, id=job_key)
        
    
    scheduler.start()
    return scheduler

def main():
    # 使用日志工具类设置日志
    logger = setup_logging("Scheduler", "scheduler.log")
    logger.info("Scheduler started...")
    last_config_mtime = 0
    current_scheduler = None

    while True:
        try:
            # 检查配置文件是否有更新
            current_mtime = os.path.getmtime(Config.SCHEDULE_CONFIG)
            if current_mtime > last_config_mtime:
                logger.info("重新加载定时任务...")

                # 如果存在旧的调度器，先关闭它
                if current_scheduler:
                    current_scheduler.shutdown()

                # 加载调度配置
                jobs = load_schedule_config(logger)

                # 设置新的定时任务
                current_scheduler = schedule_jobs(jobs, logger)

                last_config_mtime = current_mtime

            # 不需要 schedule.run_pending() 了
            # APScheduler 在后台自动运行
            time.sleep(60)  # 每分钟检查一次配置文件变化
        except Exception as e:
            logger.error(f"调度器主循环中出错: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    db = Config.DB
    main()
