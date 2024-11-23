from pymongo import MongoClient
import json
import os

class DBConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'client'):
            # 读取配置文件
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'mongodb.json')
            with open(config_path, 'r') as f:
                config = json.load(f)

            # 根据环境变量判断使用哪个 host
            host = config['docker_host'] if os.getenv('DOCKER_ENV') else config['host']
            
            self.client = MongoClient(host=host, port=config['port'], maxpoolsize=10)
            self.db = self.client[config['database']]

    def get_collection(self, table_name: str):
        return self.db[table_name]
    
    def __del__(self):
        if hasattr(self, 'client'):
            self.client.close()
