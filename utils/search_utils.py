import json
import os

class SearchUtils():
    def __init__(self, logger, data=[]):
        self.logger = logger
        self.data = data

    def load_all_data(self):
        """
        加载所有的数据文件内容
        """
        data_dir = 'data'
        all_data = []
        
        self.logger.info("Loading all data from directory: %s", data_dir)
        
        # 遍历目录中的所有 JSON 文件
        for filename in os.listdir(data_dir):
            # 仅加载以 'scraped_list_' 开头且以 '.json' 结尾的文件( 即抓取的列表数据 )
            if filename.startswith("scraped_list_") and filename.endswith(".json"):
                filepath = os.path.join(data_dir, filename)
                self.logger.info("Loading data from file: %s", filepath)
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        all_data.extend(data)
                    except json.JSONDecodeError as e:
                        self.logger.error("Failed to load data from file %s: %s", filepath, str(e))
        
        self.logger.info("Total records loaded: %d", len(all_data))
        self.data = all_data
        return self.data
    
    def filter_data_by_date(self, page=None, limit=None, date_str=None):
        """
        过滤数据根据指定日期
        """
        filtered_data = self.data

        self.logger.info(f"Filtering data for date: {date_str}, page: {page}, limit: {limit}")
        if date_str is not None:
            filtered_data = [item for item in self.data if 'date' in item and item['date'] == date_str]
        
        if page and limit:
            # 计算分页数据的起始和结束位置
            start = (page - 1) * limit
            end = start + limit
            filtered_data = filtered_data[start:end]

        self.logger.info(f"Total records after filtering by date: {len(filtered_data)}")
        
        return filtered_data
    
    def load_data_by_uuid(self, uuid):
        """
        通过 UUID 加载单个数据
        """
        self.logger.info(f"Loading content from index count is: {len(self.data)}")
        for item in self.data:
            # self.logger.info(f"{item['UUID']} : {uuid}")
            if item['UUID'] == uuid:
                date = item["date"]
                file_path = os.path.join("data", date, f"{uuid}.json")
                self.logger.info(f"Loading content's file_path is : {file_path}")
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return data
        return None
