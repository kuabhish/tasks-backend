from uuid import uuid4
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from app import db
from sqlalchemy.orm import relationship

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
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(ARRAY(db.String), default=[])
    estimated_duration = db.Column(db.Integer, nullable=True)
    actual_duration = db.Column(db.Integer, nullable=True, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subtasks = relationship('Subtask', backref='task', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'project_id': self.project_id,
            'category_id': self.category_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'tags': self.tags,
            'estimated_duration': self.estimated_duration,
            'actual_duration': self.actual_duration,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }