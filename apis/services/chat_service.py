import os
from openai import OpenAI
from utils.Model import ModelEnum
from utils.PlayGroundModel import PlayGroundModel
from utils.log_utils import setup_logging

def completion(prompt: PlayGroundModel, logger):
    
    logger = logger if logger is not None else setup_logging("completion", "completion.log") 
    
    model_name = prompt.model_name
    user_input = prompt.user_input
    system_prompt = prompt.prompt
    max_tokens = prompt.max_tokens
    temperature = prompt.temperature

    if model_name not in ModelEnum.get_models():
        raise ValueError("模型名称不存在")
    try:
        client = OpenAI(
            api_key = os.getenv("XAI_API_KEY"),
            base_url = os.getenv("BASE_URL"),
        )
    except Exception as e:
        logger.error(f"api_key: {os.getenv('XAI_API_KEY')}, base_url: {os.getenv('BASE_URL')}, error: {str(e)}")
        raise ValueError("OpenAI client 初始化失败")
    
    messages = [{"role": "user", "content": user_input}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    completion = client.chat.completions.create(
        model = model_name,
        messages = messages,
        max_tokens = max_tokens,
        temperature = temperature,
    )
    return completion.choices[0].message.content
