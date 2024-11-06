import requests
import json
from lxml import etree
from concurrent.futures import ThreadPoolExecutor, as_completed

# 免费海外代理 ip 页
FREE_IP_URL = 'https://www.iphaiwai.com/free'
# 验证网站
VERIFY_URL = 'https://httpbin.org/ip'

class IpProxy:
    def __init__(self, ip, port, area, period_of_validity):
        self.ip = ip + ':' + port
        self.area = area
        self.period_of_validity = period_of_validity

proxy_ip_list : list[IpProxy] = []

def get_random_proxies() -> dict:
    """
    随机获取一个代理 ip
    """
    if proxy_ip_list is None or len(proxy_ip_list) == 0:
        return None
    import random
    proxy = random.choice(proxy_ip_list)
    return OverseasFree.get_proxies(proxy.ip)

class OverseasFree:
    def __init__(self, logger):
        self.headers = {
            "Accept-Encoding": "gzip",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        }
        self.effective_ip_list : list[IpProxy] = []
        self.logger = logger

    @staticmethod
    def get_proxies(proxy: str) -> dict:
        proxies = {
            "http": "http://%(proxy)s/" % {"proxy": proxy},
            "https": "http://%(proxy)s/" % {"proxy": proxy}
        }
        return proxies

    def verify_ip(self, proxy_ip_data: IpProxy):
        """
        验证 ip 可用性
        :param proxy_ip_data: 获取到的免费海外代理 ip
        """
        # 获取代理 ip
        proxy = proxy_ip_data.ip
        proxies = self.get_proxies(proxy)

        try:
            # 验证可用性, 国内环境无法访问该网站
            response = requests.get(url=VERIFY_URL, proxies=proxies, timeout=20)
            response.encoding = 'utf-8'
            # <title>WhatsApp Web</title>
            if response.status_code == 200:
                self.logger.info(f"代理 {proxy} 可用，返回IP: {response.json()['origin']}")
                self.effective_ip_list.append(proxy_ip_data)
            else:
                self.logger.error(f"代理 {proxy} 不可用，状态码: {response.status_code}")
        except Exception as e:
            self.logger.error(f"代理 {proxy} 测试失败: {e}")

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

        # 验证 ip 可用性
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = [executor.submit(self.verify_ip, proxy) for proxy in proxy_data_list]
        verify_result = [future.result() for future in as_completed(futures)]
        if verify_result:
            # 处理返回的数据
            pass

        # 打印所有的有效 ip
        self.logger.info(json.dumps([proxy.__dict__ for proxy in self.effective_ip_list], ensure_ascii=False, indent=4))
        self.logger.info('Get IP Number: %d' % len(self.effective_ip_list))
        global effective_ip_list
        effective_ip_list = self.effective_ip_list


def scrape_ipproxies(logger):
    """
    爬取 IP 代理
    """
    OverseasFree(logger=logger).main()

if __name__ == "__main__":
    import os
    import logging
    LOGS_DIR = os.getenv("LOGS_DIR", "./logs")
    # 将日志级别从字符串转换为 logging 模块的级别
    level = logging.INFO
    logger = logging.getLogger("logger_name")
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)
    scrape_ipproxies(logger)  # 运行爬虫