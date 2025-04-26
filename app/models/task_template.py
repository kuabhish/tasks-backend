from uuid import uuid4
from datetime import datetime
from app import db

class TaskTemplate(db.Model):
    __tablename__ = 'task_templates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customerId': self.customer_id,
            'title': self.title,
            'description': self.description,
            'categoryId': self.category_id,
            'createdAt': self.created_at.isoformat()
        }

class SubtaskTemplate(db.Model):
    __tablename__ = 'subtask_templates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    template_id = db.Column(db.String(36), db.ForeignKey('task_templates.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'templateId': self.template_id,
            'title': self.title,
            'description': self.description
        }