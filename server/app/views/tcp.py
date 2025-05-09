from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.tcp_service import TCPServerThread, clients, runtime_logs

tcp_bp = Blueprint('tcp', __name__)
tcp_thread = None


@tcp_bp.route('/tcp/start', methods=['POST'])
@jwt_required()
def start_tcp_server():
    global tcp_thread
    if tcp_thread is None or not tcp_thread.is_alive():
        try:
            tcp_thread = TCPServerThread()
            tcp_thread.start()
            return jsonify({'msg': 'TCP 透传服务已启动'})
        except RuntimeError as e:
            return jsonify({'msg': str(e)}), 400
    return jsonify({'msg': '服务已经在运行中'})


@tcp_bp.route('/tcp/status', methods=['GET'])
@jwt_required()
def tcp_status():
    return jsonify({
        'online_devices': list(clients.keys()),
        'logs': runtime_logs[-50:]  # 只返回本次运行期间的最近 50 条日志
    })


@tcp_bp.route('/clear_logs', methods=['POST'])
@jwt_required()
def clear_logs():
    runtime_logs.clear()
    return jsonify({"message": "已清除log"}), 200
