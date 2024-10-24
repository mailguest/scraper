# wallstreetcn_scraper.py
import json
import requests
from scripts.base_scraper import BaseScraper
from utils.log_utils import setup_logging  # 引入日志工具类
from datetime import datetime
import uuid
from bs4 import BeautifulSoup


class WallStreetCNScraper(BaseScraper):
    """
    从 WallStreetCN 网站抓取文章列表
    """
    def __init__(self, url, limit):
        super().__init__(url, limit)
        self.logger = setup_logging("WallStreetCNScraper", "wallstreet_scraper.log")  # 设置日志


    def scrape(self):
        url = self.url.replace("{limit}", str(self.limit))

        # 记录开始抓取的日志
        self.logger.info(f"Starting scraping for WallStreetCN with URL: {self.url}")

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            items = data['data']['items']
            scraped_data = []
            for item in items:
                # 提取文章日期，并转换为年月日格式
                timestamp = item['resource']['display_time']
                date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')

                article = {
                    'UUID': uuid.uuid5(uuid.NAMESPACE_DNS, item['resource']['title']).hex,
                    'title': item['resource']['title'],
                    'uri': item['resource']['uri'].split("?")[0],  # 去掉 URL 中的查询参数
                    'content_short': item['resource'].get('content_short', None),
                    'date': date,
                    'source': 'WallStreetCN'  # 增加文章来源字段
                }

                if article.get('content_short') is None:
                    # 如果缺少 'content_short'，记录警告并跳过此项
                    self.logger.warning(f"Missing 'content_short' for article {item['resource'].get('title', 'Unknown Title')}")

                scraped_data.append(article)

            self.logger.info(f"Scraping completed for WallStreetCN, total articles: {len(scraped_data)}")
            return scraped_data
        else:
            return []


class WallStreetCNContentScraper(BaseScraper):
    def __init__(self, url):
        super().__init__(url)
        self.__content_url = None

        with open("config/urls.json") as file:
            self.__content_url_template = json.load(file)["WallStreetCNContent"]["url"]
        
        self.logger = setup_logging("WallStreetCNContentScraper", "wallstreet_content_scraper.log")
            

    """
    从 WallStreetCN 网站抓取文章内容
    """
    def scrape(self):
        # import pdb
        # pdb.set_trace()

        try:
            # 生成 API 请求链接
            self.__create_content_url()
            self.logger.info(f"Fetching content from {self.__content_url} ")
            if self.__content_url is None:
                self.logger.error("Failed to create content URL.")
                return None
            
            response = requests.get(self.__content_url)
            if response.status_code == 200:
                data = response.json()

                # 获取文章的主要内容并去除 HTML 标签
                content_html = data['data']['content']
                soup = BeautifulSoup(content_html, "html.parser")
                content_text = soup.get_text(strip=True)  # 去除 HTML 标签，获取纯文本

                return content_text
            else:
                self.logger.error(f"Failed to fetch content: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching content from {self.__content_url}, List url is {self.url}: {e}")
            return None
    
    def __create_content_url(self):
        # 从 uri 中提取文章 ID 并生成 API 请求链接
        self.url = self.url.split("?")[0]  # 去掉查询参数
        article_id = self.url.split('/')[-1]
        self.__content_url = self.__content_url_template.replace("{article_id}", article_id)
    
    def get_content_url(self):
        return self.__content_url
