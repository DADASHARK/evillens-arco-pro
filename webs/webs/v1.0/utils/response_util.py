# utils/response_util.py
from flask import jsonify


def success_response(data=None, message="Success", status_code=200):
    """
    生成成功响应

    Args:
        data: 响应数据
        message: 成功消息
        status_code: HTTP状态码

    Returns:
        flask.Response: JSON响应
    """
    response = {"status": "success", "message": message}

    if data is not None:
        response["data"] = data

    return jsonify(response), status_code


def error_response(message="Error", status_code=400):
    """
    生成错误响应

    Args:
        message: 错误消息
        status_code: HTTP状态码

    Returns:
        flask.Response: JSON响应
    """
    response = {"status": "error", "message": message}

    return jsonify(response), status_code
