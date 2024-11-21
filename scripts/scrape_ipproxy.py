from dataclasses import dataclass
import requests
import os
import json
from lxml import etree
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
from config.config import Config
from utils.log_utils import setup_logging

# 免费海外代理 ip 页
FREE_IP_URL = 'https://www.iphaiwai.com/free'
# 验证网站
VERIFY_URL = 'https://httpbin.org/ip'

# 使用日志工具类设置日志
logger = setup_logging("scrape_ipproxy", "scrape_ipproxy.log")

@dataclass
class IpProxy:
    ip: str
    port: str
    area: str
    period_of_validity: str
    status: int = 1

class IpProxyMapping():
    def __init__(self, logger):
        self.file_path = Config.IP_PROXY_FILE
        self.logger = logger

    def load_proxies(self) -> list[IpProxy]:
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                return []
            proxy_ip_list = json.loads(content, object_hook=lambda d: IpProxy(**d))
        return proxy_ip_list
    
    def get_proxy_by_ip(self, ip: str, port: str) -> IpProxy:
        proxies = self.load_proxies()
        for proxy in proxies:
            if proxy.ip == ip and proxy.port == port:
                return proxy
        return None
    
    def get_a_proxy(self) -> dict:
        proxies = self.load_proxies()
        if not proxies:
            return None
        proxies = [proxy for proxy in proxies if proxy.status == 1]
        proxy = random.choice(proxies)
        return get_proxies_dict(proxy)
    
    def save_proxies(self, proxies: list[IpProxy]):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([proxy.__dict__ for proxy in proxies], f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"save proxies error: {e}")
            return False

    def add_proxy(self, proxy: IpProxy):
        proxies = self.load_proxies()
        proxies.append(proxy)
        return self.save_proxies(proxies)

    def delete_proxy(self, ip: str):
        proxies = self.load_proxies()
        proxies = [proxy for proxy in proxies if proxy.ip != ip]
        return self.save_proxies(proxies)


    def update_proxy(self, updated_proxy: IpProxy):
        proxies = self.load_proxies()
        for i, proxy in enumerate(proxies):
            if proxy.ip == updated_proxy.ip:
                proxies[i] = updated_proxy
                break
        return self.save_proxies(proxies)

def get_proxies_dict(proxy: IpProxy) -> dict:
    proxies = {
        "http": "http://%(proxy)s/" % {"proxy": proxy.ip + ':' + proxy.port},
        "https": "http://%(proxy)s/" % {"proxy": proxy.ip + ':' + proxy.port}
    }
    return proxies

def test_proxy(proxy_ip_data: IpProxy):
    proxies = get_proxies_dict(proxy_ip_data)
    try:
        # 验证可用性, 国内环境无法访问该网站
        response = requests.get(url=VERIFY_URL, proxies=proxies, timeout=20)
        response.encoding = 'utf-8'
        # <title>WhatsApp Web</title>
        if response.status_code == 200:
            return True
        else:
            proxy_ip_data.status = 0
            return False
    except Exception as e:
        proxy_ip_data.status = 0
        return False

def get_proxies(logger) -> list[IpProxy]:
    return IpProxyMapping(logger).load_proxies()

def get_random_proxies() -> dict:
   return IpProxyMapping(logger).get_a_proxy()

def save(proxy_json):
    IpProxyMapping(logger).save_proxies(proxy_json)

def delete(proxy_ip_data: IpProxy):
    IpProxyMapping(logger).delete_proxy(proxy_ip_data.ip)

def find(ip: str, port: str):
    return IpProxyMapping(logger).get_proxy_by_ip(ip, port)

class OverseasFree:
    def __init__(self, logger):
        self.headers = {
            "Accept-Encoding": "gzip",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        }
        self.effective_ip_list : list[IpProxy] = []
        self.logger = logger
        self.ip_proxy_mapping = IpProxyMapping(logger)

    def verify_ip(self, proxy_ip_data: IpProxy):
        """
        验证 ip 可用性
        :param proxy_ip_data: 获取到的免费海外代理 ip
        """
        if not test_proxy(proxy_ip_data):
            self.logger.error(f"代理 {proxy_ip_data.ip} 不可用")
        else:
            self.logger.info(f"代理 {proxy_ip_data.ip} 可用")
            self.effective_ip_list.append(proxy_ip_data)

    def get_data(self) -> list[IpProxy]:
        """
        获取 ip 相关信息
        """
        try:
            response = requests.get(url=FREE_IP_URL, headers=self.headers, timeout=5)
            html = etree.HTML(response.text)

            ip_list = html.xpath("//td[@class='kdl-table-cell'][1]/text()") # 获取 ip
            port_list = html.xpath("//td[@class='kdl-table-cell'][2]/text()") # 获取端口
            area_list = html.xpath("//td[@class='kdl-table-cell'][5]/text()") # 获取 ip 位置
            period_of_validity_list = html.xpath("//td[@class='kdl-table-cell'][6]/text()") # 获取 ip 有效期

            # 获取到的所有 ip 的相关数据
            proxy_list : list[IpProxy] = [IpProxy(ip, port, area, period) for ip, port, area, period in zip(ip_list, port_list, area_list, period_of_validity_list)]
            
            return proxy_list
        except Exception as e:
            self.logger.error('get ip error: %s' % e)

    def main(self):
        # 获取所有的免费代理 ip
        proxy_data_list = self.get_data()

        if not proxy_data_list:
            self.logger.error('get ip error: no data')
            return

        # 验证 ip 可用性
        for proxy_data in proxy_data_list:
            self.verify_ip(proxy_data)

        self.ip_proxy_mapping.save_proxies(self.effective_ip_list)


def scrape_ipproxies(logger):
    """
    爬取 IP 代理
    """
    OverseasFree(logger=logger).main()

# if __name__ == "__main__":
#     import os
#     import logging
#     LOGS_DIR = os.getenv("LOGS_DIR", "./logs")
#     # 将日志级别从字符串转换为 logging 模块的级别
#     level = logging.INFO
#     logger = logging.getLogger("logger_name")
#     logger.setLevel(level)
#     formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#     console_handler = logging.StreamHandler()
#     console_handler.setFormatter(formatter)
#     console_handler.setLevel(level)
#     logger.addHandler(console_handler)
#     scrape_ipproxies(logger)  # 运行爬虫