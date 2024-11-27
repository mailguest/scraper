from datetime import datetime
from typing import Optional
from flask import current_app
from config.db import DBConfig
from utils.log_utils import setup_logging


class TaskLogsMapper:
    def __init__(self, db: Optional[DBConfig]=None, logger=None):
        self.logger = logger if logger is not None else setup_logging("TaskLogsMapper", "TaskLogsMapper.log") 
        # 获取集合
        self.collection = current_app.config["db"].get_collection('tasklogs') if db is None else db.get_collection('tasklogs')

    def log_task_start(self, task_name):
        start_time = datetime.now()
        log_entry = {
            'task_name': task_name,
            'start_time': start_time,
            'status': 'running'
        }
        log_id = self.collection.insert_one(log_entry).inserted_id
        return log_id, start_time

    def log_task_end(self, log_id, start_time:datetime, data_count:int):
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        self.collection.update_one(
            {'_id': log_id},
            {'$set': {
                'end_time': end_time,
                'duration': duration,
                'data_count': data_count,
                'status': 'completed'
            }}
        )