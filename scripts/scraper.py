import json
from scripts.factory import ScraperFactory
from datetime import datetime
import os
from scripts.scrape_ipproxy import get_random_proxies

# 加载 URLs 配置文件
def load_urls():
    with open("config/urls.json") as file:
        return json.load(file)["websites"]

# 加载现有数据
def load_existing_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

# 保存数据到一个文件中，按日期切分文件
def save_data(new_data):
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"data/scraped_list_{today}.json"

    # 加载现有的数据
    existing_data = load_existing_data(filename)

    # 获取已存在数据的所有 uri，便于快速查重
    existing_uris = {item['uri'] for item in existing_data}

    # 过滤掉重复的项，仅保留新的数据
    unique_data = [item for item in new_data if item['uri'] not in existing_uris]

    # 如果有新数据，追加到文件中
    if unique_data:
        existing_data.extend(unique_data)
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=4)
    else:
        print("No new unique data to add.")

# 主抓取逻辑
def scrape(logger=None):
    try:
        proxy = get_random_proxies()
        logger.info(f"Using proxy: {proxy}")
            
        # 确保 proxy 是正确的格式
        if proxy and isinstance(proxy, dict):
            proxy_url = f"http://{proxy.get('ip')}:{proxy.get('port')}"  # 使用 get() 方法安全获取值
        else:
            logger.warning("Invalid proxy format or no proxy available")
            
        websites = load_urls()
        all_scraped_data = []

        for site in websites:
            try:
                scraper = ScraperFactory.create_scraper(site["name"], site["url"], site["limit"])
                scraped_data = scraper.scrape()
                if scraped_data:
                    all_scraped_data.extend(scraped_data)  # 将每个网站的数据加入到总数据中
            except ValueError as e:
                logger.error(f"Error scraping {site['name']}: {e}")
        
        if all_scraped_data:
            save_data(all_scraped_data)  # 保存所有网站的抓取数据到一个文件

    except Exception as e:
        if logger:
            logger.error(f"Error in scrape function: {str(e)}")
        raise e

if __name__ == "__main__":
    scrape()
