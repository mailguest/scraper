import os
from typing import Dict, Any

class Config:
    # 进程配置
    SCHEDULER_STARTUP_DELAY = 60  # 调度器启动延迟时间
    PROCESS_CHECK_INTERVAL = 30   # 进程健康检查间隔
    MAX_RESTART_ATTEMPTS = 3      # 最大重启尝试次数
    CONFIG_CHECK_INTERVAL = 5     # 配置检查间隔

    
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # 执行程序配置
    SCHEDULER_SCRIPT = os.path.join(BASE_DIR, "scripts/scheduler.py")
    API_SCRIPT = os.path.join(BASE_DIR, "apis/api.py")

    # 存储路径
    IP_PROXY_FILE = os.path.join(BASE_DIR, "data/ip_proxies.json")
    
    # 日志配置
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    LOG_LEVEL = "INFO" 

    # 数据库配置
    MONGO_CONFIG = os.path.join(BASE_DIR, "config/mongodb.json")

    # 定时任务配置
    SCHEDULE_CONFIG = os.path.join(BASE_DIR, "config/schedule_config.json")

    # URL配置
    URL_CONFIG = os.path.join(BASE_DIR, "config/urls.json")