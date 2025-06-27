from flask import Blueprint, jsonify, request
from controllers.mail_sender import send_mail_api
import logging

mail_bp = Blueprint('mail', __name__, url_prefix='/api/mail')

@mail_bp.route('/', methods=['POST'])
def trigger_mail_sender():
    """API：触发邮件发送（POST请求）"""
    try:
        # 从请求JSON中获取可选参数（如自定义zip文件名）
        req_data = request.get_json() or {}
        zip_name = req_data.get('zip_name')

        # 调用mail_sender的封装函数
        success, msg = send_mail_api(zip_name)
        
        if success:
            return jsonify({"code": 20000, "message": msg}), 200
        else:
            return jsonify({"code": 500, "message": msg}), 500
    except Exception as e:
        logging.error(f"邮件API异常: {str(e)}")
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500