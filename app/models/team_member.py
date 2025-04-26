from datetime import datetime
from app import db

class TeamMember(db.Model):
    __tablename__ = 'team_members'

    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True)
    team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'userId': self.user_id,
            'teamId': self.team_id,
            'joinedAt': self.joined_at.isoformat()
        }