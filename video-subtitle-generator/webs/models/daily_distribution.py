from .db import db
from datetime import datetime

class DailyDistribution(db.Model):
    __tablename__ = 'daily_distribution'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    count = db.Column(db.Integer)

    def to_dict(self):
        return {
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'count': self.count,
        }