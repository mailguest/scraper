import json
import os
from venv import logger
from flask import Flask
import toml

from database.db_manager import DatabasePool
from utils.GlobalManager import GlobalManager

def create_app():
    GlobalManager.init("API")
    app = register_flask() # 注册 Flask APP
    database_pool = register_db(app) # 注册数据库连接
    GlobalManager.set("database", database_pool)
    register_route(app) # 注册路由器
    return app

def register_flask():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(__name__,
        static_url_path='/static',
        static_folder=os.path.join(BASE_DIR, 'client', 'static'),
        root_path=BASE_DIR,
        template_folder=os.path.join(BASE_DIR, 'client', 'templates'),
        instance_path=os.path.join(BASE_DIR, 'config'),
        instance_relative_config=True
    )
    app.config.from_file("appbase.toml", load=toml.load, text=True)
    return app

def register_db(app):
    app.config.from_file("database.toml", load=toml.load, text=True)
    # 初始化数据库
    database_pool = DatabasePool()
    database_pool.init_db(app.config.get("DATABASE"))
    return database_pool

def register_route(app):
    from apis.routes import view_routes
    app.register_blueprint(view_routes.bp)
    

    # from apis.routes import article_routes
    # app.register_blueprint(article_routes.bp)
    # from apis.routes import job_routes
    # from apis.routes import proxy_routes
    
    # from apis.routes import dictionary_routes
    # from apis.routes import playground_routes
    # from apis.routes import llms_routes
    # app.register_blueprint(job_routes.bp)
    # app.register_blueprint(proxy_routes.bp)
    
    # app.register_blueprint(dictionary_routes.bp)
    # app.register_blueprint(playground_routes.bp)
    # app.register_blueprint(llms_routes.bp)

