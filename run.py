import subprocess
import signal
import time
from typing import Optional
from dataclasses import dataclass
from utils.tools.log_utils import setup_logging
from utils.tools.process_utils import ProcessUtils
from config.config import Config


logger = setup_logging("Run", "run.log")

@dataclass
class ProcessInfo:
    process: subprocess.Popen
    name: str
    is_healthy: bool = True

class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.should_run = True
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()

    def start_process(self, name: str, process_utils: ProcessUtils) -> Optional[ProcessInfo]:
        try:
            process = process_utils.start()
            if process:
                self.processes[name] = ProcessInfo(process=process, name=name)
                return self.processes[name]
        except Exception as e:
            logger.error(f"Error starting {name}: {str(e)}")
        return None

    def shutdown(self):
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

    def _create_api_process(self) -> ProcessUtils:
        """
        web 子进程
        """
        return ProcessUtils(
            process_name="Flask API server",
            root_path=Config.BASE_DIR,
            script_path=Config.API_SCRIPT,
            log_file_name="api.log", 
            logger=logger
        )
    
    def _create_scheduler_process(self) -> ProcessUtils:
        """
        调度器子进程
        """
        return ProcessUtils(
            process_name="Schedule server",
            root_path=Config.BASE_DIR,
            script_path=Config.SCHEDULER_SCRIPT,
            log_file_name="scheduler.log",
            logger=logger
        )


def main():
    process_manager = ProcessManager()
    try:
        # 启动API
        api_process = process_manager.start_process(
            "api", 
            process_manager._create_api_process())
        if not api_process:
            raise RuntimeError("Failed to start API. Exiting.")
        
        # 启动调度器
        scheduler_process = process_manager.start_process(
            "scheduler", 
            process_manager._create_scheduler_process())
        if not scheduler_process:
            raise RuntimeError("Failed to start Scheduler. Exiting.")
        
        # 保持程序运行
        while process_manager.should_run:
            # 检查子进程状态
            if api_process and api_process.process.poll() is not None:
                logger.error("API 进程意外终止")
                break
            if scheduler_process and scheduler_process.process.poll() is not None:
                logger.error("调度器进程意外终止")
                break
            time.sleep(1)
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        process_manager.shutdown()

if __name__ == "__main__":
    from dotenv import load_dotenv
    _ = load_dotenv()

    main()
