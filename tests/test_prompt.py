from apis.services.playground_service import PromptsFileService

def main():
    prompt = PromptsFileService()
    prompt.save_prompt('content content content content content1')
    prompt.save_prompt('content content content content content2')
    prompt.save_prompt('content content content content content3')
    prompt.save_prompt('content content content content content4')

    prompt.save_prompt('content content content content content3', 'test')
    prompt.save_prompt('content content content content content4', 'test2')

    prompt.save_prompt('content content content content content3', '', 'fund')
    prompt.save_prompt('content content content content content3', 'test1', 'fund')
    prompt.save_prompt('content content content content content4', 'test2', 'fund')

    print(prompt.list_versions('未命名', 'default'))

    print(prompt.list_all())

    prompt.delete_prompt("未命名")