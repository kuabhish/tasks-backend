from uuid import uuid4
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from app import db

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=True)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum('Not Started', 'In Progress', 'Completed', name='task_status'), default='Not Started')
    priority = db.Column(db.Enum('Low', 'Medium', 'High', name='task_priority'), default='Medium')
    assigned_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    assigned_team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_pattern = db.Column(JSON, nullable=True)
    tags = db.Column(ARRAY(db.String), default=[])
    estimated_duration = db.Column(db.Integer, nullable=True)
    actual_duration = db.Column(db.Integer, nullable=True, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customerId': self.customer_id,
            'projectId': self.project_id,
            'categoryId': self.category_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'assignedUserId': self.assigned_user_id,
            'assignedTeamId': self.assigned_team_id,
            'dueDate': self.due_date.isoformat() if self.due_date else None,
            'isRecurring': self.is_recurring,
            'recurringPattern': self.recurring_pattern,
            'tags': self.tags,
            'estimatedDuration': self.estimated_duration,
            'actualDuration': self.actual_duration,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }