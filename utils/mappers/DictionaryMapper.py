from typing import Dict, List, Optional
from config.db import DBConfig
from flask import current_app
from bson import ObjectId
from utils.tools.log_utils import setup_logging

class DictionaryMapper:
    def __init__(self, db: Optional[DBConfig]=None, logger=None):
        self.logger = logger if logger is not None else setup_logging("DictionaryMapper", "DictionaryMapper.log") 
        # 获取集合
        self.collection = current_app.config["db"].get("dictionary") if db is None else db.get("dictionary")

    def find(self) -> List[Dict]:
        try:
            return list(self.collection.find())
        except Exception as e:
            self.logger.error(f"Error finding dictionaries: {e}")
            return []

    def find_one(self, query: Dict) -> Optional[Dict]:
        try:
            return self.collection.find_one(query)
        except Exception as e:
            self.logger.error(f"Error finding dictionary: {e}")
            return None

    def insert_one(self, data: Dict) -> Optional[ObjectId]:
        try:
            result = self.collection.insert_one(data)
            return result.inserted_id
        except Exception as e:
            self.logger.error(f"Error inserting dictionary: {e}")
            return None

    def update_one(self, query: Dict, update: Dict) -> bool:
        try:
            result = self.collection.update_one(query, update)
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error updating dictionary: {e}")
            return False

    def delete_one(self, query: Dict) -> bool:
        try:
            result = self.collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Error deleting dictionary: {e}")
            return False