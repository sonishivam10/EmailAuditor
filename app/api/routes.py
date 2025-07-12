from flask import request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
import tempfile
import os
import json
from . import api_bp
from ..models import User, EmailAudit
from ..models.database import db
from ..services.audit_service import AuditService
from ..utils.rate_limiter import RateLimiter
import secrets
import tempfile

@api_bp.route('/audit', methods=['POST'])
def audit_email():
    """API endpoint to audit an email file."""
    # Check API key
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'error': 'API key required'}), 401
    
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Check rate limit
    rate_limiter = RateLimiter()
    if not rate_limiter.check_limit(user.id):
        return jsonify({'error': 'Daily limit exceeded'}), 429
    
    # Get email content
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    if not file.filename.lower().endswith('.eml'):
        return jsonify({'error': 'Only .eml files are allowed'}), 400
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.eml') as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name
    
    try:
        # Audit email
        audit_service = AuditService()
        result = audit_service.audit_email_file(tmp_path, user.id)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return jsonify(result)
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        current_app.logger.error(f"Error auditing email: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/usage')
def get_usage():
    """Get current usage statistics."""
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'error': 'API key required'}), 401
    
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({'error': 'Invalid API key'}), 401
    
    rate_limiter = RateLimiter()
    usage = rate_limiter.get_usage(user.id)
    
    return jsonify(usage)

@api_bp.route('/key', methods=['GET', 'POST'])
@login_required
def manage_api_key():
    """Get or regenerate API key."""
    if request.method == 'POST':
        # Regenerate API key
        current_user.api_key = secrets.token_urlsafe(32)
        db.session.commit()
        return jsonify({'api_key': current_user.api_key})
    else:
        return jsonify({'api_key': current_user.api_key})

@api_bp.route('/health')
def api_health_check():
    """Detailed health check endpoint for API monitoring."""
    try:
        # Check database connection
        db.session.execute(text('SELECT 1'))
        
        # Check if services can be imported
        from ..services.email_service import EmailService
        from ..services.audit_service import AuditService
        
        # Get basic stats
        user_count = User.query.count()
        audit_count = EmailAudit.query.count()
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0',
            'environment': current_app.config.get('FLASK_ENV', 'development'),
            'services': {
                'database': {
                    'status': 'connected',
                    'users': user_count,
                    'audits': audit_count
                },
                'email_service': 'available',
                'audit_service': 'available',
                'rate_limiter': 'available'
            },
            'limits': {
                'free_tier_daily': current_app.config.get('FREE_TIER_DAILY_LIMIT', 5),
                'premium_tier_daily': current_app.config.get('PREMIUM_TIER_DAILY_LIMIT', 100)
            }
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        health_status = {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0',
            'environment': current_app.config.get('FLASK_ENV', 'development'),
            'error': str(e),
            'services': {
                'database': 'error',
                'email_service': 'unknown',
                'audit_service': 'unknown',
                'rate_limiter': 'unknown'
            }
        }
        
        return jsonify(health_status), 503 