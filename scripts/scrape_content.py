import json
import os
from scripts.scrape_factory import ContentScraperFactory
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
    
    content = scraper.scrape()
    
    if content:
        article.content = content
        article.status = "success"
        article.content_uri = scraper.get_connect_url()
        article.updated_at = datetime.now()

        logger.info(f"Saved article content for {article.UUID}.json")
    else:
        logger.warning(f"Failed to scrape content for {article.UUID}. Skipping...")
    # 保存文章内容
    article_mapper = ArticleMapper()
    article_mapper.update_article(article)
    article_mapper.close()

def scrape_all_articles(logger):
    """
    主入口：抓取所有待处理的文章
    """
    articles = ArticleMapper().get_articles_by_status()

    for article in articles:
        scrape_article_content(article, logger)
