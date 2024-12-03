from typing import Dict, List, Optional
from flask import current_app
from utils.NamespaceMapper import NamespaceMapper
from utils.PromptTemplate import PromptTemplate
from utils.PromptTemplateMapper import PromptTemplateMapper
from utils.log_utils import setup_logging

class PromptsFileService:
    def __init__(self, logger=None):
        """
        :param namespace: 命名空间
        """
        self.logger = logger if logger is not None else setup_logging("PromptsFileService", "PromptsFileService.log") 
        self.namespace_mapper:NamespaceMapper = current_app.config['namespace_mapper']
        self.prompt_template_mapper:PromptTemplateMapper = current_app.config['playground_mapper']

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
