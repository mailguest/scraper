import logging
from typing import Optional
from sqlalchemy import Engine
from sqlalchemy.orm import scoped_session
from multiprocessing import Lock
import threading

from utils.GlobalManager import GlobalManager
from utils.tools.log_utils import setup_logging

class DatabasePool:
    """数据库连接池管理类"""
    def __init__(self) -> None:
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[scoped_session] = None
        self._process_lock = Lock()
        self._thread_lock = threading.Lock()
        self._initialized = False

    def init_db(self, config: dict) -> bool:
        """
        初始化数据库连接
        使用进程锁确保多进程环境下只初始化一次
        """
        with self._process_lock:
            if not self._initialized:
                try:
                    process_name = GlobalManager.get_process_name()
                    logger = setup_logging(f"DB-{process_name}", "database.log")
                    
                    from database.db import init_engine, init_session, init_tables
                    self._engine = init_engine(config)
                    self._session_factory = init_session(self._engine)
                    init_tables(self._engine, self._session_factory)

                    self._initialized = True
                    logger.info(f"Database initialized for process: {process_name}")
                    return True
                except Exception as e:
                    logger.error(f"Database initialization failed: {str(e)}")
                    raise e
        return False
    
    def get_engine(self) -> Engine:
        """获取数据库引擎"""
        if not self._initialized:
            raise RuntimeError("Database pool not initialized")
        return self._engine

    def get_session(self) -> scoped_session:
        """获取会话工厂"""
        if not self._initialized:
            raise RuntimeError("Database pool not initialized")
        return self._session_factory

    def close(self):
        """关闭连接池"""
        with self._process_lock:
            if self._initialized:
                if self._session_factory:
                    self._session_factory.remove()
                if self._engine:
                    self._engine.dispose()
                self._initialized = False