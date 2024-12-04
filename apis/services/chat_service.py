from http.client import BAD_GATEWAY
import os
import xml.etree.ElementTree as ET
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from sympy import comp
from utils.Model import ModelEnum
from utils.PlayGroundModel import PlayGroundModel

def completion(prompt: PlayGroundModel):
    model_name = prompt.model_name
    user_input = prompt.user_input
    system_prompt = prompt.prompt
    max_tokens = prompt.max_tokens
    temperature = prompt.temperature

    if model_name not in ModelEnum.get_models():
        raise ValueError("模型名称不存在")
    client = OpenAI(
        api_key = os.getenv("XAI_API_KEY"),
        base_url = os.getenv("BASE_URL"),
    )
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
