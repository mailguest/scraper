from bson import ObjectId
from flask import Blueprint, jsonify, request, current_app, g
from utils.mappers import DictionaryMapper

bp = Blueprint('dictionary', __name__, url_prefix='/apis')

@bp.route('/dictionaries', methods=['GET'])
def get_dictionaries():
    """
    查询所有字典数据或根据查询参数进行过滤
    """
    parent = request.args.get('parent')
    key = request.args.get('key')
    
    query = {}
    if parent:
        query['parent'] = {'$regex': parent}
    if key:
        query['key'] = {'$regex': key}

    dictonary_mapper = DictionaryMapper()
    if query:
        dictionaries = list(dictonary_mapper.find(query))
    else:
        dictionaries = list(dictonary_mapper.find())
    for dictionary in dictionaries:
        dictionary['_id'] = str(dictionary['_id'])
    return jsonify(dictionaries)

@bp.route('/dictionaries/<id>', methods=['GET'])
def get_dictionary(id):
    """
    查询指定字典数据
    """
    dictonary_mapper = DictionaryMapper()
    dictionary = dictonary_mapper.find_one({'_id': ObjectId(id)})
    if dictionary:
        dictionary['_id'] = str(dictionary['_id'])
        return jsonify(dictionary)
    return jsonify({'error': 'Dictionary not found'}), 404

@bp.route('/dictionaries', methods=['POST'])
def add_dictionary():
    """
    添加字典数据
    """
    data = request.json
    dictonary_mapper = DictionaryMapper()
    dictionary_id = dictonary_mapper.insert_one(data).inserted_id
    return jsonify({'_id': str(dictionary_id)})

@bp.route('/dictionaries/<id>', methods=['PUT'])
def update_dictionary(id):
    """
    更新字典数据
    """
    data = request.json
    dictonary_mapper = DictionaryMapper()
    dictonary_mapper.update_one({'_id': ObjectId(id)}, {'$set': data})
    return jsonify({'_id': id})

@bp.route('/dictionaries/<id>', methods=['DELETE'])
def delete_dictionary(id):
    """
    删除字典数据
    """
    dictonary_mapper = DictionaryMapper()
    dictonary_mapper.delete_one({'_id': ObjectId(id)})
    return jsonify({'_id': id})