#!/usr/bin/env python3
"""
WSGI entry point for Email Auditor application.
"""

import os
from app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # For development
    app.run(host='0.0.0.0', port=5000, debug=True) 