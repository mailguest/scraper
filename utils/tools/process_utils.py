import subprocess
import os
import threading
from utils.tools.log_utils import log_subprocess_output

class ProcessUtils():
    def __init__(self, process_name, root_path, script_path, log_file_name, logger):
        """
        初始化通用子进程工具类。
        process_name: 子进程的名称（用于日志）
        root_path: 主进程项目根目录的路径
        script_path: 子进程脚本的路径
        log_file_name: 子进程的日志文件的名称
        logger: 主进程的日志记录器
        """
        self.process_name = process_name
        self.root_path = root_path
        self.script_path = script_path
        self.log_file_name = log_file_name
        self.logger = logger

    def start(self):
        """
        启动通用子进程并处理其输出到日志和控制台。

        :param process_name: 进程的名称（用于日志）
        :param script_path: 进程脚本的路径
        :param log_file_name: 日志文件的名称
        :return: 启动的子进程对象
        """
        self.logger.info(f"Starting the {self.process_name}...")
        
        log_path = os.path.join(os.getenv("LOGS_DIR", "./logs"), self.log_file_name)
        
        env = os.environ.copy()
        env["PYTHONPATH"] = self.root_path

        process = subprocess.Popen(
            ["python", self.script_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True, encoding='utf-8'
        )

        # 使用线程捕获子进程输出
        threading.Thread(target=log_subprocess_output, args=(process.stdout, log_path, self.logger), daemon=True).start()
        threading.Thread(target=log_subprocess_output, args=(process.stderr, log_path, self.logger), daemon=True).start()

        self.logger.info(f"{self.process_name} started with PID: {process.pid}")
        return process
