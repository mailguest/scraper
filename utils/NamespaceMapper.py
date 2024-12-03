from typing import Dict, List, Optional
import uuid
from utils.log_utils import setup_logging
from config.db import DBConfig
from flask import current_app

class NamespaceMapper:
    def __init__(self, db: Optional[DBConfig]=None, logger=None):
        self.logger = logger if logger is not None else setup_logging("NamespaceMapper", "NamespaceMapper.log") 
        # 获取集合
        self.collection = current_app.config["db"].fetch_table('namespace') if db is None else db.fetch_table('namespace')

       # 判断索引是否存在
        if not self.collection.index_information().get('namespace_1'):
            # 创建索引
            self.collection.create_index([('namespace', 1), ('filename', 1)], unique=True)

    # 插入命名空间
    def insert_namespace(self, namespace: str) -> int:
        try:
            if namespace is None:
                return 0
            result = self.collection.update_one(
                {'namespace': namespace},
                {'$set': {'namespace': namespace}},
                upsert=True
            )
            return result.modified_count
        except Exception as e:
            self.logger.error(f"Error inserting namespace: {str(e)}")
            return 0
        
    def insert_filename(self, namespace: str, filename: str, version: str, **kwargs) -> int:
        try:
            if namespace is None or filename is None or version is None:
                return 0
            session = kwargs.get('session', None)
            result = self.collection.update_one(
                {'namespace': namespace, 'filename': filename},
                {'$set': {'namespace': namespace, 'filename': filename, 'version': version}},
                upsert=True,
                session=session
            )
            return result.modified_count
        except Exception as e:
            self.logger.error(f"Error inserting filename: {str(e)}")
            return 0

    # 获取所有命名空间 和 文件名
    def list_all(self) -> Dict[str, List]:
        """
        return: 返回所有的命名空间 及 其下的文件
        {
            "namespace1": [{"filename":"file1", "version":"version"}, {"filename":"file3", "version":"version"}],
            "namespace2": [{"filename":"file4", "version":"version"}, {"filename":"file2", "version":"version"}],
        }
        """
        rtn = {}
        try:
            result = self.collection.find({})
            
            for item in result:
                namespace = item.get('namespace')
                filename = item.get('filename')
                version = item.get('version')
                if namespace not in rtn:
                    rtn[namespace] = []
                if filename is not None:
                    rtn[namespace].append({'filename':filename, 'version':version})
            return rtn
        except Exception as e:
            self.logger.error(f"Error listing all namespaces: {e}")
            return rtn
        

    # 获取版本号
    def get_version(self, namespace: str, filename: str) -> Optional[str]:
        try:
            result = self.collection.find_one({'namespace': namespace, 'filename': filename})
            return result.get('version') if result else None
        except Exception as e:
            self.logger.error(f"Error listing versions: {e}")
            return None