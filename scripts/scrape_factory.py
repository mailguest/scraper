# factory.py
from scripts.wallstreetcn_scraper import WallStreetCNScraper, WallStreetCNContentScraper
from scripts.sinafinance_scraper import SinaFinanceScraper, SinaContentScraper
from scripts.base_scraper import BaseScraper
from utils.log_utils import setup_logging  # 引入日志工具类

# 使用日志工具类设置日志
logger = setup_logging("ScraperFactory", "ScraperFactory.log")

class ScraperFactory:
    scrapers = {
        "WallStreetCN": WallStreetCNScraper,
        "SinaFinance": SinaFinanceScraper
    }

    @classmethod
    def create_scraper(cls, name, url, limit) -> BaseScraper:
        if name in cls.scrapers:
            return cls.scrapers[name](url, limit)
        else:
            raise ValueError(f"Scraper for {name} not found.")

class ContentScraperFactory:
    
    @classmethod
    def create_scraper(cls, source, url) -> BaseScraper:
        if source == "WallStreetCN":
            return WallStreetCNContentScraper(url)
        elif source == "SinaFinance":
            # return SinaContentScraper(url)
            return None
        else:
            logger.error(f"No content scraper available for source: {source}")
            return None