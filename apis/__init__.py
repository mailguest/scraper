import json
import os
from venv import logger
from flask import Flask
from database.db import init_engine, init_session, init_tables
import toml

def create_app():
    app = register_flask() # 注册 Flask APP
    register_db(app) # 注册数据库连接
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
    db_engine = init_engine(app.config.get("DATABASE"))
    db_session = init_session(db_engine)
    app.config['DB_ENGINE'] = db_engine
    app.config['DB_SESSION'] = db_session
    # 确保数据库表只创建一次
    with app.app_context():
        init_tables(db_engine)

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

