import json
from pathlib import Path

CONFIG_PATH = Path("config/schedule_config.json")

def load_schedule_config():
    if not CONFIG_PATH.exists():
        return {"jobs": []}
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_schedule_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# ... 其他定时任务相关业务逻辑 