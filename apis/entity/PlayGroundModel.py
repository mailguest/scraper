from typing import Annotated, Optional
from pydantic import BaseModel, Field, constr, field_validator
from config.config import Config

class PlayGroundModel(BaseModel):
    name: Annotated[str, constr(min_length=1, max_length=50)]
    namespace: Annotated[str, constr(min_length=1, max_length=50)]
    model_name: Annotated[str, constr(min_length=1, max_length=50)]
    user_input: str
    version: Optional[str] = None
    temperature: Annotated[float, Field(strict=True, ge=0.0, le=2.0)] # confloat(default=1.0, ge=0.0, le=2.0)
    max_tokens: Annotated[int, Field(default=Config.DEFAULT_PROMPT_TOKENS, strict=True, ge=0, le=Config.DEFAULT_PROMPT_TOKENS)]# conint(default=Config.DEFAULT_PROMPT_TOKENS, ge=0, le=Config.DEFAULT_PROMPT_TOKENS)
    prompt: str = Field(max_length=Config.DEFAULT_PROMPT_TOKENS)

    @field_validator('name', 'namespace', 'model_name', 'user_input', 'prompt', mode='before')
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator('temperature', mode='before')
    def validate_temperature(cls, v):
        try:
            return float(v)
        except ValueError:
            raise ValueError('temperature must be a valid float')

    @field_validator('max_tokens', mode='before')
    def validate_max_tokens(cls, v):
        try:
            return int(v)
        except ValueError:
            raise ValueError('max_tokens must be a valid integer')
        
    class Config:
        protected_namespaces = ()  # 解决命名空间冲突

        json_schema_extra = {
            "example": {
                "name": "prompt",
                "namespace": "default",
                "model_name": "default_model",
                "user_input": "example input",
                "version": "v1",
                "temperature": 0.5,
                "max_tokens": 1024,
                "prompt": "example prompt",
                "versions": ["v1", "v2"]
            }
        }