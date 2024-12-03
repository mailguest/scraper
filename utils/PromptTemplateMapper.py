from typing import Dict, List, Optional
import uuid
from utils.log_utils import setup_logging
from config.db import DBConfig
from flask import current_app
from utils.PromptTemplate import PromptTemplate

class PromptTemplateMapper:
    def __init__(self, db: Optional[DBConfig]=None, logger=None):
        self.logger = logger if logger is not None else setup_logging("PromptTemplateMapper", "PromptTemplateMapper.log") 
        # 获取集合
        self.collection = current_app.config["db"].fetch_table('prompt') if db is None else db.fetch_table('prompt')

        # 判断索引是否存在
        if not self.collection.index_information().get('prompt_nnv_index'):
            # 创建索引
            self.collection.create_index([('namespace', 1), ('name', 1), ('version', -1)], unique=True, name='prompt_nnv_index')


    # 插入提示词模版
    def insert_prompt_template(self, prompt_template: PromptTemplate, **kwargs) -> int:
        try:
            session = kwargs.get("session", None)
            result = self.collection.update_one(
                {'namespace': prompt_template.namespace, 'name': prompt_template.name, 'version': prompt_template.version},
                {'$set': prompt_template.to_dict()},
                upsert=True,
                session=session
            )
            return result.modified_count
        except Exception as e:
            self.logger.error(f"Error inserting prompt_template: {str(e)}")
            return 0
        
    # 获取提示词模版
    def get_prompt_by_namespace_name_version(self, namespace: str, name: str, version: str) -> Optional[PromptTemplate]:
        try:
            rtn = self.collection.find_one({'namespace': namespace, 'name': name, 'version': version})
            return PromptTemplate.from_dict(rtn) if rtn else None
        except Exception as e:
            self.logger.error(f"Error finding prompt_template: {e}")
            return None
        
    # 获取文件的所有版本信息
    def get_versions(self, namespace: str, name: str) -> List[str]:
        try:
            rtn = self.collection.find({'namespace': namespace, 'name': name})
            return [item['version'] for item in rtn]
        except Exception as e:
            self.logger.error(f"Error listing versions: {e}")
            return []