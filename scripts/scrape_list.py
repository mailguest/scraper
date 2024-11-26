import json
from logging import Logger
from scripts.scrape_factory import ScraperFactory
from datetime import datetime
import os
from scripts.scrape_ipproxy import get_random_proxies
from config.config import Config
from flask import current_app
from utils.ArticleMapper import ArticleMapper
from utils.log_utils import setup_logging  # 引入日志工具类


# 加载 URLs 配置文件
def load_urls():
    with open(Config.URL_CONFIG) as file:
        return json.load(file)["websites"]

# 保存数据到一个文件中，按日期切分文件
def save_data(new_data, logger:Logger):
    try:
        article_mapper = ArticleMapper(db=current_app.config["db"], logger=logger)

        # 根据 list_uri 过滤掉重复的项，仅保留新的数据
        unique_data = [
            item for item in new_data 
            if article_mapper.get_article_by_list_uri(item.list_uri) is None
        ]
        logger.debug(f"list_uri 过滤后数量: {len(unique_data)}")


        # 根据 UUID 过滤掉重复的项，仅保留新的数据
        unique_data = [
            item for item in unique_data
            if article_mapper.get_article_by_uuid(item.UUID) is None
        ]
        logger.debug(f"UUID 过滤后数量: {len(unique_data)}")


        if unique_data and len(unique_data) > 0:
            logger.info(f"Found {len(unique_data)} new unique data to add.")
            # 逐个插入并记录错误
            for article in unique_data:
                try:
                    article_mapper.insert_article(article)
                except Exception as e:
                    logger.error(f"插入文章失败: UUID={article.UUID}, title={article.title}，错误信息: {str(e)}")
        else:
            logger.info("No new unique data to add.")
    except Exception as e:
        logger.error(f"保存数据时发生错误: {str(e)}")
        raise

# 主抓取逻辑
def scrape(logger:Logger):
    try:
        proxy = get_random_proxies()
        # 确保 proxy 是正确的格式
        if proxy and isinstance(proxy, dict):
            proxy_url = f"http://{proxy.get('ip')}:{proxy.get('port')}"  # 使用 get() 方法安全获取值
        else:
            logger.warning("Invalid proxy format or no proxy available")
            
        websites = load_urls()
        all_scraped_data = []

        for site in websites:
            try:
                scraper = ScraperFactory.create_scraper(site["name"], site["url"], limit=site.get('limit', 30))
                scraped_data = scraper.scrape()
                if scraped_data:
                    # 确保 scraped_data 是列表
                    if isinstance(scraped_data, list):
                        all_scraped_data.extend(scraped_data)
                    else:
                        all_scraped_data.append(scraped_data)
            except ValueError as e:
                logger.warning(f"Error scraping {site['name']}: {e}")
        
        if all_scraped_data and len(all_scraped_data) > 0:
            save_data(all_scraped_data, logger)  # 保存所有网站的抓取数据到一个文件

    except Exception as e:
        if logger:
            logger.error(f"Error in scrape function: {str(e)}")
        raise e

if __name__ == "__main__":
    logger = setup_logging("SinaFinanceScraper", "sina_scraper.log")
    scrape(logger=logger)
