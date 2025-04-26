from uuid import uuid4
from datetime import datetime
from app import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customerId': self.customer_id,
            'name': self.name,
            'color': self.color,
            'createdAt': self.created_at.isoformat()
        }