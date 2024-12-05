from datetime import datetime
from typing import Optional
from flask import current_app
from config.db import DBConfig
from utils.log_utils import setup_logging

class TaskLogsMapper:
    def __init__(self, db: Optional[DBConfig]=None, logger=None):
        self.logger = logger if logger is not None else setup_logging("TaskLogsMapper", "TaskLogsMapper.log") 
        # 获取集合
        self.collection = current_app.config["db"].fetch_table('tasklogs') if db is None else db.fetch_table('tasklogs')

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
        
    def get_task_logs(self, page:int=1, size:int=10, task_name:str=None, status:str=None) -> dict:
        filter = {}
        if task_name:
            filter['task_name'] = task_name
        if status:
            filter['status'] = status
            
        total = self.collection.count_documents(filter)
        logs_cursor = self.collection.find(filter).skip((page-1)*size).limit(size)
        
        logs = []
        for log in logs_cursor:
            log_entry = {
                'task_name': log.get('task_name', None),
                'start_time': log.get('start_time', None),
                'status': log.get('status', None),
                'data_count': log.get('data_count', None),
                'duration': log.get('duration', None),
                'end_time': log.get('end_time', None)
            }
            if log_entry:
                logs.append(log_entry)
        
        return {
            'total': total,
            'items': logs,
            'page': page,
            'size': size,
            'total_pages': (total + size - 1) // size
        }