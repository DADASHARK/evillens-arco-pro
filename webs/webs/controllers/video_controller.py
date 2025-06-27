# controllers/video_controller.py - 视频相关接口
from flask import Blueprint, jsonify, request
from webs.models.db import db
from webs.models.video import Video
from webs.config import Config


video_bp = Blueprint("video", __name__)


@video_bp.route("/carousel", methods=["GET"])
def get_carousel_videos():
    """获取滚动图视频数据"""
    try:
        limit = int(request.args.get("limit", Config.CAROUSEL_DEFAULT_LIMIT))
        offset = int(request.args.get("offset", 0))

        # 获取视频数据，按发布时间降序排列
        videos = (
            Video.query.order_by(Video.publish_time.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        result = []
        for video in videos:
            result.append(
                {"name": video.name, "vd_id": video.vd_id, "cover_url": video.cover_url}
            )

        return jsonify({"code": 200, "data": result})
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500
