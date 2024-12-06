from pymongo import MongoClient
import json
import os

class DBConfig:
    def __init__(self):
        if not hasattr(self, 'pool'):
            # 读取配置文件
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'mongodb.json')
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            # 根据环境变量判断使用哪个 host
            host = self.config['docker_host'] if os.getenv('DOCKER_ENV') else self.config['host']
            self.pool = MongoClient(host=host, port=self.config['port'], maxpoolsize=10)
    
    def get(self, name):
        return self.pool[self.config['database']][name]
    
db_connect = DBConfig()