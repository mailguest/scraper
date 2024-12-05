from flask import Blueprint, jsonify, request, current_app
from services.job_service import load_schedule_config, save_schedule_config
from scripts.scrape_list import scrape as scrape_list
from scripts.scrape_content import scrape_all_articles
import scripts.scrape_ipproxy as ipproxy


bp = Blueprint('job', __name__, url_prefix='/apis/jobs')

@bp.route('/', methods=['GET'])
def get_jobs():
    """获取所有定时任务"""
    logger = current_app.config['logger']
    try:
        config = load_schedule_config()
        return jsonify(config['jobs'])
    except Exception as e:
        logger.error(f"Error getting jobs: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/<job_id>', methods=['GET'])
def get_job(job_id):
    """获取特定定时任务"""
    logger = current_app.config['logger']
    try:
        config = load_schedule_config()
        job = next((job for job in config['jobs'] if job['id'] == job_id), None)
        if not job:
            return jsonify({"error": "Job not found"}), 404
        return jsonify(job)
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/', methods=['POST'])
def create_job():
    """创建新的定时任务"""
    logger = current_app.config['logger']
    try:
        new_job = request.get_json()
        if not hasattr(new_job, "id"):
            return jsonify({"error": "无效的任务数据"}), 400

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

@bp.route('/<job_id>', methods=['PUT'])
def update_job(job_id):
    """更新定时任务"""
    logger = current_app.config['logger']
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

@bp.route('/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """删除定时任务"""
    logger = current_app.config['logger']
    try:
        config = load_schedule_config()
        config['jobs'] = [job for job in config['jobs'] if job['id'] != job_id]
        save_schedule_config(config)
        return '', 204
    except Exception as e:
        logger.error(f"Error deleting job {job_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/<job_id>/execute', methods=['POST'])
def execute_job(job_id):
    """立即执行指定的定时任务"""
    logger = current_app.config['logger']
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
            "scrape_content": scrape_all_articles,
            "scrape_ip_proxies": ipproxy.scrape_ipproxies
        }
        
        if job['function'] not in function_map:
            return jsonify({"error": "Invalid function name"}), 400
            
        try:
            # 执行任务
            func = function_map[job['function']]
            logger.info(f"Executing job {job_id} with function: {func.__name__}")
            func(logger, db=current_app.config['db'])
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

@bp.route('/<job_id>/toggle', methods=['POST'])
def toggle_job(job_id):
    """切换任务的启用/禁用状态"""
    logger = current_app.config['logger']
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

@bp.route('/logs', methods=['GET'])
def get_logs():
    """
    获取任务日志列表
    Returns:
        {
            'total': 990,
            'items': list[dict],
            'page': 1,
            'size': 10,
            'total_pages': 99
        }
    """
    tasklogs_mapper = current_app.config['tasklogs_mapper']

    # 获取查询参数 page, limit 和 date，设置默认值
    page = int(request.args.get('page', 1))  # 默认为第一页
    size = int(request.args.get('size', 10))  # 默认为每页 10 条数据
    task_name = request.args.get('taskName', None)
    status = request.args.get('status', None)
    
    data = tasklogs_mapper.get_task_logs(page=page, size=size, task_name=task_name, status=status)
    return jsonify(data)
    