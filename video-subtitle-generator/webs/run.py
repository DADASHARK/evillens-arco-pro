# run.py - 运行脚本
from app import create_app
from models.db import db
from file_watcher import start_watcher
from controllers.analysis import check_removed_videos  # 新增：导入检查函数
import schedule
import time
import threading
from config import CHECK_INTERVAL  # 新增：导入检查间隔配置



app = create_app()

# 在应用上下文中初始化数据库
with app.app_context():
    # db.init_app(app)
    db.create_all()

# 启动文件监控服务（后台线程）
watcher_thread = threading.Thread(target=start_watcher, daemon=True)
watcher_thread.start()

# 新增：定时任务逻辑（后台线程）
def run_scheduler():
    # 启动时立即执行一次检查
    check_removed_videos()
    # 配置定时任务（每CHECK_INTERVAL分钟执行一次）
    schedule.every(CHECK_INTERVAL).minutes.do(check_removed_videos)
    # 运行定时任务循环
    while True:
        schedule.run_pending()
        time.sleep(1)

# 启动定时任务线程（后台运行）
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8080)