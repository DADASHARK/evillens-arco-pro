# 认证控制器 - 处理登录请求
from flask import Blueprint, request, jsonify
from models.database import session, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({
            'code': 40000,
            'data': {
                'message': '用户名和密码不能为空'
            }
        }), 400
    
    username = data.get('username')
    password = data.get('password')
    
    user = session.query(User).filter_by(username=username).first()
    
    if user and user.check_password(password):
        # 返回符合前端格式的成功响应
        return jsonify({
            'code': 20000,
            'data': {
                'token': 'admin-token-123456',
                'user': {
                    'id': user.id,
                    'username': user.username
                }
            }
        })
    
    return jsonify({
        'code': 40001,
        'data': {
            'message': '用户名或密码错误'
        }
    }), 401