from flask import Blueprint, render_template
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

bp = Blueprint('view', __name__, 
               url_prefix='/', 
               static_url_path='/static',  # 确保这个路径正确
               static_folder=os.path.join(BASE_DIR, 'static'),  # 使用绝对路径
               template_folder=os.path.join(BASE_DIR, 'templates')
)

@bp.route('/')
def index():
    return get_jobs_page()

@bp.route('/jobs')
def get_jobs_page():
    return render_template('jobs.html', active_page='jobs')

@bp.route('/proxy')
def proxy_page():
    return render_template('proxy.html', active_page='proxy')

@bp.route('/articles')
def article_page():
    return render_template('articles.html', active_page='articles')

@bp.route('/dictionary')
def dictionary_page():
    return render_template('dictionary.html', active_page='dictionary')

@bp.route('/playground')
def playground_page():
    return render_template('playground.html', active_page='playground')