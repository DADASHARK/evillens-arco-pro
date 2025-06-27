# models/gang.py - 团伙模型
from .db import db


class Gang(db.Model):
    __tablename__ = "gangs"

    id = db.Column(db.Integer, primary_key=True)
    gang_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    distribution = db.Column(db.String(255))
    activity_time = db.Column(db.String(255))

    def to_dict(self):
        return {"gang_id": self.gang_id, "name": self.name}

    def to_detail_dict(self):
        cross_platform_accounts = [account.to_dict() for account in self.accounts]

        return {
            "gang_id": self.gang_id,
            "name": self.name,
            "distribution": self.distribution,
            "activity_time": self.activity_time,
            "cross_platform_accounts": cross_platform_accounts,
        }
