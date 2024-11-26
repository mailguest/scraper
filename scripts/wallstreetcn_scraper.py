# wallstreetcn_scraper.py
import json
from httpcore import ProxyError
import requests
from scripts.base_scraper import BaseScraper
from utils.log_utils import setup_logging  # 引入日志工具类
from datetime import datetime
import uuid
from bs4 import BeautifulSoup
from scripts.scrape_ipproxy import get_random_proxies
from utils.Article import Article
from config.config import Config

class WallStreetCNScraper(BaseScraper):
    """
    从 WallStreetCN 网站抓取文章列表
    """
    def __init__(self, url, limit=30, **kwargs):
        super().__init__(url, **kwargs)
        self.limit = limit
        self.logger = setup_logging("WallStreetCNScraper", "wallstreet_scraper.log")  # 设置日志

    def get_connect_url(self):
        return self.url

    def scrape(self):
        self.url = self.url.replace("{limit}", str(self.limit))

        # 获取代理
        proxies = get_random_proxies()

        # 记录开始抓取的日志
        self.logger.info(f"开始抓取 WallStreetCN，URL: {self.url}, 代理: {str(proxies)}")

        if proxies is None:
            response = requests.get(self.url, headers=self.headers)
        else:
            try:
                response = requests.get(self.url, proxies=proxies, headers=self.headers)
            except Exception as e:
                self.logger.error(f"代理获取失败，使用普通请求: {e}")
            finally:
                response = requests.get(self.url, headers=self.headers)
        
        scraped_data: list[Article] = []
        
        if response.status_code == 200:
            data = response.json()
            items = data['data']['items']
            for item in items:
                resource: dict = item['resource']
                if "articles" in  resource.keys():
                    articles = resource['articles']
                    for article in articles:
                        article["display_time"] = item.get("most_recent_content_time", datetime.now().timestamp())
                        scraped_data.append(self.analyze_content(article))
                else:
                    scraped_data.append(self.analyze_content(resource))
            self.logger.info(f"抓取 WallStreetCN 完成，总文章数: {len(scraped_data)}")
        
        return scraped_data
    
    # 分析内容
    def analyze_content(self, item) -> Article:
        # 提取文章日期，并转换为年月日格式
        timestamp = item['display_time']
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

        article = Article(
            UUID=uuid.uuid5(uuid.NAMESPACE_DNS, item['title']).hex,
            title=item['title'],
            content=None,
            content_short=item.get('content_short', item['title']),
            date=date,
            source='WallStreetCN',  # 增加文章来源字段
            list_uri=item['uri'].split("?")[0],  # 去掉 URL 中的查询参数
            content_uri=None,
            status='pending',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        if article.content_short is None:
            # 如果缺少 'content_short'，记录警告并跳过此项
            self.logger.warning(f"缺少 'content_short'，文章标题: {item.get('title', '未知标题')}")
        
        return article


class WallStreetCNContentScraper(BaseScraper):
    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)
        self.__content_url = None

        with open(Config.URL_CONFIG) as file:
            self.__content_url_template = json.load(file)["WallStreetCNContent"]["url"]
        
        self.logger = setup_logging("WallStreetCNContentScraper", "wallstreet_content_scraper.log")
            

    """
    从 WallStreetCN 网站抓取文章内容
    """
    def scrape(self):

        try:
            # 生成 API 请求链接
            self.__set_content_url()
            if self.__content_url is None:
                self.logger.error("生成内容 URL 失败。")
                return None
            
            # 获取代理
            proxies = get_random_proxies()
            self.logger.info(f"开始抓取 WallStreetCN 文章内容，URL: {self.url}, 代理: {str(proxies)}")

            if proxies is None:
                response = requests.get(self.__content_url, headers=self.headers)
            else:
                try:
                    response = requests.get(self.__content_url, proxies=proxies, headers=self.headers)
                except Exception as e:
                    self.logger.error(f"代理获取失败，使用普通请求: {e}")
                finally:
                    response = requests.get(self.__content_url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()

                # 获取文章的主要内容并去除 HTML 标签
                content_html = data['data'].get('content', None)
                if content_html is None:
                    self.logger.error(f"获取内容失败: {data.get('message', None)} code: {data.get('code', None)}")
                    return None, "failed"
                soup = BeautifulSoup(content_html, "html.parser")
                content_text = soup.get_text(strip=True)  # 去除 HTML 标签，获取纯文本

                return content_text, "success"
            else:
                self.logger.error(f"获取内容失败: {response.status_code}")
                return None, "failed"
        except Exception as e:
            self.logger.error(f"从 {self.__content_url} 获取内容时出错，列表 URL 为 {self.url}: {e}")
            return None, "pending"
    
    def __set_content_url(self):
        # 从 uri 中提取文章 ID 并生成 API 请求链接
        self.url = self.url.split("?")[0]  # 去掉查询参数
        article_id = self.url.split('/')[-1]
        self.__content_url = self.__content_url_template.replace("{article_id}", article_id)
    
    def get_connect_url(self):
        return self.__content_url
