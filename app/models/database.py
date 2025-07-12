from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
import time
import threading
import os

db = SQLAlchemy()

# Global lock for database initialization
_db_init_lock = threading.Lock()
_db_initialized = False

def init_database(app):
    """Safely initialize database tables with concurrency handling."""
    global _db_initialized
    
    # Use a lock to prevent multiple workers from initializing simultaneously
    with _db_init_lock:
        if _db_initialized:
            app.logger.info("Database already initialized by another worker, skipping.")
            return True
            
        with app.app_context():
            try:
                # Check if tables already exist
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()
                
                if 'users' in existing_tables and 'otp_codes' in existing_tables:
                    app.logger.info("Database tables already exist, skipping creation.")
                    _db_initialized = True
                    return True
                
                # Create tables if they don't exist
                # Use a more robust approach with retries
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        db.create_all()
                        app.logger.info("Database tables created successfully.")
                        _db_initialized = True
                        return True
                    except Exception as create_error:
                        if "already exists" in str(create_error).lower():
                            app.logger.info("Tables were created by another worker, continuing...")
                            _db_initialized = True
                            return True
                        elif attempt < max_retries - 1:
                            app.logger.warning(f"Database creation attempt {attempt + 1} failed, retrying...")
                            time.sleep(1)  # Wait before retry
                        else:
                            raise create_error
                            
            except Exception as e:
                app.logger.error(f"Database initialization failed: {e}")
                return False

def init_database_docker(app):
    """Docker-specific database initialization with file-based locking."""
    # Check if we're in a Docker environment
    if not os.path.exists('/.dockerenv') and not os.environ.get('DOCKER_CONTAINER'):
        # Not in Docker, use regular initialization
        return init_database(app)
    
    # Docker-specific initialization
    lock_file = '/tmp/db_init.lock'
    max_wait_time = 30  # Maximum seconds to wait for lock
    
    try:
        # Try to acquire file-based lock
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            try:
                with open(lock_file, 'x') as f:
                    f.write(str(os.getpid()))
                break
            except FileExistsError:
                # Another process is initializing, wait
                app.logger.info("Another process is initializing database, waiting...")
                time.sleep(2)
                continue
        else:
            app.logger.warning("Could not acquire database lock, proceeding anyway...")
            
        with app.app_context():
            try:
                # Check if tables already exist
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()
                
                if 'users' in existing_tables and 'otp_codes' in existing_tables:
                    app.logger.info("Database tables already exist, skipping creation.")
                    return True
                
                # Create tables with retry logic
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        db.create_all()
                        app.logger.info("Database tables created successfully.")
                        return True
                    except Exception as create_error:
                        error_msg = str(create_error).lower()
                        if "already exists" in error_msg:
                            app.logger.info("Tables were created by another process, continuing...")
                            return True
                        elif attempt < max_retries - 1:
                            app.logger.warning(f"Database creation attempt {attempt + 1} failed, retrying in 2 seconds...")
                            time.sleep(2)
                        else:
                            app.logger.error(f"Database initialization failed after {max_retries} attempts: {create_error}")
                            return False
                            
            except Exception as e:
                app.logger.error(f"Database initialization failed: {e}")
                return False
                
    finally:
        # Clean up lock file
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
        except:
            pass

def reset_database(app):
    """Reset database by dropping and recreating all tables."""
    with app.app_context():
        try:
            db.drop_all()
            db.create_all()
            app.logger.info("Database reset successfully.")
            return True
        except Exception as e:
            app.logger.error(f"Database reset failed: {e}")
            return False 