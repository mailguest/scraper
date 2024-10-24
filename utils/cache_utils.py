import threading
import time
from typing import List, Optional
from utils.search_utils import SearchUtils

# 全局缓存变量
_cache: Optional[List[dict]] = None

def get_cache() -> Optional[List[dict]]:
    """返回当前的缓存数据"""
    global _cache
    return _cache

def set_cache(data: List[dict]) -> None:
    """设置缓存数据"""
    global _cache
    _cache = data

def update_cache(logger, search_utils_instance: SearchUtils) -> Optional[List[dict]]:
    """
    更新缓存中的数据。
    :param logger: 日志记录器
    :param search_utils_instance: SearchUtils 实例，用于加载新的数据
    :return: 返回更新后的缓存数据或 None
    """
    try:
        logger.info("Updating cache...")
        data = search_utils_instance.load_all_data()  # 重新加载所有数据
        set_cache(data)  # 更新缓存
        logger.info(f"Cache updated with {len(data)} records.")
    except Exception as e:
        logger.error(f"Failed to update cache: {e}")
        return None
    return _cache

def get_search(logger) -> Optional[SearchUtils]:
    """
    返回一个包含缓存数据的 SearchUtils 实例。如果缓存为空则加载所有数据到缓存。
    :param logger: 日志记录器
    :return: 返回 SearchUtils 实例，或 None 如果加载数据失败
    """
    try:
        data = get_cache()  # 获取缓存中的数据
        if data is None:
            logger.info("Cache is empty, loading data...")
            search_utils = SearchUtils(logger)
            data = update_cache(logger, search_utils)  # 更新并设置缓存
            if data is None:
                logger.error("Failed to load and cache data.")
                return None
        return SearchUtils(logger, data)
    except Exception as e:
        logger.error(f"Error in factory: {e}")
        return None

def update_worker(logger, interval: int = 600) -> None:
    """
    每隔指定的时间间隔更新一次缓存。
    :param logger: 日志记录器
    :param interval: 更新缓存的时间间隔（秒），默认为600秒（10分钟）。
    """
    search_utils = SearchUtils(logger)
    while True:
        logger.info("Cache update worker is running...")
        update_cache(logger, search_utils)  # 更新缓存
        logger.info(f"Next cache update in {interval} seconds.")
        time.sleep(interval)  # 等待一段时间后再更新

def start_worker(logger, interval: int = 600) -> None:
    """
    启动子线程，定期更新缓存。 \n
    :param logger: 日志记录器 \n
    :param interval: 更新缓存的时间间隔（秒），默认为600秒（10分钟）。
    """
    try:
        thread = threading.Thread(target=update_worker, args=(logger, interval), daemon=True)
        thread.start()
        logger.info("Cache update thread started successfully.")
    except Exception as e:
        logger.error(f"Failed to start cache update thread: {e}")
