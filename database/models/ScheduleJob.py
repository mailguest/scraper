from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from database.db import Base

class ScheduleJob(Base):
    __tablename__ = 'schedule_job'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    cron = Column(String(50), nullable=False)
    function = Column(String(50), nullable=False)
    enabled = Column(Boolean, nullable=False)
    params = Column(Text, nullable=False)
    description = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<ScheduleJob {self.name}>"