from .db import db

class HourlyDistribution(db.Model):
    __tablename__ = 'hourly_distribution'
    id = db.Column(db.Integer, primary_key=True)
    hour = db.Column(db.Integer)
    count = db.Column(db.Integer)

    def to_dict(self):
        return {
            "hour": self.hour,
            "count": self.count
        }