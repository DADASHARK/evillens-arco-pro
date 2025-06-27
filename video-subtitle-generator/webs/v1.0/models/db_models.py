# models/db_models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import json

db = SQLAlchemy()


class Video(db.Model):
    """视频信息表"""

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False, unique=True)
    title = db.Column(db.String(200))
    source = db.Column(db.String(100))
    upload_date = db.Column(db.DateTime)
    crawl_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(
        db.String(50), default="pending"
    )  # pending, processing, completed, failed
    is_dangerous = db.Column(db.Boolean, nullable=True)
    metadata = db.Column(db.Text)  # 存储JSON格式的元数据

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "source": self.source,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "crawl_date": self.crawl_date.isoformat(),
            "status": self.status,
            "is_dangerous": self.is_dangerous,
            "metadata": json.loads(self.metadata) if self.metadata else {},
        }


class AnalysisResult(db.Model):
    """视频分析结果表"""

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("video.id"), nullable=False)
    detection_date = db.Column(db.DateTime)
    detection_score = db.Column(db.Float)  # 危险评分
    detection_features = db.Column(db.Text)  # 存储JSON格式的检测特征
    analysis_date = db.Column(db.DateTime)
    trace_results = db.Column(db.Text)  # 存储JSON格式的溯源结果
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "video_id": self.video_id,
            "detection_date": (
                self.detection_date.isoformat() if self.detection_date else None
            ),
            "detection_score": self.detection_score,
            "detection_features": (
                json.loads(self.detection_features) if self.detection_features else {}
            ),
            "analysis_date": (
                self.analysis_date.isoformat() if self.analysis_date else None
            ),
            "trace_results": (
                json.loads(self.trace_results) if self.trace_results else {}
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
