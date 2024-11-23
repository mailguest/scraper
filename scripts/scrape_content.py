import json
import os
from scripts.scrape_factory import ContentScraperFactory
from flask import current_app
from utils.ArticleMapper import ArticleMapper
from utils.Article import Article
from datetime import datetime

def scrape_article_content(article: Article, logger):
    """
    抓取单篇文章内容
    """
    scraper = ContentScraperFactory.create_scraper(article.source, article.list_uri)
    if scraper is None:
        # logger.warning(f"Scraper not found for {article['source']}. Skipping...")
        return 
    
    try:
        content, status = scraper.scrape() or (None, "failed")
    except (TypeError, ValueError) as e:
        logger.error(f"抓取失败: {str(e)}")
        return
    
    if content:
        article.content = content
    else:
        logger.warning(f"爬取Content为空，UUID is： {article.UUID}. ")

    article.status = status
    article.content_uri = scraper.get_connect_url()
    article.updated_at = datetime.now()
    # 保存文章内容
    mapper = ArticleMapper(db=current_app.config["db"], logger=logger)
    mapper.update_article(article)
    logger.info(f"Saved article content for {article.UUID}.json")

def scrape_all_articles(logger):
    """
    主入口：抓取所有待处理的文章
    """
    try:
        mapper = ArticleMapper(db=current_app.config["db"], logger=logger)
        articles = mapper.get_articles_by_status(status="pending")

        for article in articles:
            scrape_article_content(article, logger)
    except Exception as e:
        logger.error(f"主入口：抓取所有待处理的文章: {str(e)}")
        raise e
