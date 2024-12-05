from apis.services.playground_service import PromptsFileService
from utils import PromptTemplate


def main():
    # 创建一个日志记录器（可选）
    logger = None

    # 模拟 NamespaceMapper 和 PromptTemplateMapper
    class MockNamespaceMapper:
        def __init__(self):
            self.namespaces = {}
            self.versions = {}

        def list_all(self):
            return self.namespaces

        def insert_namespace(self, namespace):
            if namespace not in self.namespaces:
                self.namespaces[namespace] = []

        def insert_filename(self, namespace, name, version):
            if namespace not in self.versions:
                self.versions[namespace] = {}
            if name not in self.versions[namespace]:
                self.versions[namespace][name] = []
            self.versions[namespace][name].append(version)

        def get_version(self, namespace, name):
            if namespace in self.versions and name in self.versions[namespace]:
                return self.versions[namespace][name][-1]
            return None

    class MockPromptTemplateMapper:
        def __init__(self):
            self.prompts = {}

        def insert_prompt_template(self, prompt_template):
            key = (prompt_template.namespace, prompt_template.name)
            if key not in self.prompts:
                self.prompts[key] = []
            self.prompts[key].append(prompt_template)

        def get_prompt_by_namespace_name_version(self, namespace, name, version):
            key = (namespace, name)
            if key in self.prompts:
                for prompt in self.prompts[key]:
                    if prompt.version == version:
                        return prompt
            return None

        def get_versions(self, namespace, name):
            key = (namespace, name)
            if key in self.prompts:
                return [prompt.version for prompt in self.prompts[key]]
            return []

    # 创建 MockNamespaceMapper 和 MockPromptTemplateMapper 实例
    namespace_mapper = MockNamespaceMapper()
    prompt_template_mapper = MockPromptTemplateMapper()

    # 创建 PromptsFileService 实例
    service = PromptsFileService(logger=logger)
    service.namespace_mapper = namespace_mapper
    service.prompt_template_mapper = prompt_template_mapper

    # 创建 PromptTemplate 实例
    prompt1 = PromptTemplate(name="test_prompt", namespace="test_namespace", version="v1", content="This is a test prompt.")
    prompt2 = PromptTemplate(name="test_prompt", namespace="test_namespace", version="v2", content="This is another test prompt.")

    # 测试 save_prompt 方法
    service.save_prompt(prompt1)
    service.save_prompt(prompt2)

    # 测试 get_latest_prompt 方法
    latest_prompt = service.get_latest_prompt(namespace="test_namespace", name="test_prompt")
    assert latest_prompt is not None, "Latest prompt should not be None"
    assert latest_prompt.version == "v2", "Latest prompt version should be 'v2'"

    # 测试 get_versions 方法
    versions = service.get_versions(namespace="test_namespace", name="test_prompt")
    assert versions == ["v1", "v2"], f"Versions should be ['v1', 'v2'], but got {versions}"

    print("All tests passed.")
    


