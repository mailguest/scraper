from logging import Logger
from config.db import DBConfig
from scripts.scrape_factory import ContentScraperFactory
from utils.ArticleMapper import ArticleMapper
from utils.Article import Article
from datetime import datetime

def scrape_article_content(article: Article, logger:Logger, db:DBConfig) -> int:
    """
    抓取单篇文章内容
    """
    success_data_count = 0
    try:
        scraper = ContentScraperFactory.create_scraper(article.source, article.list_uri)
        if scraper is None:
            return success_data_count
    except ValueError as e:
        # logger.warning(e)
        return  success_data_count
    
    try:
        content, status = scraper.scrape() or (None, "failed")
    except (TypeError, ValueError) as e:
        logger.error(f"抓取失败: {str(e)}")
        return success_data_count
    
    if content:
        article.content = content
    else:
        logger.warning(f"爬取Content为空，UUID is： {article.UUID}. ")

    try:
        article.status = status
        article.content_uri = scraper.get_connect_url()
        article.updated_at = datetime.now()
        # 保存文章内容
        mapper = ArticleMapper(db=db, logger=logger)
        success_data_count = mapper.update_article(article)
        logger.info(f"Saved article content for {article.UUID}.json")
    except Exception as e:
        logger.error(f"保存文章内容失败: {str(e)}")
    finally:
        return success_data_count

def scrape_all_articles(logger, db: DBConfig) -> int:
    """
    主入口：抓取所有待处理的文章
    """
    success_data_count = 0
    try:
        mapper = ArticleMapper(db=db, logger=logger)
        articles = mapper.get_articles_by_status(status="pending")

        for article in articles:
            i = scrape_article_content(article, logger, db)
            success_data_count += i
        return success_data_count
    except Exception as e:
        logger.error(f"主入口：抓取所有待处理的文章: {str(e)}")
        raise e
