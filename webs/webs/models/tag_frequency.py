from .db import db

class TagFrequency(db.Model):
    __tablename__ = 'tag_frequencies'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(255))
    frequency = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "tag": self.tag,
            "frequency": self.frequency
        }