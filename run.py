import subprocess
import os
import time
import threading
from utils.log_utils import setup_logging  # 更新引用路径
from utils.process_utils import ProcessUtils  # 更新引用路径

# 使用日志工具类设置日志
logger = setup_logging("Run", "run.log")

def start_scheduler():
    sub_process = ProcessUtils(
        process_name="scraper scheduler", 
        root_path=os.path.abspath("."), 
        script_path=os.path.abspath("scripts/scheduler.py"), 
        log_file_name="scheduler.log", 
        logger=logger)
    return sub_process.start()

def start_api():
    sub_process = ProcessUtils(
        process_name="Flask API server", 
        root_path=os.path.abspath("."), 
        script_path=os.path.abspath("apis/api.py"), 
        log_file_name="api.log", 
        logger=logger)
    return sub_process.start()

def main():
    logger.info("Starting the entire scraper application...")

    try:
        # 启动调度器
        scheduler_process = start_scheduler()

        # 等待调度器启动后启动 API
        time.sleep(5)
        
        # 启动 API 服务
        api_process = start_api()

        scheduler_process.wait()
        api_process.wait()

    except KeyboardInterrupt:
        logger.info("Shutting down all processes...")
        scheduler_process.terminate()
        api_process.terminate()

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
