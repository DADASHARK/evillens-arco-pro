# controllers/searchVideo_controller.py - 视频搜索相关接口
from flask import Blueprint, jsonify, request
from datetime import datetime
from models.database import session, TopVideo  

# 创建蓝图 - 确保名称为 searchVideo_bp
searchVideo_bp = Blueprint("video", __name__)

@searchVideo_bp.route("", methods=["GET","OPTIONS"])
@searchVideo_bp.route("/", methods=["GET","OPTIONS"])
def search_videos():
    try:
        current = int(request.args.get("current", 1))
        pageSize = int(request.args.get("pageSize", 10))
        number = request.args.get("number", "")
        name = request.args.get("name", "")

        query = session.query(TopVideo)
        if number:
            query = query.filter(TopVideo.vd_id.like(f"%{number}%"))
        if name:
            query = query.filter(TopVideo.vd_title.like(f"%{name}%"))
        total = query.count()
        start = (current - 1) * pageSize
        videos = query.offset(start).limit(pageSize).all()

        result = []
        for video in videos:
            result.append({
                "id": str(video.vd_id),
                "number": int(video.vd_id) if video.vd_id.isdigit() else 0,  # 或根据实际number字段
                "name": video.vd_title,
                "author": video.author,
                "engagement": float(video.engagement_rate) if video.engagement_rate is not None else 0.0,
                "count": video.likes if video.likes is not None else 0,
                "status": bool(video.removed),  # True为下架，False为在线
                "createdTime": video.create_time.strftime("%Y-%m-%d %H:%M:%S") if video.create_time else "",
            })

        return jsonify({
            "code": 20000,
            "data": {
                "list": result,
                "total": total
            }
        })
    except Exception as e:
        session.rollback()
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500
    finally:
        session.close()