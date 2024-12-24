from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from database.db import Base

class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer, primary_key=True)
    title_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    content_short = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    source = Column(String(50), nullable=False)
    url = Column(String(200), nullable=False)
    status = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
