from flask_login import UserMixin
from datetime import datetime
import secrets
from .database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(200))
    is_verified = db.Column(db.Boolean, default=False)
    subscription_tier = db.Column(db.String(20), default='free')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    api_key = db.Column(db.String(64), unique=True)
    
    # Relationships
    otp_codes = db.relationship('OTPCode', backref='user', lazy=True, cascade='all, delete-orphan')
    email_audits = db.relationship('EmailAudit', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.api_key:
            self.api_key = secrets.token_urlsafe(32)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'mobile': self.mobile,
            'is_verified': self.is_verified,
            'subscription_tier': self.subscription_tier,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'api_key': self.api_key
        } 