from flask import Blueprint, render_template

bp = Blueprint('view', __name__,  url_prefix='/')

@bp.route('/')
def index():
    return render_template('articles.html', active_page='articles')

@bp.route('/jobs')
def get_jobs_page():
    return render_template('jobs.html', active_page='jobs')

@bp.route('/joblogs')
def get_joblogs_page():
    return render_template('joblogs.html')

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