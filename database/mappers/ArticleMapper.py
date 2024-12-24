from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import current_app
from utils.tools import setup_logging
from models import Article

class ArticleMapper:
    def __init__(self, engine=None, session=None, logger=None):
        self.logger = logger if logger is not None else setup_logging("ArticleMapper", "ArticleMapper.log") 
        # 获取集合
        self.collection = current_app.config["db"].get("articles") if db is None else db.get("articles")

        # 判断索引是否存在
        if not self.collection.index_information().get('UUID_1'):
            # 创建索引
            self.collection.create_index('UUID', unique=True)
            self.collection.create_index('date')
            self.collection.create_index('source')
            self.collection.create_index('list_uri')

    def insert_article(self, article: Article) -> int:
        """
        插入单篇文章
        """
        try:
            article_dict = article.to_dict()
            article_dict['created_at'] = datetime.now()
            
            result = self.collection.update_one(
                {'UUID': article_dict['UUID']},
                {'$set': article_dict},
                upsert=True
            )
            return result.modified_count
        except Exception as e:
            self.logger.error(f"Error inserting article: {str(e)}")
            return 0
        
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
            articles = [article for article in map(Article.from_dict, articles_dict) if article is not None]
            return articles
        except Exception as e:
            self.logger.error(f"Error getting articles by status: {str(e)}")
            return []
        
    def get_count_articles(self, date_str: Optional[str] = None) -> int:
        """
        获取文章总数
        """
        try:
            query = {}
            if date_str:
                # 将日期字符串转换为日期对象
                target_date = datetime.strptime(date_str, '%Y-%m-%d')
                next_date = target_date + timedelta(days=1)
                
                # 使用日期范围查询
                query = {
                    'date': {
                        '$gte': target_date.strftime('%Y-%m-%d'),
                        '$lt': next_date.strftime('%Y-%m-%d')
                    }
                }
            return self.collection.count_documents(query)
        except Exception as e:
            self.logger.error(f"Error getting count of articles: {str(e)}")
            return 0
        
    def get_all_articles(self) -> List[Article]:
        """
        获取所有文章
        """
        try:
            articles_dict = self.collection.find().sort('date', -1)
            articles = [article for article in map(Article.from_dict, articles_dict) if article is not None]
            return articles
        except Exception as e:
            self.logger.error(f"Error getting all articles: {str(e)}")
            return []

    def get_articles_by_article(self, article: Optional[dict], page: int = 1, per_page: int = 10) -> Dict:
        """
        获取文章列表，支持分页和过滤
        """
        if article is None:
            self.logger.error(f"参数错误: article 不能为空")
            return {'total': 0, 'items': [], 'page': page, 'per_page': per_page, 'total_pages': 0}

        # 定义需要检查的字段映射
        field_mappings = {
            'UUID': article.get('UUID'),
            'title': article.get('title'),
            'list_uri': article.get('list_uri'),
            'content_uri': article.get('content_uri'),
            'source': article.get('source'),
            'status': article.get('status')
        }
        
        # 构建查询字典
        query = {
            field: value 
            for field, value in field_mappings.items() 
            if value is not None
        }

        if article.get('date'):
            date_str = article.get('date')
            if isinstance(date_str, str):  # 确保是字符串类型
                target_date = datetime.strptime(date_str, '%Y-%m-%d')
                next_date = target_date + timedelta(days=1)
                query['date'] = {
                    '$gte': target_date.strftime('%Y-%m-%d'),
                    '$lt': next_date.strftime('%Y-%m-%d')
                }
        
        return self.get_articles(page, per_page, query)
        
    def get_articles(self, page: int = 1, per_page: int = 10, filter: dict = {}) -> Dict:
        """
        获取文章列表，支持分页和过滤
        """
        try:
            total = self.collection.count_documents(filter)
            
            articles_cursor = self.collection.find(filter)\
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

    def update_article(self, article: Article) -> int:
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
            return result.modified_count
        except Exception as e:
            self.logger.error(f"Error updating article: {str(e)}")
            return 0

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
            articles = [article for article in map(Article.from_dict, articles_dict) if article is not None]
            return articles
        except Exception as e:
            self.logger.error(f"Error getting articles by date range: {str(e)}")
            return []

    def get_articles_by_source(self, source: str) -> List[Article]:
        """
        按来源获取文章
        """
        try:
            articles_dict = self.collection.find({'source': source}).sort('date', -1)
            articles = [article for article in map(Article.from_dict, articles_dict) if article is not None]
            return articles
        except Exception as e:
            self.logger.error(f"Error getting articles by source: {str(e)}")
            return []