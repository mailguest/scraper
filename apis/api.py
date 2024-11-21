from flask import Flask, jsonify, request, render_template # 导入 Flask 框架
from utils.log_utils import setup_logging # 导入日志工具
from utils.cache_utils import get_search, start_worker  # 导入缓存管理
import json
from pathlib import Path
import os
from scripts.scraper import scrape as scrape_list  # 列表爬虫
from scripts.scrape_content import scrape_all_articles as scrape_content  # 内容爬虫
import scripts.scrape_ipproxy as ipproxy

# 获取当前文件所在目录的上级目录（项目根目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 创建Flask应用时指定模板文件夹路径
app = Flask(__name__, 
            static_url_path='/static', # 指定静态文件夹路径
            static_folder=os.path.join(BASE_DIR, 'static'), # 指定静态文件夹路径
            template_folder=os.path.join(BASE_DIR, 'templates') # 指定模板文件夹路径
)

# 使用日志工具类设置日志
logger = setup_logging("API", "api.log")

# 添加新的路由处理定时任务相关的请求
CONFIG_PATH = Path("config/schedule_config.json")

def load_schedule_config():
    """加载定时任务配置"""
    if not CONFIG_PATH.exists():
        return {"jobs": []}
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_schedule_config(config):
    """保存定时任务配置"""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


# 添加页面路由
@app.route('/')
def index():
    return get_jobs_page()

@app.route('/jobs')
def get_jobs_page():
    return render_template('jobs.html', active_page='jobs')

@app.route('/proxy')
def proxy_page():
    return render_template('proxy.html', active_page='proxy')

@app.route('/articles')
def article_page():
    return render_template('articles.html', active_page='articles')

#########################################################
# API 端点 IP代理
#########################################################
@app.route('/apis/proxies')
def get_proxies():
    try:
        proxies = ipproxy.get_proxies(logger)
        return jsonify(proxies)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/apis/proxies/refresh', methods=['POST'])
