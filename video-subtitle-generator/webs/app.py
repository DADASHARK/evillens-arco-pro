# app.py - 主文件
from flask import Flask, jsonify, request
# 缓存机制库
from flask_caching import Cache
from flask_cors import CORS
import os
from config import Config
from controllers.video_controller import video_bp
from controllers.geography_controller import geography_bp
from controllers.trends_controller import trends_bp
from controllers.keywords_controller import keywords_bp
from controllers.gangs_controller import gangs_bp
from controllers.report_controller import report_bp
from controllers.simple_api_controller import simple_api_bp
from controllers.searchVideo_controller import searchVideo_bp
from controllers.mail_controller import mail_bp
# 在现有导入语句中添加
from controllers.auth_controller import auth_bp
# 添加新的检测任务控制器
from controllers.detect_controller import detect_bp
# 添加用户画像控制器
from controllers.profile_controller import profile_bp

import schedule
import time
from controllers.analysis import check_removed_videos
from config import CHECK_INTERVAL  


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # 初始化缓存
    cache = Cache()
    cache.init_app(app)
    # 允许跨域请求
    CORS(app, resources={r"/api/*": {"origins": "*", "max_age": 60}})
    # 关键：初始化数据库
    from models.db import db
    db.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(geography_bp, url_prefix='/api/geography')
    # app.register_blueprint(video_bp, url_prefix='/api/video')
    app.register_blueprint(trends_bp, url_prefix='/api/trends')
    app.register_blueprint(keywords_bp, url_prefix='/api/keywords')
    app.register_blueprint(gangs_bp, url_prefix='/api/gangs')
    app.register_blueprint(report_bp, url_prefix='/api/report')
    app.register_blueprint(simple_api_bp, url_prefix="/api")
    app.register_blueprint(searchVideo_bp, url_prefix="/api/video")
    app.register_blueprint(mail_bp, url_prefix='/api/mail')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # 注册检测任务蓝图
    app.register_blueprint(detect_bp, url_prefix='/api/detect')
     # 注册用户画像蓝图
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    
    
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "ok", "message": "服务正常运行"})
    
    return app


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
