# 数据库模型与连接
from sqlalchemy import Boolean, create_engine, Column, String, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URI
from passlib.hash import pbkdf2_sha256  # 导入密码哈希库

# 初始化数据库连接
engine = create_engine(DATABASE_URI, connect_args={'check_same_thread': False})
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# 数据库模型定义
class AccountStat(Base):
    __tablename__ = 'account_stats'
    id = Column(Integer, primary_key=True)
    author = Column(String(255))
    location=Column(String(255))
    video_count = Column(Integer)
    total_likes = Column(Integer)
    total_shares = Column(Integer)
    total_collects = Column(Integer)
    engagement_rate = Column(Float)


class TagFrequency(Base):
    __tablename__ = 'tag_frequencies'
    id = Column(Integer, primary_key=True)
    tag = Column(String(255))
    frequency = Column(Integer)

class TopVideo(Base):
    __tablename__ = 'top_videos'
    vd_id = Column(String(255), primary_key=True)
    vd_title = Column(String(255))
    author = Column(String(255))
    likes = Column(Integer)
    shares = Column(Integer)
    collects = Column(Integer)
    engagement_rate = Column(Float)
    create_time = Column(DateTime)
    #请注意修改默认值！！！！
    evil = Column(Boolean,default=True)
    reported = Column(Boolean,default=False)
    removed = Column(Boolean,default=False)
    # 新增url字段存储视频链接
    img_url = Column(String(500))  # 假设URL最大长度500


class HourlyDistribution(Base):
    __tablename__ = 'hourly_distribution'
    id = Column(Integer, primary_key=True)
    hour = Column(Integer)  # 0-23
    count = Column(Integer)

class DailyDistribution(Base):
    __tablename__ = 'daily_distribution'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    count = Column(Integer)

class InteractionCorrelation(Base):
    __tablename__ = 'interaction_correlations'
    id = Column(Integer, primary_key=True)
    metric1 = Column(String(50))
    metric2 = Column(String(50))
    correlation = Column(Float)

class SimilarUser(Base):
    __tablename__ = 'similar_users'
    id = Column(Integer, primary_key=True)
    original_account = Column(String(255))
    similar_account = Column(String(255))
    similarity_score = Column(Float)

class TagVideoMapping(Base):
    __tablename__ = 'tag_video_mapping'
    id = Column(Integer, primary_key=True)
    tag = Column(String(255), index=True)  # 建立索引，提高查询效率
    vd_id = Column(String(255), index=True)

# 新增用户模型，用于登录验证
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = pbkdf2_sha256.hash(password)
        
    def check_password(self, password):
        """验证密码"""
        return pbkdf2_sha256.verify(password, self.password_hash)

# 创建所有表
Base.metadata.create_all(engine)

# 创建默认管理员账户（如果不存在）
def create_admin_user():
    admin = session.query(User).filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.set_password('admin')
        session.add(admin)
        session.commit()
        print("✅ 已创建默认管理员账户")

# 调用函数创建管理员账户
create_admin_user()