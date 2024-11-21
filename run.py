import subprocess
import os
import signal
from typing import Optional
from dataclasses import dataclass
from config.config import Config
from utils.log_utils import setup_logging
from utils.process_utils import ProcessUtils

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
                logger.info(f"Started {name} with PID {process.pid} successfully.")
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
        return ProcessUtils(
            process_name="Flask API server",
            root_path=Config.BASE_DIR,
            script_path=Config.API_SCRIPT,
            log_file_name="api.log", 
            logger=logger)

def main():
    logger.info("Starting the API server...")
    process_manager = ProcessManager()
    try:
        # 启动API
        api_process = process_manager.start_process(
            "api", 
            process_manager._create_api_process())
        if not api_process:
            raise RuntimeError("Failed to start API. Exiting.")
        
        # 保持程序运行
        while process_manager.should_run:
            import time
            time.sleep(1)
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        process_manager.shutdown()

if __name__ == "__main__":
    main()
