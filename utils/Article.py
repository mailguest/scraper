from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

@dataclass
class Article:
    UUID: str
    title: str
    content: str
    content_short: Optional[str]
    date: str
    source: str
    list_uri: Optional[str]
    content_uri: Optional[str]
    status: str = 'success'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """
        将实体对象转换为字典
        """
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict) -> 'Article':
        """
        从字典创建实体对象
        """
        if not data:
            return None
            
        return cls(
            UUID=data.get('UUID', ''),
            title=data.get('title', ''),
            content=data.get('content', ''),
            content_short=data.get('content_short'),
            date=data.get('date', ''),
            source=data.get('source', ''),
            list_uri=data.get('list_uri'),
            content_uri=data.get('content_uri'),
            status=data.get('status', 'success'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
 