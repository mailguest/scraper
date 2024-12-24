import enum
from typing import Optional

class LLModel:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def get_name(self):
        return self.name

    def get_version(self):
        return self.version
    
class ModelEnum(enum.Enum):

    GROK_BETA = LLModel(name="grok-beta", version="2021-10-01")

    def get_name(self):
        return self.value.name
    
    def get_version(self):
        return self.value.version
    
    @staticmethod
    def get_version_by_name(name: str) -> Optional[str]:
        for model in ModelEnum:
            if model.get_name() == name:
                return model.get_version()
        return None
    
    @staticmethod
    def get_models():
        return [model.get_name() for model in ModelEnum]