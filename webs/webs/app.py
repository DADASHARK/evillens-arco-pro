# app.py - 主文件
from flask import Flask, jsonify, request

# 缓存机制库
from flask_caching import Cache  # Ensure this import exists
from flask_cors import CORS
import os
from webs.config import Config, CHECK_INTERVAL
from webs.controllers.video_controller import video_bp
from webs.controllers.geography_controller import geography_bp  # 导入地理分布蓝图
from webs.controllers.trends_controller import trends_bp
from webs.controllers.keywords_controller import keywords_bp
from webs.controllers.gangs_controller import gangs_bp
from webs.controllers.report_controller import report_bp  # 导入报告蓝图
from webs.controllers.simple_api_controller import simple_api_bp
from webs.controllers.searchVideo_controller import searchVideo_bp
from webs.controllers.mail_controller import mail_bp  # 新增导入
from webs.controllers.task_controller import tasks_bp
import schedule
import time
from webs.controllers.analysis import check_removed_videos
# 在现有导入语句中添加
from controllers.auth_controller import auth_bp
from config import CHECK_INTERVAL  


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # 初始化缓存 - 新增缓存实例创建
    cache = Cache()  # Add this line to create the cache instance
    cache.init_app(app)  # Now 'cache' is properly defined

    # 允许跨域请求
    CORS(app, resources={r"/api/*": {"origins": "*", "max_age": 60}})

    # 注册蓝图
    # app.register_blueprint(video_bp, url_prefix="/api/videos")
    # 注册地理分布接口（必须添加）
    app.register_blueprint(geography_bp, url_prefix="/api/geography")
    app.register_blueprint(trends_bp, url_prefix="/api/trends")
    app.register_blueprint(keywords_bp, url_prefix="/api/keywords")
    app.register_blueprint(gangs_bp, url_prefix="/api/gangs")
    app.register_blueprint(
        report_bp, url_prefix="/api/report"
    )  # 注册蓝图，接口路径为 /api/report
    app.register_blueprint(simple_api_bp, url_prefix="/api")
    app.register_blueprint(searchVideo_bp, url_prefix="/api/video")
    app.register_blueprint(mail_bp, url_prefix="/api/mail")
    app.register_blueprint(tasks_bp, url_prefix="/api/detect")

    # 在注册其他蓝图的地方添加
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    @app.route("/routes")
    def list_routes():
        import json

        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(
                {
                    "endpoint": rule.endpoint,
                    "methods": list(rule.methods),
                    "path": str(rule),
                }
            )
        return json.dumps(routes, indent=2)

    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"code": 404, "message": "资源未找到"}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"code": 400, "message": "无效参数"}), 400

    @app.route("/")
    def index():
        return jsonify({"message": "欢迎使用邪典视频治理平台API"})

    return app


# app = create_app()

if __name__ == "__main__":
    app = create_app()
    # 启动时立即执行一次检查
    check_removed_videos()

    # 配置定时任务（每CHECK_INTERVAL分钟执行一次）
    schedule.every(CHECK_INTERVAL).minutes.do(check_removed_videos)

    # 运行定时任务循环
    while True:
        schedule.run_pending()
        time.sleep(1)
    app.run(debug=True, host="127.0.0.1", port=8080)
