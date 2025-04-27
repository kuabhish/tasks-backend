from uuid import uuid4
from datetime import datetime
from app import db

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(50), nullable=True)
    contact_email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    plan = db.Column(db.Enum('Basic', 'Pro', 'Enterprise', name='customer_plan'), default='Basic')
    billing_status = db.Column(db.Enum('Active', 'Past Due', 'Canceled', name='billing_status'), default='Active')
    max_users = db.Column(db.Integer, nullable=True)
    logo_url = db.Column(db.String(255), nullable=True)
    time_zone = db.Column(db.String(50), nullable=False, default='UTC')
    domain = db.Column(db.String(100), nullable=True)  # New field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'industry': self.industry,
            'contactEmail': self.contact_email,
            'phone': self.phone,
            'address': self.address,
            'plan': self.plan,
            'billingStatus': self.billing_status,
            'maxUsers': self.max_users,
            'logoUrl': self.logo_url,
            'timeZone': self.time_zone,
            'domain': self.domain,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }