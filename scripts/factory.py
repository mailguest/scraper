# factory.py
from scripts.wallstreetcn_scraper import WallStreetCNScraper, WallStreetCNContentScraper
from scripts.sina_finance_scraper import SinaFinanceScraper, SinaContentScraper
from utils.log_utils import setup_logging  # 引入日志工具类

# 使用日志工具类设置日志
logger = setup_logging("ScraperFactory", "ScraperFactory.log")

class ScraperFactory:
    scrapers = {
        "WallStreetCN": WallStreetCNScraper,
        "SinaFinance": SinaFinanceScraper
    }

    @classmethod
    def create_scraper(cls, name, url, limit):
        if name in cls.scrapers:
            return cls.scrapers[name](url, limit)
        else:
            raise ValueError(f"Scraper for {name} not found.")

class ContentScraperFactory:
    
    @classmethod
    def create_scraper(cls, source, url):
        if source == "WallStreetCN":
            return WallStreetCNContentScraper(url)
        elif source == "SinaFinance":
            # return SinaContentScraper(url)
            return None
        else:
            logger.error(f"No content scraper available for source: {source}")
            return None