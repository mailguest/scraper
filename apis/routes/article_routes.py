from flask import Blueprint, jsonify, request, current_app, g
from scripts.scrape_list import scrape as scrape_list
from scripts.scrape_content import scrape_all_articles
from utils.mappers import ArticleMapper

bp = Blueprint('article', __name__, url_prefix='/apis')

@bp.route('/articles', methods=['GET'])
def get_data():
    """
    获取文章数据的 API 端点
    :return: JSON 格式的文章数据
    """
    logger = current_app.logger
    
    # 获取查询参数 page, limit 和 date，设置默认值
    page = int(request.args.get('page', 1))  # 默认为第一页
    limit = int(request.args.get('limit', 10))  # 默认为每页 10 条数据


    article_filter = {
        "date": request.args.get('date', None),  # 如果提供了日期，按日期过滤
        "source": request.args.get('source', None), # 如果提供了来源，按来源过滤
        "status": request.args.get('status', None)
    }

    logger.info(f"Parameters - get_data: article_filter={article_filter}, page={page}, limit={limit}")

    # 加载缓存中的数据
    article_mapper = ArticleMapper()
    data = article_mapper.get_articles_by_article(article_filter, page, limit)

    # 如果请求的页面超出范围，返回空列表
    if not data or not data['items']:
        logger.warning("No data available for the requested page: %d", page)
        return jsonify({"error": "No data available for the requested page"}), 404

    return jsonify(data)

@bp.route('/article/<uuid>', methods=['GET'])
def get_article(uuid):
    """
    获取指定 UUID 的文章
    :param uuid: 文章的 UUID
    :return: JSON 格式的文章数据
    """
    logger = current_app.logger

    logger.info(f"Received request for article with UUID: {uuid}")

    # 加载缓存中的数据
    article_mapper = ArticleMapper()
    data = article_mapper.get_article_by_uuid(uuid)

    if not data:
        logger.warning(f"No article found with UUID: {uuid}")
        return jsonify({"error": "Article not found"}), 404

    return jsonify(data)

@bp.route('/article/<uuid>', methods=['DELETE'])
def delete_article(uuid):
    logger = current_app.logger

    article_mapper = ArticleMapper()
    article_mapper.delete_article(uuid)
    return jsonify({"message": "Article deleted"}), 204

@bp.route('/scrape', methods=['POST'])
def do_scrape():
    """
    手动抓取一次数据
    """
    logger = current_app.logger
    db = current_app.config['db']
    try:
        logger.info("Running manual scraping job...")
        scrape_list(logger, db)
        scrape_all_articles(logger, db)
        logger.info("Manual scraping completed successfully.")
    except Exception as e:
        logger.error(f"Manual scraping failed: {str(e)}")
        return jsonify({"error": "Manual scraping failed"}), 500
    return jsonify({"message": "Manual scraping completed successfully"})

