# controllers/gangs_controller.py - 团伙分析相关接口
from flask import Blueprint, jsonify
from models.db import db
from models.gang import Gang
from models.cross_platform_account import CrossPlatformAccount

gangs_bp = Blueprint("gangs", __name__)


@gangs_bp.route("", methods=["GET"])
def get_gangs():
    """获取团伙列表"""
    try:
        gangs = Gang.query.all()

        result = []
        for gang in gangs:
            result.append(gang.to_dict())

        return jsonify({"code": 200, "data": result})
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500


@gangs_bp.route("/<string:gang_id>", methods=["GET"])
def get_gang_detail(gang_id):
    """获取团伙详情"""
    try:
        gang = Gang.query.filter_by(gang_id=gang_id).first()

        if not gang:
            return jsonify({"code": 404, "message": "未找到该团伙"}), 404

        return jsonify({"code": 200, "data": gang.to_detail_dict()})
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500
