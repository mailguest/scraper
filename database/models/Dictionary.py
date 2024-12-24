
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from database.db import Base

class Dictionary(Base):
    __tablename__ = 'dictionary'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    namespace = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Dictionary {self.name}>"