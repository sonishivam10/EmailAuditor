from datetime import datetime, date
from flask import current_app
from ..models import EmailAudit, User
from ..models.user import db

class RateLimiter:
    """Rate limiting utility for API usage."""
    
    def check_limit(self, user_id: int) -> bool:
        """Check if user has exceeded daily limit."""
        today = datetime.utcnow().date()
        user = User.query.get(user_id)
        
        if not user:
            return False
        
        # Get daily limit based on subscription tier
        if user.subscription_tier == 'free':
            daily_limit = current_app.config['FREE_TIER_DAILY_LIMIT']
        else:
            daily_limit = current_app.config['PREMIUM_TIER_DAILY_LIMIT']
        
        # Count today's audits
        today_audits = EmailAudit.query.filter(
            EmailAudit.user_id == user_id,
            db.func.date(EmailAudit.created_at) == today
        ).count()
        
        return today_audits < daily_limit
    
    def get_usage(self, user_id: int) -> dict:
        """Get current usage statistics for user."""
        today = datetime.utcnow().date()
        user = User.query.get(user_id)
        
        if not user:
            return {'error': 'User not found'}
        
        # Get daily limit based on subscription tier
        if user.subscription_tier == 'free':
            daily_limit = current_app.config['FREE_TIER_DAILY_LIMIT']
        else:
            daily_limit = current_app.config['PREMIUM_TIER_DAILY_LIMIT']
        
        # Count today's audits
        today_audits = EmailAudit.query.filter(
            EmailAudit.user_id == user_id,
            db.func.date(EmailAudit.created_at) == today
        ).count()
        
        return {
            'today_usage': today_audits,
            'daily_limit': daily_limit,
            'remaining': max(0, daily_limit - today_audits),
            'subscription_tier': user.subscription_tier
        } 