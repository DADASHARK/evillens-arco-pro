# controllers/keywords_controller.py - 关键词分析相关接口
from flask import Blueprint, jsonify
from models.db import db
from models.keyword import Keyword
from models.video import Video
from models import TagFrequency  # 新增：导入词频模型
from models.video_keyword import video_keyword
from models.database import TagVideoMapping, session  # 新增：导入session

keywords_bp = Blueprint("keywords", __name__)


@keywords_bp.route("", methods=["GET"])
def get_keywords():
    """获取关键词云（基于tag_frequency表）"""
    try:
        # 从tag_frequency表查询所有关键词及频率
        tag_freqs = TagFrequency.query.all()
        
        # 计算总频率
        total_frequency = sum(tf.frequency for tf in tag_freqs)
        
        result = []
        for tf in tag_freqs:
            # 计算百分比
            percentage = f"{round((tf.frequency / total_frequency) * 100,2)}%"
            result.append({
                "keyword": tf.tag,  # 关键词字段名假设为tag
                "percentage": percentage  # 新增百分比字段
            })

        return jsonify({"code": 20000, "data": result})
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500


@keywords_bp.route("<keyword>/videos", methods=["GET"])
def get_videos_by_keyword(keyword):
    """根据关键词获取视频ID列表"""
    try:
        # 使用session.query()替代TagVideoMapping.query
        mappings = session.query(TagVideoMapping).filter_by(tag=keyword).all()  # 关键修改
        
        # 提取所有vd_id
        video_ids = [mapping.vd_id for mapping in mappings]
        
        return jsonify({
            "code": 200,
            "data": {
                "keyword": keyword,
                "video_ids": video_ids,
                "count": len(video_ids)
            }
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500