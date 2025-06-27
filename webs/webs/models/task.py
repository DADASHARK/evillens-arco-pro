# models/task.py - 检测任务模型
from .db import db
import datetime
from datetime import timezone
from sqlalchemy.orm import relationship


class Task(db.Model):
    """Model representing a detection task."""

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    # vd_id = db.Column(db.String(255), nullable=False, index=True)
    status = db.Column(
        db.String(20), default="pending", nullable=False
    )  # pending, processing, completed, failed
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.datetime.now(), nullable=False
    )
    completed_at = db.Column(db.DateTime)
    # result_path = db.Column(db.String(255))

    # Relationship with DetectionResult
    results = relationship("DetectionResult", backref="task", lazy="dynamic")

    def to_dict(self):
        """Convert task object to dictionary."""
        return {
            "task_id": self.task_id,
            # "vd_id": self.vd_id,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": (
                self.completed_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.completed_at
                else None
            ),
            # "result_path": self.result_path,
        }

    # def get_evil_video_ids(self):
    #     """Get a list of evil video IDs detected in this task."""
    #     evil_results = DetectionResult.query.filter_by(
    #         task_id=self.task_id, is_evil=True
    #     ).all()
    #     return [result.vd_id for result in evil_results]

    # def get_all_video_ids(self):
    #     """Get a list of all video IDs in this task."""
    #     results = DetectionResult.query.filter_by(task_id=self.task_id).all()
    #     return [result.vd_id for result in results]
    def get_evil_video_ids(self):
        """Get a list of unique evil video IDs detected in this task."""
        query = (
            DetectionResult.query.with_entities(DetectionResult.vd_id)
            .filter_by(task_id=self.task_id, is_evil=True)
            .distinct(DetectionResult.vd_id)
        )

        return [result.vd_id for result in query.all()]

    def get_all_video_ids(self):
        """Get a list of all unique video IDs in this task."""
        query = (
            DetectionResult.query.with_entities(DetectionResult.vd_id)
            .filter_by(task_id=self.task_id)
            .distinct(DetectionResult.vd_id)
        )

        return [result.vd_id for result in query.all()]


class DetectionResult(db.Model):
    """Model representing a detection result."""

    __tablename__ = "detection_results"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(
        db.String(50), db.ForeignKey("tasks.task_id"), nullable=False, index=True
    )
    vd_id = db.Column(db.String(50), nullable=False, index=True)
    is_evil = db.Column(db.Boolean, default=False, nullable=False)
    # Commented out field, preserved for future use
    # confidence = db.Column(db.Float, default=0)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.datetime.now(), nullable=False
    )

    def to_dict(self):
        """Convert detection result object to dictionary."""
        return {
            "vd_id": self.vd_id,
            "is_evil": self.is_evil,
            # "confidence": self.confidence,
            # "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
