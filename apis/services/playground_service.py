import os
from typing import Dict, List, Optional
from flask import current_app, g
from apis.services.chat_service import completion
from utils.models import PlayGroundModel, PromptTemplate
from utils.mappers import NamespaceMapper, PromptTemplateMapper
from utils.tools import setup_logging

class PromptsFileService:
    def __init__(self, logger=None):
        """
        :param namespace: 命名空间
        """
        self.logger = logger if logger is not None else setup_logging("PromptsFileService", "PromptsFileService.log") 
        self.namespace_mapper:NamespaceMapper = NamespaceMapper()
        self.prompt_template_mapper:PromptTemplateMapper = PromptTemplateMapper()

    def list_all(self) -> Dict[str, List]:
        """
        :return: 返回所有的命名空间 及 其下的文件
        """
        return self.namespace_mapper.list_all()
    
    def save_namespace(self, namespace: Optional[str]) -> str:
        """
        :param namespace: 命名空间
        :return: namespace
        """
        if namespace is None or namespace == "":
            raise ValueError("命名空间不能为空")
        self.namespace_mapper.insert_namespace(namespace)
        return namespace

    def get_prompt(self, namespace:str, name:str, version:str) -> Optional[PromptTemplate]:
        """
        :param namespace: 命名空间
        :param name: 文件名称
        :param version: 版本
        :return: PromptTemplate
        """
        if namespace is None or name is None or version is None:
            raise ValueError("参数不能为空")
        return self.prompt_template_mapper.get_prompt_by_namespace_name_version(namespace, name, version)
    
    def get_versions(self, namespace: str, name: str) -> list[str]:
        """
        :param name: 文件名称
        :param namespace: 命名空间
        :return: namespace, name, versions
        Demo:
        ["version1", "version2"]
        """
        if namespace is None or name is None:
            raise ValueError("参数不能为空")
        return self.prompt_template_mapper.get_versions(namespace, name)
        
    
    def get_latest_prompt(self, namespace: str, name: str) -> Optional[PromptTemplate]:
        """
        :param namespace: 命名空间
        :param name: 文件名称
        :return: 返回最后一次修改的文件内容
        """
        if namespace is None or name is None:
            raise ValueError("参数不能为空")
        version = self.namespace_mapper.get_version(namespace, name)
        if version is None:
            return None
        
        return self.get_prompt(namespace, name, version)
    
    # 保存文件
    def save_prompt(self, prompt_template:PromptTemplate) -> tuple[str, str, str]:
        if prompt_template is None:
            raise ValueError("参数不能为空")
        if prompt_template.name is None or prompt_template.name == "" \
        or prompt_template.namespace is None or prompt_template.namespace == "" \
        or prompt_template.version is None or prompt_template.version == "":
            raise ValueError("参数不能为空")

        self.prompt_template_mapper.insert_prompt_template(prompt_template)
        self.namespace_mapper.insert_filename(prompt_template.namespace, prompt_template.name, prompt_template.version)

        return prompt_template.namespace, prompt_template.name, prompt_template.version
    
    def get_pid(self, namespace:str, name:str) -> Optional[str]:
        """
        :param namespace: 命名空间
        :param name: 文件名称
        :param version: 版本
        :return: pid
        """
        if namespace is None or name is None :
            raise ValueError("参数不能为空")
        return self.namespace_mapper.get_pid_by_namespace_name(namespace, name)
    
    def chat(self, prompt: PlayGroundModel) -> Optional[str]:
        rtn = None
        # self.logger.info(f"api_key: {os.getenv('XAI_API_KEY')}, base_url: {os.getenv('BASE_URL')}, prompt: {prompt.prompt}, user_input: {prompt.user_input}, model_name: '{prompt.model_name}'") 
        rtn = completion(prompt, logger=self.logger)
        # self.logger.info(f"api_key: {os.getenv('XAI_API_KEY')}, base_url: {os.getenv('BASE_URL')}")

        return rtn
    
    def chat_by_pid(self, pid:str, user_input:str, **kwargs) -> Optional[str]:
        rtn = None
        prompt_template = self.prompt_template_mapper.get_prompt_by_pid(pid)
        if prompt_template is None:
            raise ValueError(f"传入的模版ID: {pid} 不存在")
        
        # 如果 **kwargs 有值，则更新 prompt_template中的prompt_content，替换里面的占位符，占位符格式："{key}"
        if kwargs is not None and len(kwargs) > 0:
            prompt_template.prompt_content = prompt_template.prompt_content.format(**kwargs)

        prompt = PlayGroundModel(
            name=prompt_template.name,
            namespace=prompt_template.namespace,
            model_name=prompt_template.model,
            user_input=user_input,
            version=prompt_template.version,
            temperature=prompt_template.temperature,
            max_tokens=prompt_template.max_tokens,
            prompt=prompt_template.prompt_content
        )
        rtn = completion(prompt, logger=self.logger)
        return rtn


    # # 执行事务
    # def execute_transaction(self, client, operations):
    #     session = client.start_session()
    #     try:
    #         session.start_transaction()

    #         # 执行事务中的操作
    #         operations(session)

    #         # 提交事务
    #         session.commit_transaction()
    #         transaction_success = True
    #     except Exception as e:
    #         raise Exception(f"事务失败: {str(e)}")
    #     finally:
    #         if not transaction_success:
    #             session.abort_transaction()
    #         session.end_session()
