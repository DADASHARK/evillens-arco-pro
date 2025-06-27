# 数据分析模块
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models.db import db
from datetime import datetime
from config import IMAGE_DIR  # 导入图像目录
from utils import download_image  # 导入下载图片函数
from models.video import Video  # 导入视频模型
from models.tag_frequency import *
import os
# 从数据库模块导入会话和模型
from models.database import (
    session, AccountStat, TopVideo, HourlyDistribution,
    DailyDistribution, InteractionCorrelation, SimilarUser,session, TagVideoMapping
)
import requests
from models.database import session, TopVideo  # 导入数据库会话和模型

def parse_date(date_str):
    """Convert string to datetime object"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None

def load_data(file_path):
    """数据加载与清洗"""
    data = pd.read_csv(file_path)
    
    # 修改时间解析逻辑
    data['create_time'] = pd.to_datetime(
        data['create_time'],
        format='%Y-%m-%d %H:%M:%S',
        errors='coerce'  # 将解析失败的值转为NaT
    )
    
    valid_data = data.copy()
    
    # 新增时区处理（保持原有列不变）
    valid_data['hour_of_day'] = valid_data['create_time'].dt.hour
    valid_data['day_of_week'] = valid_data['create_time'].dt.day_name().fillna('未知')
    
    # 修复空值处理：填充空标题为空白字符串
    valid_data['tags'] = valid_data['vd_title'].fillna('').str.findall(r'#([^#\s]+)').apply(set)

    valid_data['image_path'] = valid_data.apply(
        lambda x: os.path.join(IMAGE_DIR, f"{x['vd_id']}.jpg"), axis=1
    )

    # 下载图片（根据需求启用）
    valid_data['image_downloaded'] = valid_data.apply(
          lambda x: download_image(x['img_url'], x['image_path']), axis=1
      )

    # 计算互动率（保留原有逻辑）
    if 'followers' in valid_data.columns:
        valid_data['engagement_rate'] = valid_data['likes'] / valid_data['followers']
    else:
        valid_data['engagement_rate'] = np.nan

    # 时间特征提取添加空值保护
    valid_data['hour_of_day'] = valid_data['create_time'].dt.hour.where(valid_data['create_time'].notna(), np.nan)
    valid_data['day_of_week'] = valid_data['create_time'].dt.day_name().where(valid_data['create_time'].notna(), '未知')

    print(f"数据加载完成：共加载{len(valid_data)}条记录")
    return valid_data
    
def generate_word_frequency(data):
    """生成标签词频统计并存储到数据库（增量模式）"""
    all_tags = [tag for tags in data['tags'] for tag in tags]
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
    author_counts = data['author'].value_counts()
    valid_authors = author_counts[author_counts >= min_videos].index
    valid_data = data[data['author'].isin(valid_authors)]

    # 构建时间分布矩阵
    hourly_dist = valid_data.groupby(['author', 'hour_of_day']).size().unstack(fill_value=0)
    hourly_dist = hourly_dist.div(hourly_dist.sum(axis=1), axis=0)
    authors = hourly_dist.index.tolist()

    # 构建名称特征
    name_vec = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
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
        for tag in row['tags']:
            mapping_list.append({
                'tag': tag,
                'vd_id': row['vd_id']
            })

    # 批量插入数据库
    session.bulk_insert_mappings(TagVideoMapping, mapping_list)
    session.commit()
    print("✅ 标签与视频ID映射已写入数据库")


def store_to_database(data, similar_users=None):
    """
    将分析结果存储到数据库
    :param data: 清洗后的视频数据
    :param similar_users: 相似用户分析结果
    """
    try:

        # 1. 存储账号统计
        data['engagement_rate'] = ((data['likes'] + data['shares'] * 10 + data['collects'] * 10))/100

        account_stats = data.groupby('author').agg(
            video_count=('vd_id', 'count'),
            total_likes=('likes', 'sum'),
            total_shares=('shares', 'sum'),
            total_collects=('collects','sum'),
            engagement_rate=('engagement_rate',"sum"),
        ).reset_index()

        # 处理可能的无穷大和NaN值
        account_stats['total_shares'] = account_stats['total_shares'].fillna(0).replace([np.inf, -np.inf], 0)
        account_stats['engagement_rate'] = account_stats['engagement_rate'].fillna(0).replace([np.inf, -np.inf], 0)


        # 写入数据库
        for _, row in account_stats.iterrows():
            session.add(AccountStat(**row.to_dict()))

        # 按点赞数降序排序所有视频（移除head(100)限制）
        top_videos = data.sort_values('likes', ascending=False)[[
            'vd_id', 'vd_title', 'author', 'likes', 'shares', 'collects',
            'engagement_rate', 'create_time','img_url'
        ]]  

        # 处理互动率缺失值
        top_videos['engagement_rate'] = top_videos['engagement_rate'].fillna(0).replace([np.inf, -np.inf], 0)
        
        # 新增：确保所有数值字段为整数
        numeric_cols = ['likes', 'shares', 'collects']
        for col in numeric_cols:
            top_videos[col] = top_videos[col].fillna(0).astype(int)
        
        # 新增：过滤无效时间记录
        top_videos = top_videos[top_videos['create_time'].notna()]
        
        # 修改为批量插入
        session.bulk_insert_mappings(TopVideo, 
            top_videos[['vd_id', 'vd_title', 'author', 'likes', 'shares', 
                       'collects', 'engagement_rate', 'create_time','img_url']].to_dict(orient='records'))

        # 3. 存储小时分布
        hourly_data = data.groupby(data['create_time'].dt.hour)['vd_id'].count().reset_index()
        hourly_data.columns = ['hour', 'count']
        for _, row in hourly_data.iterrows():
            session.add(HourlyDistribution(hour=int(row['hour']), count=int(row['count'])))

        # 4. 存储日期分布
        daily_data = data.groupby(data['create_time'].dt.date)['vd_id'].count().reset_index()
        daily_data.columns = ['date', 'count']
        daily_data['date'] = pd.to_datetime(daily_data['date'])
        for _, row in daily_data.iterrows():
            session.add(DailyDistribution(date=row['date'], count=int(row['count'])))

        # 5. 存储互动相关性
        corr_matrix = data[['likes', 'shares', 'collects']].corr()
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                metric1 = corr_matrix.columns[i]
                metric2 = corr_matrix.columns[j]
                corr = corr_matrix.iloc[i, j]
                session.add(InteractionCorrelation(metric1=metric1, metric2=metric2, correlation=float(corr)))

        # 6. 存储相似用户分析
        if similar_users:
            for author, similar_dict in similar_users.items():
                for sim_author, score in similar_dict.items():
                    session.add(
                        SimilarUser(
                            original_account=author,
                            similar_account=sim_author,
                            similarity_score=float(score)
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
