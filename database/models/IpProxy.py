from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from database.db import Base

class IpProxy(Base):
    __tablename__ = 'ip_proxy'
    id = Column(Integer, primary_key=True)
    ip = Column(String(20), nullable=False)
    port = Column(String(10), nullable=False)
    area = Column(String(50), nullable=False)
    period_of_validity = Column(String(20), nullable=False)
    status = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)