from flask import render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import secrets
import json
from sqlalchemy import text
from . import web_bp
from ..models import User, OTPCode, EmailAudit
from ..models.database import db
from ..services.email_service import EmailService
from ..services.audit_service import AuditService

@web_bp.route('/')
def index():
    """Home page."""
    # Redirect logged-in users to dashboard
    if current_user.is_authenticated:
        flash('Welcome back! Redirecting to your dashboard.', 'info')
        return redirect(url_for('web.dashboard'))
    
    return render_template('index.html')

@web_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with OTP verification."""
    # Redirect logged-in users to dashboard
    if current_user.is_authenticated:
        flash('You are already logged in. Redirecting to dashboard.', 'info')
        return redirect(url_for('web.dashboard'))
    
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        mobile = data.get('mobile')
        
        if not email and not mobile:
            return jsonify({'error': 'Email or mobile is required'}), 400
        
        # Check if user already exists
        existing_user = None
        if email:
            existing_user = User.query.filter_by(email=email).first()
        if mobile and not existing_user:
            existing_user = User.query.filter_by(mobile=mobile).first()
        
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        
        # Create new user
        user = User(email=email, mobile=mobile)
        db.session.add(user)
        db.session.commit()
        
        # Generate and send OTP
        email_service = EmailService()
        success = email_service.send_otp(user)
        
        if success:
            return jsonify({'message': 'OTP sent successfully', 'user_id': user.id})
        else:
            return jsonify({'error': 'Failed to send OTP'}), 500
    
    return render_template('register.html')

@web_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and complete registration/login."""
    data = request.get_json()
    user_id = data.get('user_id')
    otp_code = data.get('otp')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    otp = OTPCode.query.filter_by(
        user_id=user_id,
        code=otp_code,
        is_used=False
    ).filter(OTPCode.expires_at > datetime.utcnow()).first()
    
    if not otp:
        return jsonify({'error': 'Invalid or expired OTP'}), 400
    
    # Mark OTP as used
    otp.is_used = True
    user.is_verified = True
    db.session.commit()
    
    # Log user in
    login_user(user)
    
    flash('Login successful! Welcome back.', 'success')
    return jsonify({'message': 'OTP verified successfully'})

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with OTP."""
    # Redirect logged-in users to dashboard
    if current_user.is_authenticated:
        flash('You are already logged in. Redirecting to dashboard.', 'info')
        return redirect(url_for('web.dashboard'))
    
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        mobile = data.get('mobile')
        
        user = None
        if email:
            user = User.query.filter_by(email=email).first()
        elif mobile:
            user = User.query.filter_by(mobile=mobile).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate and send OTP
        email_service = EmailService()
        success = email_service.send_otp(user)
        
        if success:
            return jsonify({'message': 'OTP sent successfully', 'user_id': user.id})
        else:
            return jsonify({'error': 'Failed to send OTP'}), 500
    
    return render_template('login.html')

@web_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('web.index'))

@web_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    return render_template('dashboard.html')

@web_bp.route('/docs')
def docs():
    """API documentation."""
    return render_template('docs.html')

@web_bp.route('/ping')
def ping():
    """Simple ping endpoint for basic connectivity testing."""
    return jsonify({'message': 'pong', 'timestamp': datetime.utcnow().isoformat()})

@web_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring and deployment platforms."""
    try:
        # Check database connection
        from ..models.database import db
        db.session.execute(text('SELECT 1'))
        
        # Check if all required services are available
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0',
            'services': {
                'database': 'connected',
                'email_service': 'available',
                'audit_service': 'available'
            },
            'uptime': 'running'
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        health_status = {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0',
            'error': str(e),
            'services': {
                'database': 'error',
                'email_service': 'unknown',
                'audit_service': 'unknown'
            }
        }
        
        return jsonify(health_status), 503 