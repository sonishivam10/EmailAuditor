#!/usr/bin/env python3
"""
Database management script for EmailAuditor.
Use this script to initialize, reset, or check the database.
"""

import os
import sys
from app import create_app
from app.models.database import init_database, reset_database, db
from app.models import User, OTPCode

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_db.py [init|reset|check|create-admin]")
        sys.exit(1)
    
    command = sys.argv[1]
    app = create_app()
    
    with app.app_context():
        if command == "init":
            print("Initializing database...")
            if init_database(app):
                print("Database initialized successfully!")
            else:
                print("Database initialization failed!")
                sys.exit(1)
                
        elif command == "reset":
            print("Resetting database...")
            confirm = input("This will delete all data. Are you sure? (y/N): ")
            if confirm.lower() == 'y':
                if reset_database(app):
                    print("Database reset successfully!")
                else:
                    print("Database reset failed!")
                    sys.exit(1)
            else:
                print("Reset cancelled.")
                
        elif command == "check":
            print("Checking database status...")
            try:
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"Found tables: {tables}")
                
                if 'users' in tables:
                    user_count = User.query.count()
                    print(f"Users in database: {user_count}")
                    
                if 'otp_codes' in tables:
                    otp_count = OTPCode.query.count()
                    print(f"OTP codes in database: {otp_count}")
                    
            except Exception as e:
                print(f"Error checking database: {e}")
                sys.exit(1)
                
        elif command == "create-admin":
            print("Creating admin user...")
            email = input("Enter admin email: ")
            mobile = input("Enter admin mobile (optional): ")
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                print(f"User with email {email} already exists!")
                sys.exit(1)
            
            # Create admin user
            admin_user = User(
                email=email,
                mobile=mobile,
                is_verified=True,
                subscription_tier='admin'
            )
            admin_user.set_password('admin123')  # You should change this
            
            try:
                db.session.add(admin_user)
                db.session.commit()
                print(f"Admin user created successfully!")
                print(f"Email: {email}")
                print(f"Password: admin123")
                print("Please change the password after first login!")
            except Exception as e:
                print(f"Error creating admin user: {e}")
                db.session.rollback()
                sys.exit(1)
                
        else:
            print(f"Unknown command: {command}")
            print("Available commands: init, reset, check, create-admin")
            sys.exit(1)

if __name__ == "__main__":
    main() 