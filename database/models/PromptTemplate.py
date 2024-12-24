from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from database.db import Base

class PromptTemplate(Base):
    __tablename__ = 'prompt_template'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False, default=datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    namespace = Column(String(50), nullable=False, default="default")
    prompt_content = Column(Text, nullable=False)
    user_input = Column(Text, nullable=False)
    model = Column(String(50), nullable=False)
    model_version = Column(String(50), nullable=False)
    temperature = Column(Float, nullable=False, default=1.0)
    max_tokens = Column(Integer, nullable=False, default=4096)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)