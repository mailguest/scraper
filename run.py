import subprocess
import os
import time
import threading
import signal
from typing import Optional, Dict
from dataclasses import dataclass
from config.config import Config
from utils.log_utils import setup_logging  # 更新引用路径
from utils.process_utils import ProcessUtils  # 更新引用路径

# 使用日志工具类设置日志
logger = setup_logging("Run", "run.log")

@dataclass
class ProcessInfo:
    process: subprocess.Popen
    name: str
    restart_count: int = 0
    is_healthy: bool = True

class ProcessManager:
    def __init__(self):
        self.processes: Dict[str, ProcessInfo] = {}
        self.should_run: bool = True
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """设置信号处理器"""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """信号进程信号"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()

    def start_process(self, name: str, process_utils: ProcessUtils) -> Optional[ProcessInfo]:
        """启动并管理进程"""
        try:
            process = process_utils.start()
            if process:
                self.processes[name] = ProcessInfo(process=process, name=name)
                logger.info(f"Started {name} with PID {process.pid} successfully.")
                return self.processes[name]
        except Exception as e:
            logger.error(f"Error starting {name}: {str(e)}")
        return None
    
    def monitor_process(self):
        """监控进程状态"""
        while self.should_run:
            for name, info in self.processes.items():
                if not self._is_process_running(info.process):
                    logger.error(f"{name} is not running. Restarting...")
                    if info.restart_count < Config.MAX_RESTART_ATTEMPTS:
                        self._restart_process(name)
                    else:
                        logger.error(f"{name} has been restarted {Config.MAX_RESTART_ATTEMPTS} times. Shutting down...")
            time.sleep(Config.PROCESS_CHECK_INTERVAL)

    def _is_process_running(self, process: subprocess.Popen) -> bool:
        """
        检查进程是否正在运行
        运行中：True
        未运行：False
        """
        try:
            # 正常：返回None；异常：返回退出码，比如0（正常退出）或其他值（异常退出）；
            return process.poll() is None
        except Exception as e:
            logger.error(f"Error checking process status: {str(e)}")
            return False
        
    def _restart_process(self, name: str):
        """重启进程"""
        info = self.processes[name]
        info.restart_count += 1
        logger.info(f"Restarting {name} ({info.restart_count} restarts).")

        if name == "scheduler":
            process_utils = self._create_scheduler_process()
        elif name == "api":
            process_utils = self._create_api_process()
        else:
            logger.error(f"Unknown process name: {name}")
            return

        new_process = process_utils.start()
        if new_process:
            info.process = new_process
            logger.info(f"Restarted {name} with PID {new_process.pid} successfully.")

    def shutdown(self):
        """优雅关闭所有进程"""
        logger.info("Shutting down all processes...")
        self.should_run = False
        for name, info in self.processes.items():
            try:
                logger.info(f"Shutting down {name}...")
                if info.process.poll() is None:
                    info.process.terminate()
                    info.process.wait(timeout=5)
            except Exception as e:
                logger.error(f"Error terminating {name}: {str(e)}")
                info.process.kill()

    def _create_scheduler_process(self) -> ProcessUtils:
        return ProcessUtils(
            process_name="scraper scheduler",
            root_path=Config.BASE_DIR,
            script_path=Config.SCHEDULER_SCRIPT,
            log_file_name="scheduler.log", 
            logger=logger)
    
    def _create_api_process(self) -> ProcessUtils:
        return ProcessUtils(
            process_name="Flask API server",
            root_path=Config.BASE_DIR,
            script_path=Config.API_SCRIPT,
            log_file_name="api.log", 
            logger=logger)
    
def main():
    logger.info("Starting the entire scraper application...")
    process_manager = ProcessManager()
    try:
        # 启动调度器
        scheduler_process = process_manager.start_process(
            "scheduler", 
            process_manager._create_scheduler_process())
        if not scheduler_process:
            raise RuntimeError("Failed to start scheduler. Exiting.")
    
        # 等待调度器启动
        logger.info(f"Waiting {Config.SCHEDULER_STARTUP_DELAY}s for scheduler to start...")
        time.sleep(Config.SCHEDULER_STARTUP_DELAY)

        # 启动API
        api_process = process_manager.start_process(
            "api", 
            process_manager._create_api_process())
        if not api_process:
            raise RuntimeError("Failed to start API. Exiting.")
        
        # 启动监控
        monitor_thread = threading.Thread(
            target=process_manager.monitor_process, 
            daemon=True)
        monitor_thread.start()

        # 等待监控线程结束
        while process_manager.should_run:
            time.sleep(1)
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        process_manager.shutdown()

if __name__ == "__main__":
    main()
