import os
import sys
import csv
import time
import argparse
import threading
import logging
from scrapy.utils.log import configure_logging

configure_logging(install_root_handler=False)
logging.basicConfig(level=logging.WARNING)
logging.getLogger("scrapy").setLevel(logging.WARNING)
logging.getLogger("seleniumwire").setLevel(logging.WARNING)
from threading import Event

# from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings
# from crawler.douyin_video.auto_process import auto_process_video
# from detector.main import start_detect
from utils.detect import crawler_and_detect
import pandas as pd
from crawler.recommend.recommend import process_evil_videos
from crawler.explore.new_pipline1 import main_explore
from webs.run import start_app


def update_time_csv_and_get_active_csv_path(base_search_results):
    """
    从给定的 base_search_results 目录下的 time.csv 中查找状态为 "0" 的记录，
    并更新该记录状态为 "1"，然后返回以记录时间戳为前缀的 CSV 文件完整路径。

    参数:
        base_search_results: str 类型, CSV 文件所在的目录（同时包含 time.csv 文件）
                           例如 r"D:\Documents\VSCode\minor_protection\to_use\crawler\douyin_video\search_results\results"

    返回:
        csv_file_path: 以查找到的时间前缀命名的 CSV 文件路径，
                       例如 r"D:\...\results\2025-05-06-10.csv"

    如果未找到状态为 "0" 的记录，则抛出 Exception。
    """
    time_csv_path = os.path.join(base_search_results, "time.csv")

    active_time = None

    # 1. 读取 time.csv 中状态为 "0" 的记录
    with open(time_csv_path, "r", encoding="utf-8", newline="") as f_time:
        reader = csv.reader(f_time)
        header = next(reader)  # 第一行是表头 ["time", "status"]
        for row in reader:
            if active_time is None and row[1] == "0":
                active_time = row[0]
                break

    if active_time is None:
        raise Exception("未找到状态为0的时间记录，请检查 time.csv 文件。")

    # 2. 更新 time.csv，将该行状态修改为 "1"
    updated_rows = []
    updated = False
    with open(time_csv_path, "r", encoding="utf-8", newline="") as f_time:
        reader = csv.reader(f_time)
        header = next(reader)
        updated_rows.append(header)
        for row in reader:
            if not updated and row[0] == active_time and row[1] == "0":
                updated_rows.append([row[0], "1"])
                updated = True
            else:
                updated_rows.append(row)
    with open(time_csv_path, "w", encoding="utf-8", newline="") as f_time:
        writer = csv.writer(f_time)
        writer.writerows(updated_rows)

    return active_time


def save_evil_csv(csv_path, evil_video_ids, active_time):
    """
    根据 evil_video_ids 列表，从 csv_path 指定的 CSV 文件中过滤出对应的行，
    并将结果保存为 evil_(active_time).csv 文件，保存路径与 csv_path 同一目录下。

    :param csv_path: 输入 CSV 文件路径
    :param evil_video_ids: 视频 ID 列表，用于作为过滤条件
    :param active_time: 字符串格式的活动时间，用作新文件名的一部分
    :return: 保存的 CSV 文件路径
    """
    # 1. 读取 CSV 文件数据
    df = pd.read_csv(csv_path)

    # 2. 筛选出含有指定视频ID的行
    filtered_df = df[df["vd_id"].isin(evil_video_ids)]

    # 3. 保存当前时间段的 evil CSV 文件（例如：evil_2025-05-16-20.csv）
    output_filename = f"evil_{active_time}.csv"
    output_path = os.path.join(os.path.dirname(csv_path), output_filename)
    filtered_df.to_csv(output_path, index=False)

    # 4. 更新全量文件 evil_all.csv 的内容
    #    根据要求，evil_all.csv 的字段对应关系为：
    #       vd_id            -> vd_id
    #       vd_title         -> vd_title
    #       create_time      -> create_time
    #       author_nickname  -> author   (author_uid 和 enterprise_verify 均跳过)
    #       likes            -> likes
    #       shares           -> shares
    #       collects         -> collects
    #       img_url          -> img_url
    #
    # 因此，我们从 filtered_df 中选取所需的字段，并将 "author_nickname" 重命名为 "author"
    required_columns = [
        "vd_id",
        "vd_title",
        "create_time",
        "author_nickname",
        "likes",
        "shares",
        "collects",
        "img_url",
    ]
    evil_all_df = filtered_df[required_columns].rename(
        columns={"author_nickname": "author"}
    )

    # 定义全量文件的路径（根据需求填写具体的路径）
    evil_all_csv_path = r"D:\Documents\VSCode\minor_protection\to_use\crawler\explore\search_results\evil_all.csv"

    # 5. 将数据追加到 evil_all.csv 的尾部
    #    如果文件已存在，则以追加模式写入，并且不需要写表头；
    #    如果文件不存在，则新建文件并写入表头
    if os.path.exists(evil_all_csv_path):
        evil_all_df.to_csv(evil_all_csv_path, mode="a", header=False, index=False)
    else:
        evil_all_df.to_csv(evil_all_csv_path, mode="w", header=True, index=False)

    return output_path


def run(periodic=True):
    start_app()
    threading.Thread(target=start_app, daemon=True).start()

    if periodic:
        base_search_results = r"D:\Documents\VSCode\minor_protection\to_use\crawler\explore\search_results\results"
        active_time = update_time_csv_and_get_active_csv_path(base_search_results)
        csv_file_path = os.path.join(base_search_results, active_time + ".csv")

        # 测试
        # active_time = "2025-05-16-20"
        # csv_file_path = r"D:\Documents\VSCode\minor_protection\to_use\crawler\explore\search_results\results\round2_global_search_results.csv"

        evil_video_ids = crawler_and_detect(csv_file_path, active_time)

        # 根据evil_video_ids筛选 CSV 中的行，并保存到evil_(active_time).csv文件中
        evil_csv_path = save_evil_csv(csv_file_path, evil_video_ids, active_time)
        print(f"Evil CSV file saved to: {evil_csv_path}")

        # --- 调用推荐处理函数，对 evil_video_ids 进行点赞收藏操作 ---
        if evil_video_ids:
            print("开始对 evil_video_ids 视频执行点赞与收藏操作...")
            process_evil_videos(evil_video_ids)
        else:
            print("无需要处理的新视频。")

        # 发现新视频
        main_explore()


if __name__ == "__main__":
    periodic = False  # 是否开启定时自动搜寻视频任务
    start_time = time.time()
    print(f"start_time: {start_time}")
    run(periodic)
    end_time = time.time()
    print(f"end_time: {end_time}")
    print(f"total time: {end_time - start_time}")
