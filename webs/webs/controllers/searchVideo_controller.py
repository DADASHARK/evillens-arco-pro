# controllers/searchVideo_controller.py - 视频搜索相关接口
from flask import Blueprint, jsonify, request
from datetime import datetime
from models.database import session, TopVideo

# 创建蓝图 - 确保名称为 searchVideo_bp
searchVideo_bp = Blueprint("video", __name__)


@searchVideo_bp.route("/", methods=["GET"])
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
            result.append(
                {
                    "id": str(video.vd_id),
                    "number": (
                        int(video.vd_id) if video.vd_id.isdigit() else 0
                    ),  # 或根据实际number字段
                    "name": video.vd_title,
                    "author": video.author,
                    "engagement": (
                        float(video.engagement_rate)
                        if video.engagement_rate is not None
                        else 0.0
                    ),
                    "count": video.likes if video.likes is not None else 0,
                    "status": bool(video.removed),  # True为下架，False为在线
                    "createdTime": (
                        video.create_time.strftime("%Y-%m-%d %H:%M:%S")
                        if video.create_time
                        else ""
                    ),
                }
            )

        return jsonify({"code": 20000, "data": {"list": result, "total": total}})
    except Exception as e:
        session.rollback()
        return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500
    finally:
        session.close()


# @searchVideo_bp.route("/", methods=["GET"])
# def search_videos():
#     """搜索视频数据"""
#     try:
#         # 获取分页参数
#         current = int(request.args.get("current", 1))
#         pageSize = int(request.args.get("pageSize", 10))

#         # 获取筛选参数
#         number = request.args.get("number", "")
#         name = request.args.get("name", "")

#         # 初始化查询
#         query = session.query(TopVideo)

#         # 应用筛选条件
#         if number:
#             query = query.filter(TopVideo.vd_id.like(f"%{number}%"))
#         if name:
#             query = query.filter(TopVideo.vd_title.like(f"%{name}%"))

#         # 计算总数
#         total = query.count()

#         # 分页查询
#         start = (current - 1) * pageSize
#         videos = query.offset(start).limit(pageSize).all()

#         # 构建响应数据
#         result = []
#         for video in videos:
#             result.append({
#                 "id": str(video.vd_id),  # 使用数据库的 vd_id 作为唯一标识
#                 "name": video.vd_title,
#                 "author": video.author,  # 原 "count" 字段更名为 "author" 更清晰（根据模型字段名）
#                 "likes": video.likes,  # 新增：点赞数
#                 "shares": video.shares,  # 新增：分享数
#                 "collects": video.collects,  # 新增：收藏数
#                 "engagementRate": video.engagement_rate,  # 新增：互动率（驼峰式命名）
#                 "createdTime": video.create_time.strftime("%Y-%m-%d %H:%M:%S") if video.create_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "Evil": video.evil,  # 新增：是否违规（布尔值）
#                 "Reported": video.reported,  # 新增：是否被举报（布尔值）
#                 "Removed": video.removed,  # 新增：是否被移除（布尔值）
#             })

#         return jsonify({
#             "code": 20000,
#             "data": {
#                 "list": result,
#                 "total": total
#             }
#         })
#     except Exception as e:
#         session.rollback()  # 新增：异常时回滚数据库事务
#         return jsonify({"code": 500, "message": f"服务器内部错误: {str(e)}"}), 500
#     finally:
#         session.close()  # 新增：确保关闭数据库连接
