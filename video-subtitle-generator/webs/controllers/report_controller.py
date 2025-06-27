# controllers/report_controller.py - 报告相关接口
from flask import Blueprint, jsonify
import os
from config import OUTPUT_DIR  # 从配置文件导入输出目录
from .report_generator import generate_report  # 新增：导入生成报告函数
from models.database import TopVideo as Video  # 新增：导入视频模型
from models.database import session  # 新增：导入数据库会话
from sqlalchemy import func 
from models.db import db  # 新增：导入数据库会话
import pandas as pd  # 新增：用于数据转换


report_bp = Blueprint("report", __name__)
@report_bp.route("/", methods=["GET"])  # 修改：调整接口路径
def get_num():
    """获取治理报告统计数据"""
    try:
        # 1. 基础统计数据（修复 count 方法调用）
        total_videos = session.query(Video).count()  # 正确：执行 count 方法获取数值
        key_users = db.session.query(func.count(Video.author.distinct())).scalar()  # 关键用户数（去重作者数）

        # 2. 互动数据统计
        engagement_data = db.session.query(
            func.sum(Video.likes).label('total_likes'),  # 总点赞
            func.sum(Video.shares).label('total_share'),    # 平均点赞
            func.sum(Video.collects).label('total_collect')  # 总评论（假设存在comments字段）
        ).first()

        # 3. 操作数据统计
        actions_data = db.session.query(
            func.count(Video.reported).filter(Video.reported == True).label('reported'),  # 已举报数
            func.count(Video.removed).filter(Video.removed == True).label('removed')      # 已移除数（假设存在removed字段）
        ).first()

        # 构造响应数据
        response_data = {
            "total_videos": total_videos,
            "key_users": key_users,
            "engagement": {
                "total_likes": engagement_data.total_likes or 0,
                "total_share": engagement_data.total_share or 0,
                "total_collect": engagement_data.total_collect or 0,
            },
            "actions": {
                "reported": actions_data.reported or 0,
                "removed": actions_data.removed or 0
            }
        }

        return jsonify({
            "code": 20000,  # 修改：符合示例状态码
            "data": response_data
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500

@report_bp.route("/gen_report", methods=["POST"])
def get_report():
    """获取Markdown报告内容（先生成报告再返回）"""
    try:
        # 1. 调用生成报告（假设已包含数据查询逻辑）
        generate_report()  # 若需要传参，根据实际情况补充参数（如 data）

        # 2. 读取生成的报告文件（示例路径，根据实际配置调整）
        report_path = os.path.join(OUTPUT_DIR, "evidence_report.md")
        if not os.path.exists(report_path):
            return jsonify({"code": 404, "message": "报告文件未生成"}), 404

        # 3. 读取报告内容并传递到前端
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()

        return jsonify({
            "code": 20000,
            "data": {
                "content": report_content,
                "path": report_path
            }
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500
