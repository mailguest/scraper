# sina_finance_scraper.py
import requests
from scripts.base_scraper import BaseScraper
from utils.log_utils import setup_logging  # 引入日志工具类
from datetime import datetime
import uuid
from bs4 import BeautifulSoup

class SinaFinanceScraper(BaseScraper):
    """
    从新浪财经网站抓取文章列表
    """
    def __init__(self, url, limit):
        super().__init__(url, limit)
        self.logger = setup_logging("SinaFinanceScraper", "sina_scraper.log")

    def scrape(self):

        url = self.url.replace("{limit}", str(self.limit))

        # 记录开始抓取的日志
        self.logger.info(f"Starting scraping for Sina Finance with URL: {self.url}")

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            items = data['result']['data']
            scraped_data = []
            for item in items:
                # 提取文章日期，并转换为年月日格式
                timestamp = int(item['ctime'])  # 使用 'ctime' 字段
                date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
                
                article = {
                    'UUID': uuid.uuid5(uuid.NAMESPACE_DNS, item['title']).hex,
                    'title': item['title'],
                    'uri': item['url'].split("?")[0],   # 去掉 URL 中的查询参数
                    'content_short': item.get('intro', None),
                    'date': date,
                    'source': 'SinaFinance'  # 增加文章来源字段
                }

                if article.get('content_short') is None:
                    # 如果缺少 'content_short'，记录警告并跳过此项
                    self.logger.warning(f"Missing 'content_short' for article {item['resource'].get('title', 'Unknown Title')}")

                scraped_data.append(article)

            self.logger.info(f"Scraping completed for Sina Finance, total articles: {len(scraped_data)}")

            return scraped_data
        else:
            return []


class SinaContentScraper(BaseScraper):
    def __init__(self, url):
        super().__init__(url)
        self.logger = setup_logging("SinaContentScraper", "sina_content_scraper.log")

    """
    从新浪财经网站抓取文章内容
    """
    def scrape(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                content = soup.find('div', {'class': 'article-content'})  # 假设内容在 article-content 中
                if content:
                    return content.text.strip()
            return None
        except Exception as e:
            print(f"Error fetching content from {self.url}: {e}")
            return None