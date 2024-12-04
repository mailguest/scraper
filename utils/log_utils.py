import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logging(logger_name, log_file):
    """
    设置统一的日志配置，日志文件按日期切割，支持通过环境变量配置日志级别。
    
    :param logger_name: 日志记录器的名称
    :param log_file: 日志文件名
    :return: 配置好的 logger 实例
    """
    # 获取日志目录环境变量和日志级别环境变量
    LOGS_DIR = os.getenv("LOGS_DIR", "./logs")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    # 创建日志目录（如果不存在）
    os.makedirs(LOGS_DIR, exist_ok=True)

    # 将日志级别从字符串转换为 logging 模块的级别
    level = getattr(logging, LOG_LEVEL, logging.INFO)

    # 配置日志记录器
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # 设置日志文件路径
    log_path = os.path.join(LOGS_DIR, log_file)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')

    # 使用 TimedRotatingFileHandler，每天切割一次日志，保留 30 天的日志
    file_handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1, backupCount=30)
    file_handler.suffix = "%Y-%m-%d"  # 文件后缀为日期，防止覆盖
    file_handler.setFormatter(formatter)

    # 控制台处理器，将日志输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 添加文件和控制台处理器（避免重复添加）
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

def log_subprocess_output(pipe, log_file, logger):
    """
    实时捕获子进程的输出并写入日志文件和控制台。
    """
    with open(log_file, "a", encoding="utf-8") as f:
        for line in iter(pipe.readline, ''):
            logger.info(line.strip())  # 输出到控制台
            f.write(line)  # 写入日志文件
        f.flush()
