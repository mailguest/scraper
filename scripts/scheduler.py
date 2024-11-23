import schedule
import time
import json
from utils.log_utils import setup_logging
from scripts.scrape_list import scrape  # 列表爬虫
from scripts.scrape_content import scrape_all_articles  # 内容爬虫
from scripts.scrape_ipproxy import scrape_ipproxies  # IP 代理爬虫
from croniter import croniter
from datetime import datetime
from config.config import Config
# 使用日志工具类设置日志
logger = setup_logging("Scheduler", "scheduler.log")

# 读取调度配置文件
def load_schedule_config():
    with open(Config.SCHEDULE_CONFIG, 'r') as f:
        return json.load(f)

# 列表爬虫任务
def scrape_list(logger):
    logger.info("Running scheduled scraping scrape_list job...")
    try:
        scrape()
        logger.info("Scraping completed successfully.")
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")

# 内容爬虫任务
def scrape_content(logger):
    logger.info("Running scheduled scraping scrape_content job...")
    try:
        scrape_all_articles(logger)
        logger.info("Content scraping completed successfully.")
    except Exception as e:
        logger.error(f"Content scraping failed: {str(e)}")

# IP 代理爬虫任务
def scrape_ip_proxies(logger):
    logger.info("Running scheduled scraping scrape_ip_proxies job...")
    try:
        # 从代理网站获取 IP 代理
        scrape_ipproxies(logger)
        logger.info("IP proxy scraping completed successfully.")
    except Exception as e:
        logger.error(f"IP proxy scraping failed: {str(e)}")

# 设置定时任务
def schedule_jobs(config):
    list_scraper_cron = config['list_scraper_cron']
    content_scraper_cron = config['content_scraper_cron']
    ip_proxy_scraper_cron = config['ip_proxy_scraper_cron']

    # 获取当前时间
    now = datetime.now()

    # 设置 IP 代理爬虫的任务调度
    ip_proxy_next_run = croniter(ip_proxy_scraper_cron, now).get_next(datetime)
    schedule.every().day.at(ip_proxy_next_run.strftime('%H:%M')).do(scrape_ip_proxies, logger=logger)

    # 设置列表爬虫的任务调度
    list_next_run = croniter(list_scraper_cron, now).get_next(datetime)
    schedule.every().day.at(list_next_run.strftime('%H:%M')).do(scrape_list, logger=logger)

    # 设置内容爬虫的任务调度
    content_next_run = croniter(content_scraper_cron, now).get_next(datetime)
    schedule.every().day.at(content_next_run.strftime('%H:%M')).do(scrape_content, logger=logger)


def main():
    logger.info("Scheduler started...")

    # 加载调度配置
    config = load_schedule_config()

    # 立即执行 IP 代理爬虫
    logger.info("Executing IP proxy scraping job immediately upon start...")
    scrape_ip_proxies(logger)
    time.sleep(10)
    
    # 立即执行列表爬虫
    logger.info("Executing list scraping job immediately upon start...")
    scrape_list(logger)
    time.sleep(10)

    logger.info("Executing content scraping job immediately upon start...")
    scrape_content(logger)
    time.sleep(10)

    # 设置定时任务
    logger.info("Setting up scheduled jobs...")
    schedule_jobs(config)

    # 开始定时任务循环
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
