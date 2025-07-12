from .database import db
from datetime import datetime

class EmailAudit(db.Model):
    __tablename__ = 'email_audits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email_content = db.Column(db.Text, nullable=False)
    audit_result = db.Column(db.Text, nullable=False)
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailAudit {self.id} for user {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email_content': self.email_content,
            'audit_result': self.audit_result,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 