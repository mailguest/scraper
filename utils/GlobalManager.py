from typing import Any, Dict, Optional
from threading import Lock
import logging
from utils.tools.log_utils import setup_logging

class GlobalManager:
    """全局变量管理器"""
    _instance = None
    _lock = Lock()
    _vars: Dict[str, Any] = {}
    _logger: Optional[logging.Logger] = None
    _process_name: Optional[str] = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(GlobalManager, cls).__new__(cls)
            return cls._instance

    @classmethod
    def init(cls, process_name: str):
        """
        初始化全局管理器
        Args:
            process_name: 进程名称
        """
        with cls._lock:
            if not cls._logger:
                cls._process_name = process_name
                cls._logger = setup_logging(f"Global-{process_name}", "global.log")
                cls._logger.info(f"Global manager initialized for process: {process_name}")

    @classmethod
    def set(cls, key: str, value: Any):
        """
        设置全局变量
        Args:
            key: 变量名
            value: 变量值
        """
        if not cls._logger:
            raise RuntimeError("Global manager not initialized")
            
        with cls._lock:
            cls._vars[key] = value
            cls._logger.debug(f"Set global var: {key} = {value}")

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        获取全局变量
        Args:
            key: 变量名
            default: 默认值
        Returns:
            变量值
        """
        if not cls._logger:
            raise RuntimeError("Global manager not initialized")
            
        value = cls._vars.get(key, default)
        cls._logger.debug(f"Get global var: {key} = {value}")
        return value

    @classmethod
    def delete(cls, key: str):
        """
        删除全局变量
        Args:
            key: 变量名
        """
        if not cls._logger:
            raise RuntimeError("Global manager not initialized")
            
        with cls._lock:
            if key in cls._vars:
                del cls._vars[key]
                cls._logger.debug(f"Deleted global var: {key}")

    @classmethod
    def clear(cls):
        """清空所有全局变量"""
        if not cls._logger:
            raise RuntimeError("Global manager not initialized")
            
        with cls._lock:
            cls._vars.clear()
            cls._logger.debug("Cleared all global vars")

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """
        获取所有全局变量
        Returns:
            所有全局变量的字典
        """
        if not cls._logger:
            raise RuntimeError("Global manager not initialized")
            
        return cls._vars.copy()

    @classmethod
    def get_process_name(cls) -> str:
        """
        获取当前进程名称
        Returns:
            进程名称
        """
        if not cls._process_name:
            raise RuntimeError("Global manager not initialized")
        return cls._process_name