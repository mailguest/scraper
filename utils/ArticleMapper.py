from pymongo import MongoClient
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
from .Article import Article
from utils.log_utils import setup_logging

class ArticleMapper:
    def __init__(self, logger=None):
        self.logger = logger if logger is not None else setup_logging("ArticleMapper", "ArticleMapper.log") 

        # 读取配置文件
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'mongodb.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # 建立MongoDB连接
        self.client = MongoClient(host=config['host'], port=config['port'])
        self.db = self.client[config['database']]
        self.collection = self.db[config['collections']['articles']]
        
        # 创建索引
        self.collection.create_index('UUID', unique=True)
        self.collection.create_index('date')
        self.collection.create_index('source')
        self.collection.create_index('list_uri')

    def insert_article(self, article: Article) -> bool:
        """
        插入单篇文章
        """
        try:
            article_dict = article.to_dict()
            article_dict['created_at'] = datetime.now()
            
            self.collection.update_one(
                {'UUID': article_dict['UUID']},
                {'$set': article_dict},
                upsert=True
            )
            return True
        except Exception as e:
            self.logger.error(f"Error inserting article: {str(e)}")
            return False
        
    def insert_articles(self, articles: List[Article]) -> bool:
        """
        插入多篇文章
        """
        try:
            # 将 Article 对象转换为字典列表
            articles_dict = []
            for article in articles:
                article_dict = article.to_dict()
                articles_dict.append(article_dict)

            self.collection.insert_many(articles_dict)
            return True
        except Exception as e:
            self.logger.error(f"Error inserting articles: {str(e)}")
            return False

    def get_article_by_uuid(self, uuid: str) -> Optional[Article]:
        """
        通过UUID获取单篇文章
        """
        try:
            article_dict = self.collection.find_one({'UUID': uuid})
            if not article_dict:
                return None
            return Article.from_dict(article_dict)
        except Exception as e:
            self.logger.error(f"Error getting article: {str(e)}")
            return None
        
    def get_article_by_list_uri(self, list_uri: str) -> Optional[Article]:
        """
        通过 list_uri 获取单篇文章
        """
        try:
            article_dict = self.collection.find_one({'list_uri': list_uri})
            self.logger.debug(f"Found article by list_uri: {article_dict}")
            return Article.from_dict(article_dict)
        except Exception as e:
            self.logger.error(f"Error getting article by list_uri: {str(e)}")
            return None
        
    def get_articles_by_status(self, status: str = 'pending') -> List[Article]:
        """
        按状态获取文章, 默认获取状态为 pending 的文章
        """
        try:
            articles_dict = self.collection.find({'status': status}).sort('date', -1)
            return [Article.from_dict(article) for article in articles_dict]
        except Exception as e:
            self.logger.error(f"Error getting articles by status: {str(e)}")
            return []
        
    def get_count_articles(self, filters: Dict = None) -> int:
        """
        获取文章总数
        """
        try:
            return self.collection.count_documents(filters if filters else {})
        except Exception as e:
            self.logger.error(f"Error getting count of articles: {str(e)}")
            return 0
        
    def get_all_articles(self) -> List[Article]:
        """
        获取所有文章
        """
        return self.collection.find().sort('date', -1)

    def get_articles(self, page: int = 1, per_page: int = 10, filters: Dict = None) -> Dict:
        """
        获取文章列表，支持分页和过滤
        """
        try:
            query = filters if filters else {}
            total = self.collection.count_documents(query)
            
            articles_cursor = self.collection.find(query)\
                .sort('date', -1)\
                .skip((page - 1) * per_page)\
                .limit(per_page)
            
            articles = []
            for article_dict in articles_cursor:
                article = Article.from_dict(article_dict)
                if article:
                    articles.append(article)
            
            return {
                'total': total,
                'items': articles,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        except Exception as e:
            self.logger.error(f"Error listing articles: {str(e)}")
            return {'total': 0, 'items': [], 'page': page, 'per_page': per_page, 'total_pages': 0}

    def update_article(self, article: Article) -> bool:
        """
        更新文章
        """
        try:
            article_dict = article.to_dict()
            article_dict['updated_at'] = datetime.now()
            
            result = self.collection.update_one(
                {'UUID': article.UUID},
                {'$set': article_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error updating article: {str(e)}")
            return False

    def delete_article(self, uuid: str) -> bool:
        """
        删除文章
        """
        try:
            result = self.collection.delete_one({'UUID': uuid})
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Error deleting article: {str(e)}")
            return False

    def get_articles_by_date_range(self, start_date: str, end_date: str) -> List[Article]:
        """
        按日期范围获取文章
        """
        try:
            query = {
                'date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            articles_dict = self.collection.find(query).sort('date', -1)
            return [Article.from_dict(article) for article in articles_dict]
        except Exception as e:
            self.logger.error(f"Error getting articles by date range: {str(e)}")
            return []

    def get_articles_by_source(self, source: str) -> List[Article]:
        """
        按来源获取文章
        """
        try:
            articles_dict = self.collection.find({'source': source}).sort('date', -1)
            return [Article.from_dict(article) for article in articles_dict]
        except Exception as e:
            self.logger.error(f"Error getting articles by source: {str(e)}")
            return []
        
    def close(self):
        self.__del__()

    def __del__(self):
        """
        确保关闭数据库连接
        """
        if hasattr(self, 'client'):
            self.client.close() 