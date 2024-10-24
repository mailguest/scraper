from flask import Flask, jsonify, request # 导入 Flask 框架
from utils.log_utils import setup_logging # 导入日志工具
from utils.cache_utils import get_search, start_worker  # 导入缓存管理

app = Flask(__name__)

# 使用日志工具类设置日志
logger = setup_logging("API", "api.log")

# 获取数据的 API 端点
@app.route('/data', methods=['GET'])
def get_data():
    logger.info("Received request for data")

    # 获取查询参数 page, limit 和 date，设置默认值
    page = int(request.args.get('page', 1))  # 默认为第一页
    limit = int(request.args.get('limit', 10))  # 默认为每页 10 条数据
    date_str = request.args.get('date', None)  # 如果提供了日期，按日期过滤

    logger.info("Parameters - page: %d, limit: %d, date: %s", page, limit, date_str)

    # 加载缓存中的数据
    data = get_search(logger).filter_data_by_date(page, limit, date_str)

    # 如果请求的页面超出范围，返回空列表
    if not data:
        logger.warning("No data available for the requested page: %d", page)
        return jsonify({"error": "No data available for the requested page"}), 404

    return jsonify(data)

@app.route('/article/<uuid>', methods=['GET'])
def get_article(uuid):
    logger.info(f"Received request for article with UUID: {uuid}")

    # 加载缓存中的数据
    data = get_search(logger).load_data_by_uuid(uuid)

    if not data:
        logger.warning(f"No article found with UUID: {uuid}")
        return jsonify({"error": "Article not found"}), 404

    return jsonify(data)

if __name__ == "__main__":
    logger.info("Starting API server...")

    # 启动子线程来定期更新缓存
    start_worker(logger, interval=600)

    app.run(debug=True, host='0.0.0.0', port=5001)
