# run.py - 运行脚本
from .app import create_app
from .models.db import db
from .file_watcher import start_watcher
from .controllers.analysis import check_removed_videos
import schedule
import time
import threading
from .config import CHECK_INTERVAL

# from .app import app


def start_app(
    host="127.0.0.1", port=8080, debug=False, enable_file_watcher=False
):  # 新增 enable_file_watcher 参数
    # 创建应用实例
    app = create_app()

    # 在应用上下文中初始化数据库
    with app.app_context():
        db.init_app(app)
        db.create_all()

    # 启动文件监控服务（后台线程）- 新增条件判断
    if enable_file_watcher:
        threading.Thread(target=start_watcher, daemon=True).start()

    # 启动定时任务线程（后台运行）
    def run_scheduler():
        check_removed_videos()
        schedule.every(CHECK_INTERVAL).minutes.do(check_removed_videos)
        while True:
            schedule.run_pending()
            time.sleep(1)

    threading.Thread(target=run_scheduler, daemon=True).start()

    # 启动Flask应用
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    start_app()  # 保持原有调用方式（默认开启文件监听）
    # 若要关闭文件监听，可调用 start_app(enable_file_watcher=False)
