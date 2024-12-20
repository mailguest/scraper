from gevent.pywsgi import WSGIServer
from flask import Flask
from config.db import db_connect
from utils.tools import setup_logging
import os

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_app():
    app = Flask(__name__,
                static_url_path='/static',
                static_folder=os.path.join(BASE_DIR, 'static'),
                template_folder=os.path.join(BASE_DIR, 'templates'))
    
    # 初始化数据库
    app.config['db'] = db_connect
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    
    # 注册路由
    from apis.routes import article_routes, job_routes, proxy_routes, view_routes, dictionary_routes, playground_routes, llms_routes
    app.register_blueprint(article_routes.bp)
    app.register_blueprint(job_routes.bp)
    app.register_blueprint(proxy_routes.bp)
    app.register_blueprint(view_routes.bp)
    app.register_blueprint(dictionary_routes.bp)
    app.register_blueprint(playground_routes.bp)
    app.register_blueprint(llms_routes.bp)
    
    return app


if __name__ == "__main__":
    # 初始化日志
    logger = setup_logging("API", "api.log")
    logger.info("Starting API server...")
    app = create_app()
    
    host = "127.0.0.1"
    port = os.getenv("API_PORT", 5001)
    url = f"http://{host}:{port}"
    listener = f"{host}:{port}"
    
    http_server = WSGIServer(listener, app)
    logger.info(f"API server is running at {url}")
    http_server.serve_forever()