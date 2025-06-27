# models/video_keyword.py - 视频-关键词关联表
from .db import db

video_keyword = db.Table(
    "video_keyword",
    db.Column("video_id", db.Integer, db.ForeignKey("videos.id"), primary_key=True),
    db.Column("keyword_id", db.Integer, db.ForeignKey("keywords.id"), primary_key=True),
)
