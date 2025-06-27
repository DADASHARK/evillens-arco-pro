# 数据分析模块
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from webs.models.db import db
from datetime import datetime
from config import IMAGE_DIR  # 导入图像目录
from ..utils import download_image  # 导入下载图片函数
from webs.models.tag_frequency import *
import os
import json
import traceback

# 从数据库模块导入会话和模型
from webs.models.database import (
    session,
    AccountStat,
    TopVideo,
    HourlyDistribution,
    DailyDistribution,
    InteractionCorrelation,
    SimilarUser,
    TagVideoMapping,
    MaliciousUser,
)
from webs.models.task import DetectionResult
import requests
from webs.config import SOURCE_DIR
import math


def parse_date(date_str):
    """Convert string to datetime object"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def load_data(file_path):
    """数据加载与清洗"""
    data = pd.read_csv(file_path)

    # 修改时间解析逻辑
    data["create_time"] = pd.to_datetime(
        data["create_time"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce",  # 将解析失败的值转为NaT
    )

    valid_data = data.copy()

    # 新增时区处理（保持原有列不变）
    valid_data["hour_of_day"] = valid_data["create_time"].dt.hour
    valid_data["day_of_week"] = valid_data["create_time"].dt.day_name().fillna("未知")

    # 修复空值处理：填充空标题为空白字符串
    valid_data["tags"] = (
        valid_data["vd_title"].fillna("").str.findall(r"#([^#\s]+)").apply(set)
    )

    valid_data["image_path"] = valid_data.apply(
        lambda x: os.path.join(IMAGE_DIR, f"{x['vd_id']}.jpg"), axis=1
    )

    # 下载图片（根据需求启用）
    valid_data["image_downloaded"] = valid_data.apply(
        lambda x: download_image(x["img_url"], x["image_path"]), axis=1
    )

    # 计算互动率（保留原有逻辑）
    if "followers" in valid_data.columns:
        valid_data["engagement_rate"] = valid_data["likes"] / valid_data["followers"]
    else:
        valid_data["engagement_rate"] = np.nan

    # 时间特征提取添加空值保护
    valid_data["hour_of_day"] = valid_data["create_time"].dt.hour.where(
        valid_data["create_time"].notna(), np.nan
    )
    valid_data["day_of_week"] = (
        valid_data["create_time"]
        .dt.day_name()
        .where(valid_data["create_time"].notna(), "未知")
    )

    print(f"数据加载完成：共加载{len(valid_data)}条记录")
    return valid_data


def generate_word_frequency(data):
    """生成标签词频统计并存储到数据库（增量模式）"""
    all_tags = [tag for tags in data["tags"] for tag in tags]
    word_freq = pd.Series(all_tags).value_counts()
    # 修改为增量更新逻辑
    for word, freq in word_freq.items():
        # 检查是否已有该标签记录
        existing = session.query(TagFrequency).filter_by(tag=word).first()
        if existing:
            existing.frequency += int(freq)  # 累加计数
        else:
            session.add(TagFrequency(tag=word, frequency=int(freq)))
    session.commit()
    print("✅ 词频统计已更新到数据库（增量模式）")


def extract_similar_users(data, min_videos=3, top_n=5):
    """提取相似用户"""
    author_counts = data["author"].value_counts()
    valid_authors = author_counts[author_counts >= min_videos].index
    valid_data = data[data["author"].isin(valid_authors)]

    # 构建时间分布矩阵
    hourly_dist = (
        valid_data.groupby(["author", "hour_of_day"]).size().unstack(fill_value=0)
    )
    hourly_dist = hourly_dist.div(hourly_dist.sum(axis=1), axis=0)
    authors = hourly_dist.index.tolist()

    # 构建名称特征
    name_vec = TfidfVectorizer(analyzer="char", ngram_range=(2, 3))
    name_features = name_vec.fit_transform(authors)

    # 计算相似度
    time_sim = cosine_similarity(hourly_dist)
    name_sim = cosine_similarity(name_features)
    combined_sim = (time_sim + name_sim) / 2

    sim_df = pd.DataFrame(combined_sim, index=authors, columns=authors)
    similar_users = {}

    # 提取相似用户
    for author in authors:
        sims = sim_df[author].sort_values(ascending=False)
        sims = sims[sims.index != author]
        similar_users[author] = sims.head(top_n).to_dict()

    return similar_users


def generate_tag_video_mapping(data):
    """
    提取标签与视频ID的映射关系并写入数据库
    :param data: 清洗后的 DataFrame
    """
    # 构建映射列表
    mapping_list = []
    for _, row in data.iterrows():
        for tag in row["tags"]:
            mapping_list.append({"tag": tag, "vd_id": row["vd_id"]})

    # 批量插入数据库
    session.bulk_insert_mappings(TagVideoMapping, mapping_list)
    session.commit()
    print("✅ 标签与视频ID映射已写入数据库")


def store_to_database(data, similar_users=None, task_id=None, is_evil=False):
    """
    将分析结果存储到数据库
    :param data: 清洗后的视频数据
    :param similar_users: 相似用户分析结果
    """
    try:

        # 1. 存储账号统计
        data["engagement_rate"] = (
            (data["likes"] + data["shares"] * 10 + data["collects"] * 10)
        ) / 100

        account_stats = (
            data.groupby("author")
            .agg(
                video_count=("vd_id", "count"),
                total_likes=("likes", "sum"),
                total_shares=("shares", "sum"),
                total_collects=("collects", "sum"),
                engagement_rate=("engagement_rate", "sum"),
            )
            .reset_index()
        )

        # 处理可能的无穷大和NaN值
        account_stats["total_shares"] = (
            account_stats["total_shares"].fillna(0).replace([np.inf, -np.inf], 0)
        )
        account_stats["engagement_rate"] = (
            account_stats["engagement_rate"].fillna(0).replace([np.inf, -np.inf], 0)
        )

        # 写入数据库
        for _, row in account_stats.iterrows():
            session.add(AccountStat(**row.to_dict()))

        # 按点赞数降序排序所有视频（移除head(100)限制）
        top_videos = data.sort_values("likes", ascending=False)[
            [
                "vd_id",
                "vd_title",
                "author",
                "likes",
                "shares",
                "collects",
                "engagement_rate",
                "create_time",
                "img_url",
            ]
        ]

        # 处理互动率缺失值
        top_videos["engagement_rate"] = (
            top_videos["engagement_rate"].fillna(0).replace([np.inf, -np.inf], 0)
        )

        # 新增：确保所有数值字段为整数
        numeric_cols = ["likes", "shares", "collects"]
        for col in numeric_cols:
            top_videos[col] = top_videos[col].fillna(0).astype(int)

        # 新增：过滤无效时间记录
        top_videos = top_videos[top_videos["create_time"].notna()]

        # 处理 author 字段的 nan 值为 None（即 SQL 中的 NULL）
        top_videos["author"] = top_videos["author"].apply(
            lambda x: None if isinstance(x, float) and math.isnan(x) else x
        )

        videos_data = top_videos.to_dict(orient="records")

        # 逐条插入或更新
        for video_dict in videos_data:
            vd_id = video_dict["vd_id"]
            existing_video = session.query(TopVideo).get(vd_id)

            if existing_video:
                # 更新已有记录
                for key in video_dict:
                    if key != "vd_id":
                        setattr(existing_video, key, video_dict[key])
            else:
                # 插入新记录
                session.add(TopVideo(**video_dict))

        # # 修改为批量插入
        # session.bulk_insert_mappings(
        #     TopVideo,
        #     top_videos[
        #         [
        #             "vd_id",
        #             "vd_title",
        #             "author",
        #             "likes",
        #             "shares",
        #             "collects",
        #             "engagement_rate",
        #             "create_time",
        #             "img_url",
        #         ]
        #     ].to_dict(orient="records"),
        # )
        if task_id:
            task_data = [
                {
                    "task_id": task_id,
                    "vd_id": row["vd_id"],
                    "is_evil": True,  # 或根据逻辑判断
                }
                for _, row in top_videos.iterrows()
            ]

            for item in task_data:
                # 检查是否已存在相同 (task_id, vd_id)
                existing = (
                    session.query(DetectionResult)
                    .filter(
                        DetectionResult.task_id == item["task_id"],
                        DetectionResult.vd_id == item["vd_id"],
                    )
                    .first()
                )

                if not existing:
                    session.add(DetectionResult(**item))
        # if task_id:
        #     task_data = [
        #         {
        #             "task_id": task_id,
        #             "vd_id": row["vd_id"],
        #             "is_evil": True,  # 或根据逻辑判断
        #         }
        #         for _, row in top_videos.iterrows()
        #     ]
        #     session.bulk_insert_mappings(DetectionResult, task_data)

        # 3. 存储小时分布
        hourly_data = (
            data.groupby(data["create_time"].dt.hour)["vd_id"].count().reset_index()
        )
        hourly_data.columns = ["hour", "count"]
        for _, row in hourly_data.iterrows():
            session.add(
                HourlyDistribution(hour=int(row["hour"]), count=int(row["count"]))
            )

        # 4. 存储日期分布
        daily_data = (
            data.groupby(data["create_time"].dt.date)["vd_id"].count().reset_index()
        )
        daily_data.columns = ["date", "count"]
        daily_data["date"] = pd.to_datetime(daily_data["date"])
        for _, row in daily_data.iterrows():
            session.add(DailyDistribution(date=row["date"], count=int(row["count"])))

        # 5. 存储互动相关性
        corr_matrix = data[["likes", "shares", "collects"]].corr()
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                metric1 = corr_matrix.columns[i]
                metric2 = corr_matrix.columns[j]
                corr = corr_matrix.iloc[i, j]
                session.add(
                    InteractionCorrelation(
                        metric1=metric1, metric2=metric2, correlation=float(corr)
                    )
                )

        # 6. 存储相似用户分析
        if similar_users:
            for author, similar_dict in similar_users.items():
                for sim_author, score in similar_dict.items():
                    session.add(
                        SimilarUser(
                            original_account=author,
                            similar_account=sim_author,
                            similarity_score=float(score),
                        )
                    )

        # 提交事务
        session.commit()
        print("✅ 分析数据已成功写入数据库")

    except Exception as e:
        # 回滚事务
        session.rollback()
        print(f"❌ 数据库写入失败: {str(e)}")
        raise e  # 或者 raise Exception("数据库写入失败")


def check_removed_videos():
    try:
        # 查询所有未下架的视频
        videos = session.query(TopVideo).filter_by(removed=False).all()
        for video in videos:
            if not video.img_url:  # 跳过无链接的视频
                continue
            # 发送HEAD请求检查状态码（轻量且避免下载内容）
            response = requests.head(video.img_url, allow_redirects=True, timeout=10)
            if response.status_code == 403:
                video.removed = True  # 标记为已下架
                session.commit()
                print(f"✅ 视频 {video.vd_id} 已下架")
    except Exception as e:
        session.rollback()  # 出错时回滚事务
    finally:
        session.close()  # 确保关闭会话，避免连接泄漏


def load_json_data(file_path):
    """加载并解析JSON文件（新增函数）"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def store_json_data(file_path, task_id=None):
    """处理JSON数据并存储到数据库（新增函数）"""
    json_data = load_json_data(file_path)
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
            print(f"用户 {user_info.get('user_id')} 信息已存入数据库")
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
            if "cover_img" in video_df.columns and "img_url" not in video_df.columns:
                video_df["img_url"] = video_df["cover_img"]
            video_df["tags"] = video_df["video_label"]  # 标签列表
            # 调用现有函数存储视频数据并更新标签
            store_to_database(video_df, task_id=task_id)
            generate_word_frequency(video_df)
            generate_tag_video_mapping(video_df)
            # print(video_df)
            print(f"成功存储 {len(videos)} 条视频信息到数据库")
        session.commit()  # 提交事务
    except Exception as e:
        session.rollback()
        print(f"JSON数据处理失败: {str(e)}")


def store_file_to_database(file_path, is_evil=False, task_id=None):
    try:
        if not os.path.exists(file_path):
            return

        if file_path.endswith(".csv"):
            data = load_data(file_path)
            store_to_database(data, task_id=task_id)
            generate_word_frequency(data)
            generate_tag_video_mapping(data)
        elif file_path.endswith(".json"):
            store_json_data(file_path, task_id)

        # 统一移动处理完成的文件（修改点4）
        processed_dir = os.path.join(SOURCE_DIR, "processed")
        os.makedirs(processed_dir, exist_ok=True)
        target_path = os.path.join(processed_dir, os.path.basename(file_path))
        os.rename(file_path, target_path)
        print(f"文件 {file_path} 处理完成并已移动至 {target_path}")
    except Exception as e:
        print(f"处理失败: {str(e)}\n")
        traceback.print_exc()
