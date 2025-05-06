# app/models/project.py
from uuid import uuid4
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from app import db

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    project_manager_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('Active', 'On Hold', 'Completed', name='project_status'), default='Active')
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    budget = db.Column(db.Numeric(10, 2), nullable=True)
    goals = db.Column(JSON, nullable=True)
    milestones = db.Column(JSON, nullable=True)
    tech_stack = db.Column(ARRAY(db.String), default=[])
    repository_url = db.Column(db.String(255), nullable=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=True)  # New column for soft delete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customerId': self.customer_id,
            'title': self.title,
            'description': self.description,
            'project_manager_id': self.project_manager_id,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'budget': float(self.budget) if self.budget else None,
            'goals': self.goals,
            'milestones': self.milestones,
            'techStack': self.tech_stack,
            'repository_url': self.repository_url,
            'is_archived': self.is_archived,  # Include in response
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }
        