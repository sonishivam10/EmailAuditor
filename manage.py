#!/usr/bin/env python3
"""
Management script for Email Auditor application.
"""

import os
import sys
from flask.cli import FlaskGroup
from app import create_app
from app.models.database import db
from app.models import User, OTPCode, EmailAudit

app = create_app()
cli = FlaskGroup(app)

@cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print("✅ Database initialized successfully")

@cli.command()
def create_admin():
    """Create an admin user."""
    email = input("Enter admin email: ")
    mobile = input("Enter admin mobile (optional): ")
    
    user = User(email=email, mobile=mobile, subscription_tier='premium')
    user.is_verified = True
    db.session.add(user)
    db.session.commit()
    
    print(f"✅ Admin user created: {email}")
    print(f"API Key: {user.api_key}")

@cli.command()
def test_email():
    """Test email configuration."""
    from app.services.email_service import EmailService
    
    email = input("Enter test email address: ")
    service = EmailService()
    
    if service.send_otp_email(email, "123456"):
        print("✅ Email sent successfully")
    else:
        print("❌ Failed to send email")

if __name__ == '__main__':
    cli() 