import time
import logging
import traceback
import json  # 新增：用于解析JSON文件
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .controllers.analysis import (
    load_data,
    store_to_database,
    generate_word_frequency,
    generate_tag_video_mapping,
)
from .config import SOURCE_DIR
import os

from .models.database import (
    session,
    MaliciousUser,
)  # 新增：导入恶意用户模型和数据库会话（假设已定义MaliciousUser）

logging.basicConfig(
    # level=logging.INFO,
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class CSVHandler(FileSystemEventHandler):
    def on_created(self, event):
        """当检测到新文件创建时触发"""
        if event.is_directory:
            return

        # 支持CSV和JSON文件（修改点1）
        file_path = event.src_path.lower()
        if file_path.endswith((".csv", ".json")):  # 同时监听两种文件类型
            logger.info(f"检测到新文件: {event.src_path}")
            try:
                if not os.path.exists(event.src_path):
                    return

                # 区分CSV和JSON处理（修改点2）
                if file_path.endswith(".csv"):
                    # 原有CSV处理逻辑
                    data = load_data(event.src_path)
                    store_to_database(data)
                    generate_word_frequency(data)
                    generate_tag_video_mapping(data)
                elif file_path.endswith(".json"):
                    # 新增JSON处理逻辑（修改点3）
                    json_data = self.load_json_data(event.src_path)  # 加载JSON数据
                    self.process_json_data(json_data)  # 处理JSON数据

                # 统一移动处理完成的文件（修改点4）
                processed_dir = os.path.join(SOURCE_DIR, "processed")
                os.makedirs(processed_dir, exist_ok=True)
                target_path = os.path.join(
                    processed_dir, os.path.basename(event.src_path)
                )
                os.rename(event.src_path, target_path)
                logger.info(f"文件 {event.src_path} 处理完成并已移动至 {target_path}")
            except Exception as e:
                logger.error(f"处理失败: {str(e)}\n{traceback.format_exc()}")

    def load_json_data(self, file_path):
        """加载并解析JSON文件（新增函数）"""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def process_json_data(self, json_data):
        """处理JSON数据并存储到数据库（新增函数）"""
        try:
            # 1. 存储用户信息到MaliciousUser表（假设已定义）
            user_info = json_data.get("user_info", {})
            if user_info:
                new_user = MaliciousUser(
                    user_id=user_info.get("user_id"),
                    user_name=user_info.get("user_name"),
                    age=user_info.get("age", ""),
                    follow_count=user_info.get("follow_count", 0),
                    fans_count=user_info.get("fans_count", 0),
                    like_count=user_info.get("like_count", 0),
                    douyin_id=user_info.get("douyin_id"),
                    ip_location=user_info.get("ip_location", ""),
                    self_description=user_info.get("self_description", ""),
                )
                session.add(new_user)
                logger.info(f"用户 {user_info.get('user_id')} 信息已存入数据库")

            # 2. 存储视频信息到TopVideo表（复用analysis.py的逻辑）
            videos = json_data.get("videos", [])
            if videos:
                import pandas as pd

                # 将videos列表转为DataFrame（格式需与CSV处理后的data一致）
                video_df = pd.DataFrame(videos)
                # 补充缺失字段（与TopVideo表结构对齐）
                if "video_id" in video_df.columns and "vd_id" not in video_df.columns:
                    video_df["vd_id"] = video_df["video_id"]
                if "title" in video_df.columns and "vd_title" not in video_df.columns:
                    video_df["vd_title"] = video_df["title"]
                # video_df["author"] = video_df["author"]
                # video_df["author"] = json_data.get("user_info", {}).get(
                #     "user_name", ""
                # )  # 从user_info获取作者
                if "likes" not in video_df.columns:
                    video_df["likes"] = 0  # 默认0（无点赞数据）
                if "shares" not in video_df.columns:
                    video_df["shares"] = 0  # 默认0（无点赞数据）
                if "collects" not in video_df.columns:
                    video_df["collects"] = 0  # 默认0（无收藏数据）
                if "engagement_rate" not in video_df.columns:
                    video_df["engagement_rate"] = 0.0
                if "evil" not in video_df.columns:  # 新增字段
                    video_df["evil"] = True
                if "reported" not in video_df.columns:  # 新增字段
                    video_df["reported"] = False
                if "removed" not in video_df.columns:
                    video_df["removed"] = False
                if "create_time" not in video_df.columns:
                    video_df["create_time"] = pd.to_datetime("now")
                else:
                    video_df["create_time"] = pd.to_datetime(
                        video_df["create_time"],
                        format="%Y-%m-%d %H:%M:%S",
                        errors="coerce",  # 将解析失败的值转为NaT
                    )
                if (
                    "cover_img" in video_df.columns
                    and "img_url" not in video_df.columns
                ):
                    video_df["img_url"] = video_df["cover_img"]
                video_df["tags"] = video_df["video_label"]  # 标签列表

                # 调用现有函数存储视频数据并更新标签
                # store_to_database(video_df)
                # generate_word_frequency(video_df)
                # generate_tag_video_mapping(video_df)
                print(video_df)
                logger.info(f"成功存储 {len(videos)} 条视频信息到数据库")

            session.commit()  # 提交事务
        except Exception as e:
            session.rollback()
            logger.error(f"JSON数据处理失败: {str(e)}")


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


if __name__ == "__main__":
    file_path = r"D:\Documents\VSCode\minor_protection\to_use\test\taskid_round_1.json"
    event_handler = CSVHandler()
    data = event_handler.load_json_data(file_path)
    event_handler.store_to_database(data)
