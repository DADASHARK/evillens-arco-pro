# models/video.py - 视频模型
from .db import db
from datetime import datetime


class Video(db.Model):
    __tablename__ = "videos"

    id = db.Column(db.Integer, primary_key=True)
    vd_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    cover_url = db.Column(db.String(500))
    province = db.Column(db.String(50))
    publish_time = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    shares= db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    reported = db.Column(db.Boolean, default=False)
    removed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "vd_id": self.vd_id,
            "name": self.name,
            "cover_url": self.cover_url,
            "province": self.province,
            "publish_time": (
                self.publish_time.strftime("%Y-%m-%d %H:%M:%S")
                if self.publish_time
                else None
            ),
            "likes": self.likes,
            "shares": self.shares,
            "comments": self.comments,
            "reported": self.reported,
            "removed": self.removed,
        }
