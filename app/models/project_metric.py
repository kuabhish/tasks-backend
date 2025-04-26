from uuid import uuid4
from datetime import datetime
from app import db

class ProjectMetric(db.Model):
    __tablename__ = 'project_metrics'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    metric_type = db.Column(db.Enum('Task Completion', 'Budget Utilization', 'Time Spent', 'Milestone Completion', name='metric_type'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'projectId': self.project_id,
            'metricType': self.metric_type,
            'value': self.value,
            'recordedAt': self.recorded_at.isoformat()
        }