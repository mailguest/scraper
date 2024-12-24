from gevent.pywsgi import WSGIServer

from apis import create_app
from utils.tools import setup_logging
import os

if __name__ == "__main__":
    # 初始化日志
    logger = setup_logging("API", "api.log")
    logger.info("Starting API server...")
    app = create_app()
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    
    host = os.getenv("API_HOST", "127.0.0.1")
    port = os.getenv("API_PORT", 5001)
    listener = f"{host}:{port}"
    http_server = WSGIServer(listener, app)
    http_server.serve_forever()
    logger.info(f"API server is running at http://{listener}")