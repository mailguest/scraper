import os, json
from sqlalchemy import Engine, QueuePool, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

Base = declarative_base()
    
def init_engine(cfg: dict) -> Engine:

    connetc_url = f"mysql+pymysql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['dbname']}?charset={cfg['charset']}"
    engine = create_engine(
        url=connetc_url,
        poolclass=QueuePool,  # 使用队列池
        pool_size=cfg['pool_size'],         # 池中保持的连接数
        max_overflow=cfg['max_overflow'],   # 超过池大小的最大连接数
        pool_timeout=cfg['pool_timeout'],    # 连接池中连接的超时时间
        pool_recycle=cfg['pool_recycle']     # 连接的回收时间
    )
    return engine

def init_session(engine : Engine):
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    Base.query = db_session.query_property()
    return db_session

def init_tables(engine):
    from database import Article, Dictionary, Namespace, PromptTemplate
    Base.metadata.create_all(bind=engine)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db