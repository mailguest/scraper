from database.db import transaction
from database.models.Article import Article
from datetime import datetime

class ArticleService:
    
    @transaction
    def create_article(self, session, title: str, content: str) -> Article:
        """创建文章"""
        article = Article(
            title=title,
            content=content
        )
        session.add(article)
        return article

    @transaction
    def get_article_by_id(self, session, article_id: int) -> Article:
        """查询单篇文章"""
        return session.query(Article).filter(Article.id == article_id).first()

    @transaction
    def get_all_articles(self, session) -> list[Article]:
        """查询所有文章"""
        return session.query(Article).all()

    @transaction
    def update_article(self, session, article_id: int, title: str = None, content: str = None) -> Article:
        """更新文章"""
        article = session.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise ValueError(f"文章ID {article_id} 不存在")
            
        if title:
            article.title = title
        if content:
            article.content = content
            
        return article

    @transaction
    def delete_article(self, session, article_id: int) -> bool:
        """删除文章"""
        article = session.query(Article).filter(Article.id == article_id).first()
        if article:
            session.delete(article)
            return True
        return False 