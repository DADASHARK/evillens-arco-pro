# models/keyword.py - 关键词模型
from .db import db


class Keyword(db.Model):
    __tablename__ = "keywords"

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), unique=True, nullable=False)
    percentage = db.Column(db.Float, default=0)

    def to_dict(self):
        return {"keyword": self.keyword, "percentage": str(self.percentage)}
