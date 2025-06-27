from .db import db
from sqlalchemy import Column, Integer, String, Float

class InteractionCorrelation(db.Model):
    __tablename__ = 'interaction_correlations'
    
    id = Column(Integer, primary_key=True)
    metric1 = Column(String(50))
    metric2 = Column(String(50))
    correlation = Column(Float)

    def to_dict(self):
        return {
            "id": self.id,
            "metric1": self.metric1,
            "metric2": self.metric2,
            "correlation": self.correlation
        }