import json
import os
from scripts.factory import ContentScraperFactory
from utils.search_utils import SearchUtils

def is_file_exists(article):
    dir_path = os.path.join(os.path.abspath("data"), article['date'])
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # 根据 UUID 检查文件是否已经存在
    file_path = os.path.join(dir_path, f"{article['UUID']}.json")
    return os.path.exists(file_path)

def save_article_content(uuid, content_data):
    dir_path = os.path.join(os.path.abspath("data"), content_data['date'])
    file_path = os.path.join(dir_path, f"{uuid}.json")
    # 将内容保存为 JSON 文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(content_data, f, ensure_ascii=False, indent=4)

def scrape_article_content(article, logger):
    """
    抓取单篇文章内容
    """
    uuid = article['UUID']
    if is_file_exists(article):
        print(f"File {uuid}.json already exists. Skipping...")
        return
    
    scraper = ContentScraperFactory.create_scraper(article['source'], article['uri'])
    if scraper is None:
        # logger.warning(f"Scraper not found for {article['source']}. Skipping...")
        return 
    
    content = scraper.scrape()
    
    # 构建文章内容数据
    content_data = {
        "UUID": uuid,
        "title": article['title'],
        "uri": scraper.get_content_url(),
        "content": article['content_short'],
        "content_short": article['content_short'],
        "date": article['date'],
        "source": article['source'],
        "status": "failed"
    }
    if content:
        content_data['content'] = content
        content_data['status'] = "success"
        logger.info(f"Saved article content for {uuid}.json")
    else:
        logger.warning(f"Failed to scrape content for {uuid}. Skipping...")
    # 保存文章内容
    save_article_content(uuid, content_data)

def scrape_all_articles(logger):
    """
    主入口：抓取所有文章内容
    """
    articles = SearchUtils(logger=logger).load_all_data()
    
    for article in articles:
        scrape_article_content(article, logger)
