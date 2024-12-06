from datetime import datetime
from venv import logger
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from apis.services.playground_service import PromptsFileService
from utils.enums import ModelEnum
from utils.models import PlayGroundModel, PromptTemplate
from utils.tools import check_valid, convert_to_object

bp = Blueprint('playground', __name__, url_prefix='/apis/prompts')

@bp.route('/save', methods=['POST'])
def save_or_update_prompt():
    """
    保存或更新一个prompt
    """
    # logger = current_app.config['logger']
    logger = current_app.logger
    prompt_file_service = PromptsFileService(logger=logger)

    try:
        data = convert_to_object(request.json)
        page_input = PlayGroundModel(**data)
    except ValidationError as e:
        logger.error(f"参数校验错误: {str(e)}")
        return jsonify({'error': '参数校验错误'}), 400

    try:
        prompt_template = PromptTemplate(
            name = page_input.name,
            namespace = page_input.namespace,
            version = datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            prompt_content = page_input.prompt,
            user_input = page_input.user_input,
            model = page_input.model_name,
            model_version = ModelEnum.get_version_by_name(page_input.model_name),
            temperature = page_input.temperature,
            max_tokens = page_input.max_tokens
        )
        _namespace, _name, _version = prompt_file_service.save_prompt(prompt_template)
        _versions = prompt_file_service.get_versions(namespace=_namespace, name=_name)
        return jsonify({
                'message': 'Prompt created successfully', 
                'namespace': _namespace, 
                'name': _name, 
                'version': _version,
                'versions': _versions
            }), 200
    except Exception as e:
        logger.error(f"保存错误: {str(e)}")
        return jsonify({'保存错误': str(e)}), 500
    
@bp.route('/nsave', methods=['POST'])
def save_namespace():
    # logger = current_app.config['logger']
    logger = current_app.logger

    data = request.json
    if data is None or 'namespace' not in data:
        return jsonify({'error': '参数校验错误'}), 400

    namespace = data.get('namespace')
    try:
        prompt_file_service = PromptsFileService(logger=logger)
        prompt_file_service.save_namespace(namespace)
        return jsonify({'message': 'Namespace saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/get', methods=['POST'])
def get_prompt():
    """
    获取一个prompt
    """
    # logger = current_app.config['logger']
    logger = current_app.logger
    data = request.json
    if data is None:
        return jsonify({'error': '参数校验错误'}), 400
    if not check_valid(data, ['name', 'namespace']):
        return jsonify({'error': '参数校验错误'}), 400

    namespace = data.get('namespace')
    name = data.get('name')
    version = data.get('version', None)

    try:
        prompt_file_service = PromptsFileService(logger=logger)
        if version:
            _prompt_template = prompt_file_service.get_prompt(namespace=namespace, name=name, version=version)
        else:
            _prompt_template = prompt_file_service.get_latest_prompt(name=name, namespace=namespace)
        
        if _prompt_template is None:
            return jsonify({'error': 'Prompt not found'}), 404

        _versions = prompt_file_service.get_versions(namespace=namespace, name=name)

        return jsonify({
                'message': 'Prompt load successfully', 
                'namespace': _prompt_template.namespace, 
                'name': _prompt_template.name, 
                'version': _prompt_template.version,
                'prompt': _prompt_template.prompt_content,
                'user_input': _prompt_template.user_input,
                'model_name': _prompt_template.model,
                'temperature': _prompt_template.temperature,
                'max_tokens': _prompt_template.max_tokens,
                'versions': _versions
            }), 200
    except Exception as e:
        logger.error(f"Error getting prompt: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/tree', methods=['GET'])
def get_tree():
    """
    获取prompt树
    """
    prompt_file_service = PromptsFileService(logger=logger)
    tree = prompt_file_service.list_all()
    return jsonify({
                'message': 'tree load successfully', 
                'tree': tree 
            }), 200

@bp.route('/versios', methods=['POST'])
def get_versions():
    """
    获取prompt的所有版本
    """
    data = request.json
    if data is None:
        return jsonify({'error': '参数校验错误'}), 400
    if not check_valid(data, ['name', 'namespace']):
        return jsonify({'error': '参数校验错误'}), 400

    namespace = data.get('namespace')
    name = data.get('name')

    try:
        prompt_file_service = PromptsFileService(logger=logger)
        _versions = prompt_file_service.get_versions(namespace=namespace, name=name)
        return jsonify({
                'message': 'Versions load successfully', 
                'name': name, 
                'namespace': namespace, 
                'versions': _versions
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@bp.route('/pid', methods=['POST'])
def get_pid():
    """
    获取prompt的所有版本
    """
    data = request.json
    if data is None:
        return jsonify({'error': '参数校验错误'}), 400
    if not check_valid(data, ['name', 'namespace']):
        return jsonify({'error': '参数校验错误'}), 400

    namespace = data.get('namespace')
    name = data.get('name')

    try:
        prompt_file_service = PromptsFileService(logger=logger)
        _pid = prompt_file_service.get_pid(namespace=namespace, name=name)
        return jsonify({
                'message': 'Versions load successfully', 
                'name': name, 
                'namespace': namespace, 
                'pid': _pid
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500