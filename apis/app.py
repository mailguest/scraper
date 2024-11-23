from flask import Flask
from utils.log_utils import setup_logging
from config.db import DBConfig
from utils.ArticleMapper import ArticleMapper
import os

# 获取项目根目录
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_app():
    app = Flask(__name__,
                static_url_path='/static',
                static_folder=os.path.join(BASE_DIR, 'static'),
                template_folder=os.path.join(BASE_DIR, 'templates'))
    
    # 初始化数据库
    app.config['db'] = DBConfig()
    app.config['article_mapper'] = ArticleMapper(db=app.config['db'], logger=logger)
    app.config['logger'] = logger
    
    # 注册路由
    from apis.routes import article_routes, job_routes, proxy_routes, view_routes
    app.register_blueprint(article_routes.bp)
    app.register_blueprint(job_routes.bp)
    app.register_blueprint(proxy_routes.bp)
    app.register_blueprint(view_routes.bp)
    
    return app

if __name__ == "__main__":
    # 初始化日志
    logger = setup_logging("API", "api.log")
    logger.info("Starting API server...")
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)