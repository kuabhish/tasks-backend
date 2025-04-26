from uuid import uuid4
from datetime import datetime
from app import db

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customerId': self.customer_id,
            'name': self.name,
            'description': self.description,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }