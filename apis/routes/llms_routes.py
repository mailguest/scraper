from flask import Blueprint, request, jsonify, current_app

from utils.Model import ModelEnum

bp = Blueprint('llms', __name__, url_prefix='/apis/llms')

@bp.route('/models', methods=['GET'])
def get_models():
    """
    获取所有模型
    """
    models = ModelEnum.get_models()
    return jsonify(models), 200