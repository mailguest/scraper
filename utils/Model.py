from dataclasses import dataclass
import enum
from os import name
from sys import version

@dataclass
class Model:
    name: str
    version: str

class ModelEnum(enum.Enum):
    # Model name
    GROK_BETA = Model(name="grok-beta", version="2021-10-01")

    def get_name(self):
        return self.value.name
    
    def get_version(self):
        return self.value.version
    
    @staticmethod
    def get_version_by_name(name: str):
        for model in ModelEnum:
            if model.get_name() == name:
                return model.get_version()
        return ModelEnum.GROK_BETA.get_version()
    
    @staticmethod
    def get_models():
        return [model.get_name() for model in ModelEnum]

