from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from utils.enums import ModelEnum


@dataclass
class PromptTemplate:
    name : str = ""
    version : str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    namespace : str = "default"
    prompt_content : str = ""
    user_input : str = ""
    model : str = ModelEnum.GROK_BETA.get_name()
    model_version : str = ModelEnum.get_version_by_name(model)
    temperature: float = 1.0
    max_tokens: int = 4096

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional['PromptTemplate']:
        """
        从字典创建实体对象
        """
        if not data:
            return None
            
        return cls(
            namespace=data.get('namespace', 'default'),
            name=data.get('name', ''),
            version=data.get('version', ''),
            prompt_content=data.get('prompt_content', ''),
            user_input=data.get('user_input', ''),
            model=data.get('model', ModelEnum.GROK_BETA.get_name()),
            model_version=data.get('model_version', ModelEnum.GROK_BETA.get_version()),
            temperature=data.get('temperature', 1.0),
            max_tokens=data.get('max_tokens', 4096)
        )