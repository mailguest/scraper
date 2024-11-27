# sina_finance_scraper.py
from email import charset
from httpcore import ProxyError
import requests
from scripts.base_scraper import BaseScraper
from utils.log_utils import setup_logging  # 引入日志工具类
from datetime import datetime
import uuid
from scripts.scrape_ipproxy import get_random_proxies
from utils.Article import Article

class SinaFinanceScraper(BaseScraper):
    """
    从新浪财经网站抓取文章列表
    """
    def __init__(self, url, limit=30, **kwargs):
        super().__init__(url, **kwargs)
        self.limit = limit
        self.logger = setup_logging("SinaFinanceScraper", "sina_scraper.log")

    def get_connect_url(self):
        return self.url

    def scrape(self):

        self.url = self.url.replace("{limit}", str(self.limit))

        # 获取代理
        proxies = get_random_proxies()
        # 记录开始抓取的日志
        self.logger.info(f"开始抓取新浪财经，URL: {self.url}, 代理: {str(proxies)}")

        if proxies is None:
            response = requests.get(self.url, headers=self.headers)
        else:
            try:
                response = requests.get(self.url, proxies=proxies, headers=self.headers)
            except Exception as e:
                self.logger.error(f"代理获取失败，使用普通请求: {e}")
            finally:
                response = requests.get(self.url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            items = data['result']['data']
            scraped_data: list[Article] = []
            for item in items:
                # 提取文章日期，并转换为年月日格式
                timestamp = int(item['ctime'])  # 使用 'ctime' 字段
                date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                
                article = Article(
                    UUID=uuid.uuid5(uuid.NAMESPACE_DNS, item['title']).hex,
                    title=item['title'],
                    content=None,
                    content_short=item.get('intro', None),
                    date=date,
                    source='SinaFinance',  # 增加文章来源字段
                    list_uri=item['url'].split("?")[0],  # 去掉 URL 中的查询参数
                    content_uri=None,
                    status='pending',
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )

                scraped_data.append(article)

            self.logger.info(f"抓取新浪财经完成，总文章数: {len(scraped_data)}")

            return scraped_data
        else:
            return []


class SinaContentScraper(BaseScraper):
    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)
        self.__content_url = self.url
        self.logger = setup_logging("SinaContentScraper", "sina_content_scraper.log")

    def scrape(self):
        try:
            # 获取代理
            proxies = get_random_proxies()
            self.logger.info(f"开始抓取 新浪财经 文章内容，URL: {self.url}, 代理: {str(proxies)}")

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
                response.encoding = 'utf-8'
                content_html = response.text
                if content_html is None:
                    self.logger.error(f"获取内容失败")
                    return None, "failed"
                
                from lxml import html
                html_tree = html.fromstring(content_html)
                content_elements = html_tree.xpath('//*[@id="artibody"]')
                
                # 移除 style 元素及其后的所有兄弟元素
                for element in content_elements:
                    style_element = element.xpath('.//style')
                    if style_element:
                        parent = style_element[0].getparent()
                        for sibling in parent.getchildren()[parent.index(style_element[0]):]:
                            parent.remove(sibling)

                content_text = ""
                if content_elements:
                    content = content_elements[0].text_content()
                    content_text = content.strip() if content else ""
                else:
                    self.logger.error("未找到指定的内容元素")
                    return None, "failed"
                return content_text, "success"
            else:
                self.logger.error(f"获取内容失败: {response.status_code}")
                return None, "failed"
            # return None, "pending"
        except Exception as e:
            self.logger.error(f"从 {self.url} 获取内容时出错: {e}")
            return None, "pending"
        
    def get_connect_url(self):
        return self.url
