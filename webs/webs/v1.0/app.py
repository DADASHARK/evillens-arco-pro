# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
from models.db_models import db, Video, AnalysisResult
from services.video_service import VideoService
from services.analysis_service import AnalysisService
from utils.response_util import success_response, error_response

# 配置日志
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# 允许跨域请求
CORS(app)

# 配置数据库
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///videos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# 服务初始化
video_service = VideoService()
analysis_service = AnalysisService()


# 创建数据库表
@app.before_first_request
def create_tables():
    db.create_all()


# API路由
@app.route("/api/videos", methods=["GET"])
def get_videos():
    """获取视频列表，支持分页和筛选"""
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        filter_type = request.args.get(
            "filter", None
        )  # 可能的值: all, dangerous, normal

        videos, total = video_service.get_videos(page, per_page, filter_type)

        return success_response(
            {"videos": videos, "total": total, "page": page, "per_page": per_page}
        )
    except Exception as e:
        logger.error(f"Error getting videos: {str(e)}")
        return error_response(str(e))


@app.route("/api/videos/<video_id>", methods=["GET"])
def get_video_detail(video_id):
    """获取单个视频的详细信息和分析结果"""
    try:
        video = video_service.get_video_by_id(video_id)
        if not video:
            return error_response("Video not found", 404)

        analysis = analysis_service.get_analysis_by_video_id(video_id)

        return success_response({"video": video, "analysis": analysis})
    except Exception as e:
        logger.error(f"Error getting video detail: {str(e)}")
        return error_response(str(e))


@app.route("/api/videos/analyze", methods=["POST"])
def analyze_video():
    """请求分析一个新的视频"""
    try:
        data = request.json
        video_url = data.get("video_url")

        if not video_url:
            return error_response("Video URL is required", 400)

        # 检查视频是否已经在数据库中
        existing_video = video_service.get_video_by_url(video_url)
        if existing_video:
            return success_response(
                {
                    "video_id": existing_video["id"],
                    "message": "Video already exists in database",
                    "status": "existing",
                }
            )

        # 通过队列或直接调用爬虫进行视频爬取
        video_id = video_service.request_video_crawl(video_url)

        return success_response(
            {
                "video_id": video_id,
                "message": "Video analysis requested successfully",
                "status": "processing",
            }
        )
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        return error_response(str(e))


@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    """获取系统统计数据"""
    try:
        stats = {
            "total_videos": video_service.get_total_videos(),
            "dangerous_videos": video_service.get_dangerous_videos_count(),
            "recent_additions": video_service.get_recent_additions(days=7),
            "analysis_statistics": analysis_service.get_analysis_statistics(),
        }

        return success_response(stats)
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return error_response(str(e))


@app.route("/api/videos/search", methods=["GET"])
def search_videos():
    """搜索视频"""
    try:
        query = request.args.get("q", "")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        if not query:
            return error_response("Search query is required", 400)

        videos, total = video_service.search_videos(query, page, per_page)

        return success_response(
            {"videos": videos, "total": total, "page": page, "per_page": per_page}
        )
    except Exception as e:
        logger.error(f"Error searching videos: {str(e)}")
        return error_response(str(e))


@app.route("/api/videos/<video_id>/trace", methods=["GET"])
def trace_video(video_id):
    """获取视频溯源分析结果"""
    try:
        trace_results = analysis_service.get_trace_analysis(video_id)
        if not trace_results:
            return error_response("Trace analysis not found", 404)

        return success_response(trace_results)
    except Exception as e:
        logger.error(f"Error getting trace analysis: {str(e)}")
        return error_response(str(e))


@app.route("/api/callback/crawl", methods=["POST"])
def crawl_callback():
    """爬虫完成后的回调接口"""
    try:
        data = request.json
        video_id = data.get("video_id")
        status = data.get("status")
        metadata = data.get("metadata", {})

        if not video_id or not status:
            return error_response("Invalid callback data", 400)

        # 更新视频状态
        video_service.update_video_status(video_id, status, metadata)

        # 如果爬取成功，启动检测流程
        if status == "completed":
            analysis_service.request_video_detection(video_id)

        return success_response({"message": "Callback processed successfully"})
    except Exception as e:
        logger.error(f"Error processing crawl callback: {str(e)}")
        return error_response(str(e))


@app.route("/api/callback/detection", methods=["POST"])
def detection_callback():
    """检测模型完成后的回调接口"""
    try:
        data = request.json
        video_id = data.get("video_id")
        is_dangerous = data.get("is_dangerous")
        detection_results = data.get("detection_results", {})

        if video_id is None or is_dangerous is None:
            return error_response("Invalid callback data", 400)

        # 更新检测结果
        analysis_service.update_detection_results(
            video_id, is_dangerous, detection_results
        )

        # 如果是危险视频，启动溯源分析
        if is_dangerous:
            analysis_service.request_trace_analysis(video_id)

        return success_response({"message": "Detection results saved successfully"})
    except Exception as e:
        logger.error(f"Error processing detection callback: {str(e)}")
        return error_response(str(e))


@app.route("/api/callback/analysis", methods=["POST"])
def analysis_callback():
    """分析模块完成后的回调接口"""
    try:
        data = request.json
        video_id = data.get("video_id")
        analysis_results = data.get("analysis_results", {})

        if not video_id or not analysis_results:
            return error_response("Invalid callback data", 400)

        # 更新分析结果
        analysis_service.update_analysis_results(video_id, analysis_results)

        return success_response({"message": "Analysis results saved successfully"})
    except Exception as e:
        logger.error(f"Error processing analysis callback: {str(e)}")
        return error_response(str(e))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
