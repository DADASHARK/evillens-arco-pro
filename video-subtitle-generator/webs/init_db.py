# init_db.py - 数据库初始化脚本
import pandas as pd
import os
from app import create_app
from models.db import db
from models.video import Video
from models.keyword import Keyword
from models.gang import Gang
from models.cross_platform_account import CrossPlatformAccount
from models.tag_frequency import TagFrequency
from models.interaction_correlation import InteractionCorrelation
from models.daily_distribution import DailyDistribution
from models.hourly_distribution import HourlyDistribution
from datetime import datetime, timedelta
from controllers.analysis import *
from controllers.data_visual import *
from controllers.report_generator import *
import random
from datetime import datetime
from config import DATASET_DIR, OUTPUT_DIR, IMAGE_DIR
from utils import download_image


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        # 创建所有数据库表
        db.create_all()
    
    # 加载测试数据
    df = load_data('../source/test.csv')
    
    # 生成可视化图表
    generate_word_frequency(df)
    generate_tag_video_mapping(df)
    similar_users = extract_similar_users(df)
    '''
    generate_interaction_plot(df)
    generate_trend_plot(df)
    generate_hourly_distribution_plot(df)
    '''
    store_to_database(df, similar_users)

    