def refresh_proxies():
    try:
        ipproxy.scrape_ipproxies(logger)
        return jsonify({"message": "代理列表已更新"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/apis/proxies/<path:ip>/test', methods=['POST'])
def test_and_flush_proxy(ip):
    # 测试代理
    # logger.info(f"测试代理: {ip}")
    # logger.info(f"测试代理: {ip.split(':')[0]}")
    # logger.info(f"测试代理: {ip.split(':')[1]}")
    # proxy = ipproxy.IpProxy(ip.split(':')[0], ip.split(':')[1], '', '')
    proxy = ipproxy.find(ip.split(':')[0], ip.split(':')[1])
    if proxy is None:
        return jsonify({"error": f"代理 {ip} 不存在"}), 500
    if  ipproxy.test_proxy(proxy):
        logger.info(f"代理 {ip} 测试成功")
        return jsonify({"message": f"代理 {ip} 测试成功"})
    else:
        ipproxy.IpProxyMapping(logger).update_proxy(proxy)
        logger.error(f"代理 {ip} 测试失败")
        return jsonify({"error": f"代理 {ip} 测试失败"}), 500

@app.route('/apis/proxies/<path:ip>', methods=['DELETE'])
def delete_proxy(ip):
    try:
        logger.info(f"删除代理: {ip}")
        ipproxy.delete(ipproxy.IpProxy(ip.split(':')[0], ip.split(':')[1], '', ''))
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

#########################################################
# API 端点 文章
#########################################################

@app.route('/apis/articles', methods=['GET'])
def get_data():
    """
    获取文章数据的 API 端点
    :return: JSON 格式的文章数据
    """
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

@app.route('/apis/article/<uuid>', methods=['GET'])
def get_article(uuid):
    """
    获取指定 UUID 的文章
    :param uuid: 文章的 UUID
    :return: JSON 格式的文章数据
    """
    logger.info(f"Received request for article with UUID: {uuid}")

    # 加载缓存中的数据
    data = get_search(logger).load_data_by_uuid(uuid)

    if not data:
        logger.warning(f"No article found with UUID: {uuid}")
        return jsonify({"error": "Article not found"}), 404

    return jsonify(data)

@app.route('/apis/refresh', methods=['POST'])
def refresh_cache():
    """
    刷新缓存
    :return: JSON 格式的响应
    """
    logger.info("Received request to flush cache")

    # 清空缓存
    get_search(logger).refresh_cache()

    return jsonify({"message": "Cache flushed"})

@app.route('/apis/scrape', methods=['POST'])
def do_scrape():
    """
    手动抓取一次数据
    """
    try:
        logger.info("Running manual scraping job...")
        from scripts.scraper import scrape
        scrape()
        from scripts.scrape_content import scrape_all_articles
        scrape_all_articles(logger)
        logger.info("Manual scraping completed successfully.")
    except Exception as e:
        logger.error(f"Manual scraping failed: {str(e)}")
        return jsonify({"error": "Manual scraping failed"}), 500
    return jsonify({"message": "Manual scraping completed successfully"})


#########################################################
# API 端点 定时任务
#########################################################

@app.route('/apis/jobs', methods=['GET'])
def get_jobs():
    """获取所有定时任务"""
    try:
        config = load_schedule_config()
        return jsonify(config['jobs'])
    except Exception as e:
        logger.error(f"Error getting jobs: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/apis/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """获取特定定时任务"""
    try:
        config = load_schedule_config()
        job = next((job for job in config['jobs'] if job['id'] == job_id), None)
        if not job:
            return jsonify({"error": "Job not found"}), 404
        return jsonify(job)
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/apis/jobs', methods=['POST'])
def create_job():
    """创建新的定时任务"""
    try:
        new_job = request.json
        config = load_schedule_config()
        
        # 检查ID是否已存在
        if any(job['id'] == new_job['id'] for job in config['jobs']):
            return jsonify({"error": "Job ID already exists"}), 400
        
        config['jobs'].append(new_job)
        save_schedule_config(config)
        return jsonify(new_job), 201
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/apis/jobs/<job_id>', methods=['PUT'])
def update_job(job_id):
    """更新定时任务"""
    try:
        updated_job = request.json
        config = load_schedule_config()
        
        job_index = next((i for i, job in enumerate(config['jobs']) if job['id'] == job_id), None)
        if job_index is None:
            return jsonify({"error": "Job not found"}), 404
        
        config['jobs'][job_index] = updated_job
        save_schedule_config(config)
        return jsonify(updated_job)
    except Exception as e:
        logger.error(f"Error updating job {job_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/apis/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """删除定时任务"""
    try:
        config = load_schedule_config()
        config['jobs'] = [job for job in config['jobs'] if job['id'] != job_id]
        save_schedule_config(config)
        return '', 204
    except Exception as e:
        logger.error(f"Error deleting job {job_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/apis/jobs/<job_id>/execute', methods=['POST'])
def execute_job(job_id):
    """立即执行指定的定时任务"""
    try:
        config = load_schedule_config()
        job = next((job for job in config['jobs'] if job['id'] == job_id), None)
        if not job:
            return jsonify({"error": "Job not found"}), 404

        # 检查任务是否启用
        if not job.get('enabled', False):
            return jsonify({"error": "Job is disabled"}), 400

        # 根据function名称执行相应的函数
        function_map = {
            "scrape_list": scrape_list,
            "scrape_content": scrape_content,
            "scrape_ip_proxies": ipproxy.scrape_ipproxies
        }
        
        if job['function'] not in function_map:
            return jsonify({"error": "Invalid function name"}), 400
            
        try:
            # 执行任务
            function_map[job['function']](logger)
            return jsonify({"message": f"Job {job_id} executed successfully"})
        except Exception as e:
            logger.error(f"Error executing job {job_id}: {str(e)}")
            # 返回更详细的错误信息
            return jsonify({
                "error": f"执行任务失败: {str(e)}",
                "details": {
                    "job_id": job_id,
                    "function": job['function']
                }
            }), 500
            s
    except Exception as e:
        logger.error(f"Error executing job {job_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/apis/jobs/<job_id>/toggle', methods=['POST'])
def toggle_job(job_id):
    """切换任务的启用/禁用状态"""
    try:
        config = load_schedule_config()
        job = next((job for job in config['jobs'] if job['id'] == job_id), None)
        if not job:
            return jsonify({"error": "Job not found"}), 404
        
        # 切换状态
        job['enabled'] = not job.get('enabled', True)  # 默认为True
        save_schedule_config(config)
        
        return jsonify({
            "message": f"Job {job_id} {'enabled' if job['enabled'] else 'disabled'} successfully",
            "enabled": job['enabled']
        })
    except Exception as e:
        logger.error(f"Error toggling job {job_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logger.info("Starting API server...")

    # 启动子线程来定期更新缓存
    start_worker(logger, interval=600)

    app.run(debug=True, host='0.0.0.0', port=5001)
