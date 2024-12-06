from flask import Blueprint, jsonify, current_app
import scripts.scrape_ipproxy as ipproxy

bp = Blueprint('proxy', __name__, url_prefix='/apis')

@bp.route('/proxies')
def get_proxies():
    # logger = current_app.config['logger']
    logger = current_app.logger
    try:
        proxies = ipproxy.get_proxies(logger)
        return jsonify(proxies)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/proxies/refresh', methods=['POST'])
def refresh_proxies():
    # logger = current_app.config['logger']
    logger = current_app.logger
    try:
        ipproxy.scrape_ipproxies(logger)
        return jsonify({"message": "代理列表已更新"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/proxies/<path:ip>/test', methods=['POST'])
def test_and_flush_proxy(ip):
    # logger = current_app.config['logger']
    logger = current_app.logger
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

@bp.route('/proxies/<path:ip>', methods=['DELETE'])
def delete_proxy(ip):
    # logger = current_app.config['logger']
    logger = current_app.logger
    try:
        logger.info(f"删除代理: {ip}")
        ipproxy.delete(ipproxy.IpProxy(ip.split(':')[0], ip.split(':')[1], '', ''))
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500