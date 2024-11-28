from datetime import datetime
import json
import uuid
import requests
from config.config import Config
from scripts.base_scraper import BaseScraper
from hashlib import sha1
from hashlib import md5

from scripts.scrape_ipproxy import get_random_proxies
from utils.Article import Article
from utils.log_utils import setup_logging

def get_sign(keywords):
    if keywords is None:
        return ""
    # 首先sha1加密
    psw = sha1()
    psw.update(keywords.encode('utf8'))
    s_pwd_sha1 = psw.hexdigest()
    # sha1加密结果再次md5加密
    hash_md5 = md5(s_pwd_sha1.encode('utf8'))
    psw = hash_md5.hexdigest()
    return psw

class ClsScraper(BaseScraper):
    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)
        self.params = kwargs.get("params", None)
        self.sign = get_sign(self.params)
        self.logger = setup_logging("ClsScraper", "cls_scraper.log")

    def scrape(self):
        self.url = self.url.replace("{sign}", str(self.sign))
        # 获取代理
        proxies = get_random_proxies()
        # 记录开始抓取的日志
        self.logger.info(f"开始抓取财联社，URL: {self.url}, 代理: {str(proxies)}")

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
            items = data['data']
            scraped_data: list[Article] = []
            
            if items:
                for item in items:
                    # 提取文章日期，并转换为年月日格式
                    timestamp = int(item['ctime'])  # 使用 'ctime' 字段
                    date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                    
                    article = Article(
                        UUID=uuid.uuid5(uuid.NAMESPACE_DNS, item['title']).hex,
                        title=item['title'],
                        content=None,
                        content_short=item.get('brief', None),
                        date=date,
                        source='Cls',  # 增加文章来源字段
                        list_uri=item.get('id', None),  # 去掉 URL 中的查询参数
                        content_uri=None,
                        status='pending',
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    scraped_data.append(article)

            self.logger.info(f"抓取财联社完成，总文章数: {len(scraped_data)}")

            return scraped_data
        else:
            return []

    def get_connect_url(self):
        return self.url

class ClsContentScraper(BaseScraper):
    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)
        self.__content_url = None

        with open(Config.URL_CONFIG) as file:
            self.__content_url_template = json.load(file)["ClsContent"]["url"]
        self.logger = setup_logging("ClsContentScraper", "cls_scraper.log")

    def scrape(self):
        try:
            self.__set_content_url()
            if self.__content_url is None:
                self.logger.error("生成内容 URL 失败。")
                return None
            # 获取代理
            proxies = get_random_proxies()
            self.logger.info(f"开始抓取 财联社 文章内容，URL: {self.url}, 代理: {str(proxies)}")

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
                content_html = response.text
                if content_html is None:
                    self.logger.error(f"获取内容失败")
                    return None, "failed"
                
                from lxml import html
                html_tree = html.fromstring(content_html)
                content_elements = html_tree.xpath('//*[@id="__next"]/div/div[2]/div[2]/div[1]/div[3]')
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
        
    def __set_content_url(self):
        self.__content_url = self.__content_url_template.replace("{id}", str(self.url))
        
    def get_connect_url(self):
        return self.__content_url