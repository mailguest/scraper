from typing import Any


def check_valid(data, keys:list) -> bool:
    for key in keys:
        if key not in data:
            return False
        if not data.get(key):
            return False
    return True

def convert_to_object(data: Any):
    if data is None:
        raise ValueError("参数校验错误")
    return {key: data.get(key, None) for key in data.keys()}