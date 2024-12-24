from functools import wraps
import os, json
from sqlalchemy import Engine, QueuePool, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from flask import current_app, g
import logging

from database.db_manager import DatabasePool

Base = declarative_base()
logger = logging.getLogger(__name__)
    
def init_engine(cfg: dict) -> Engine:
    connetc_url = f"mysql+pymysql://{cfg['USER']}:{cfg['PASSWORD']}@{cfg['HOST']}:{cfg['PORT']}/{cfg['DBNAME']}?charset={cfg['CHARSET']}"
    
    engine = create_engine(
        url=connetc_url,
        poolclass=QueuePool,  # 使用队列池
        pool_size=cfg['POOL_SIZE'],         # 池中保持的连接数
        max_overflow=cfg['MAX_OVERFLOW'],   # 超过池大小的最大连接数
        pool_timeout=cfg['POOL_TIMEOUT'],    # 连接池中连接的超时时间
        pool_recycle=cfg['POOL_RECYCLE']     # 连接的回收时间
    )
    return engine

def init_session(engine : Engine):
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return db_session

def init_tables(engine, session):
    from database import Article, Dictionary, Namespace, PromptTemplate
    Base.query = session.query_property()
    Base.metadata.create_all(bind=engine)

def transaction(func):
    """
    事务装饰器
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = DatabasePool.get_session()()
        try:
            result = func(session, *args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"事务执行失败: {e}")
            raise e
        finally:
            session.close()
    return wrapper
        
