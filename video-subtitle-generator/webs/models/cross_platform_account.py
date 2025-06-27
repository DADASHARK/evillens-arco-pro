from datetime import datetime
from .db import db


class CrossPlatformAccount(db.Model):
    __tablename__ = 'cross_platform_accounts'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    followers = db.Column(db.Integer)
    likes = db.Column(db.Integer)
    comments = db.Column(db.Integer)
    shares = db.Column(db.Integer)  # Add this field for total shares
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {"platform": self.platform, "url": self.url}


