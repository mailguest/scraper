# base_scraper.py
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self, url, limit=None):
        self.url = url
        self.limit = limit
    
    @abstractmethod
    def scrape(self):
        pass
