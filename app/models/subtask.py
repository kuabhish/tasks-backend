from uuid import uuid4
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from app import db

class Subtask(db.Model):
    __tablename__ = 'subtasks'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum('Not Started', 'In Progress', 'Completed', name='subtask_status'), default='Not Started')
    assigned_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    assigned_team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(ARRAY(db.String), default=[])
    estimated_duration = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'taskId': self.task_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'assignedUserId': self.assigned_user_id,
            'assignedTeamId': self.assigned_team_id,
            'dueDate': self.due_date.isoformat() if self.due_date else None,
            'tags': self.tags,
            'estimatedDuration': self.estimated_duration,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }