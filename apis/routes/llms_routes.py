from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError

from apis.services.playground_service import PromptsFileService
from utils.PlayGroundModel import PlayGroundModel
from utils.Model import ModelEnum
from utils.check import convert_to_object
from datetime import datetime

bp = Blueprint('llms', __name__, url_prefix='/apis/llms')

@bp.route('/models', methods=['GET'])
def get_models():
    """
    获取所有模型
    """
    models = ModelEnum.get_models()
    return jsonify(models), 200

@bp.route('/chat', methods=['POST'])
def chat():
    logger = current_app.config['logger']
    prompt_file_service = PromptsFileService(logger=logger)

    try:
        data = convert_to_object(request.json)
        page_input = PlayGroundModel(**data)
    except ValidationError as e:
        logger.error(f"参数校验错误: {str(e)}")
        return jsonify({'error': '参数校验错误'}), 400


    data["time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data["user"] = page_input.model_name;
    try:
        data["reply"] = prompt_file_service.chat(page_input)
    except Exception as e:
        error = f"调用模型出错: {str(e)}"
        logger.error(error)
        data["reply"] = error

    return jsonify(data), 200