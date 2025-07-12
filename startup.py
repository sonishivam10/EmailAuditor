#!/usr/bin/env python3
"""
Startup script to ensure database is properly initialized before starting the application.
This prevents race conditions in multi-worker environments like Docker.
"""

import os
import sys
import time
import sqlite3
from pathlib import Path

def ensure_database_ready():
    """Ensure database is ready before starting the application."""
    print("🔧 Checking database initialization...")
    
    # Get database path
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///email_auditor.db')
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
        if db_path.startswith('/'):
            db_path = db_path[1:]
    else:
        db_path = 'email_auditor.db'
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}, initializing...")
        try:
            from app import create_app
            app = create_app()
            with app.app_context():
                from app.models.database import db
                db.create_all()
            print("Database initialized successfully!")
            return True
        except Exception as e:
            print(f"Database initialization failed: {e}")
            return False
    
    # Check if tables exist
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for required tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        users_exists = cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='otp_codes'")
        otp_exists = cursor.fetchone() is not None
        
        conn.close()
        
        if users_exists and otp_exists:
            print("Database tables already exist!")
            return True
        else:
            print("Database file exists but tables are missing, initializing...")
            try:
                from app import create_app
                app = create_app()
                with app.app_context():
                    from app.models.database import db
                    db.create_all()
                print("Database tables created successfully!")
                return True
            except Exception as e:
                print(f"Database table creation failed: {e}")
                return False
                
    except Exception as e:
        print(f"Error checking database: {e}")
        return False

def main():
    """Main startup function."""
    print("Email Auditor Startup Script")
    print("=" * 40)
    
    # Set Docker environment variable
    os.environ['DOCKER_CONTAINER'] = 'true'
    
    # Ensure database is ready
    if not ensure_database_ready():
        print("Database initialization failed, exiting...")
        sys.exit(1)
    
    print("Database is ready!")
    print("Starting Email Auditor application with Gunicorn...")
    print("=" * 40)
    
    # Start gunicorn server
    import subprocess
    import sys
    
    # Gunicorn command
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--workers", "4",
        "--timeout", "120",
        "--preload",  # Preload app to avoid worker initialization issues
        "wsgi:app"
    ]
    
    # Execute gunicorn
    subprocess.run(cmd)

if __name__ == "__main__":
    main() 