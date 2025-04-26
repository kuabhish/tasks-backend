from uuid import uuid4
from datetime import datetime
from app import db

class TimeEntry(db.Model):
    __tablename__ = 'time_entries'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    subtask_id = db.Column(db.String(36), db.ForeignKey('subtasks.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customerId': self.customer_id,
            'userId': self.user_id,
            'subtaskId': self.subtask_id,
            'startTime': self.start_time.isoformat(),
            'endTime': self.end_time.isoformat(),
            'duration': self.duration,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat()
        }