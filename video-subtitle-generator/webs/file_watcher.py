import time
import logging
import traceback  # 新增：用于获取堆栈跟踪
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from controllers.analysis import load_data, store_to_database
from config import SOURCE_DIR 
import os  # 新增：用于文件操作
from controllers.analysis import generate_word_frequency, generate_tag_video_mapping, extract_similar_users
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class CSVHandler(FileSystemEventHandler):
    def on_created(self, event):
        """当检测到新文件创建时触发"""
        if event.is_directory:
            return
        # 修改：支持大小写后缀（.csv/.CSV）
        if event.src_path.lower().endswith('.csv'):
            logger.info(f"检测到新CSV文件: {event.src_path}")
            try:
                # 新增处理前文件检查
                if not os.path.exists(event.src_path):
                    return
                
                data = load_data(event.src_path)
                store_to_database(data)
                generate_word_frequency(data)
                generate_tag_video_mapping(data)
                #similar_users = extract_similar_users(df)
                # 新增：处理完成后移动文件到processed目录
                processed_dir = os.path.join(SOURCE_DIR, 'processed')
                os.makedirs(processed_dir, exist_ok=True)
                os.rename(event.src_path, os.path.join(processed_dir, os.path.basename(event.src_path)))
                
                logger.info(f"文件 {event.src_path} 处理完成并已移动")
            except Exception as e:
                logger.error(f"处理失败: {str(e)}\n{traceback.format_exc()}")

def start_watcher():
    """启动文件监控服务"""
    event_handler = CSVHandler()
    observer = Observer()
    observer.schedule(event_handler, path=SOURCE_DIR, recursive=False)
    observer.start()
    logger.info(f"开始监控文件夹: {SOURCE_DIR}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()