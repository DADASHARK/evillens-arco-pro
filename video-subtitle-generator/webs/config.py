# config.py - 配置文件
import os
from pathlib import Path

# Create instance directory if it doesn't exist
basedir = os.path.dirname(os.path.abspath(__file__))
instance_dir = os.path.join(basedir, 'instance')
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard-to-guess-string"

    # 数据库配置 (假设使用MySQL，实际应根据需求选择)
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{os.path.join(basedir, 'instance', 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 默认分页设置
    DEFAULT_PAGE_SIZE = 10

    # 轮播图默认数量
    CAROUSEL_DEFAULT_LIMIT = 6

    # 默认统计天数
    DEFAULT_STATS_DAYS = 90
    DEFAULT_STATS_WEEKS = 8

    # JWT配置（如果需要用户认证）
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "jwt-secret-string"
    JWT_ACCESS_TOKEN_EXPIRES = 3600

# 目录配置
DATASET_DIR = instance_dir  # 保持在 instance 目录（原逻辑）
OUTPUT_DIR = os.path.join(instance_dir, 'output')  # 调整为 instance 下的 output 子目录
IMAGE_DIR = os.path.join(OUTPUT_DIR, 'images')  # 基于新的 OUTPUT_DIR 路径
SOURCE_DIR ="D:\\xinansai\\web\\evillens-arco-pro\\video-subtitle-generator\\source"

# 创建必要目录
os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)


 # 新增缓存配置（解决警告）
CACHE_TYPE = "SimpleCache"  # 使用内存缓存（开发环境推荐）
CACHE_DEFAULT_TIMEOUT = 300  # 默认缓存超时时间（秒）

# 数据库配置
DATABASE_URI = f'sqlite:///{os.path.join(DATASET_DIR, "app.db")}'
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
SMTP_USERNAME = "evillens@163.com"
SMTP_PASSWORD = "DJe5EPucmnmnbVf2"  # 邮箱授权码（非登录密码）
EMAIL_TO = "1298824624@qq.com"
EMAIL_SUBJECT = "邪典视频检测报告 - 自动发送"

CHECK_INTERVAL = 60  # 检查间隔时间（秒），默认为60秒
