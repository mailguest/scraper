# factory.py
from scripts.wallstreetcn_scraper import WallStreetCNScraper, WallStreetCNContentScraper
from scripts.sinafinance_scraper import SinaFinanceScraper, SinaContentScraper
from scripts.base_scraper import BaseScraper
from tests.test_scraper import scraper
from utils.log_utils import setup_logging  # 引入日志工具类
from typing import Optional

# 使用日志工具类设置日志
logger = setup_logging("ScraperFactory", "ScraperFactory.log")

class BaseFactory:
    opts = {}

    @classmethod
    def create_scraper(cls, source, url, **kwargs) -> BaseScraper:
        scraper = cls.opts.get(source, None)
        if scraper:
            return scraper(url, **kwargs)  # 传递 **kwargs
        raise ValueError(f"Scraper for {source} not found.")

class ScraperFactory(BaseFactory):
    opts = {
        "WallStreetCN": WallStreetCNScraper,
        "SinaFinance": SinaFinanceScraper,
        "Cls": None #ClsScraper
    }

class ContentScraperFactory(BaseFactory):
    opts = {
        "WallStreetCN": WallStreetCNContentScraper,
        "SinaFinance": None, #SinaContentScraper,
        "Cls": None #ClsContentScraper
    }