# base_scraper.py
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self, url, limit=None):
        self.headers = {
            "Accept-Encoding": "gzip",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        self.url = url
        self.limit = limit
    
    @abstractmethod
    def scrape(self):
        pass
