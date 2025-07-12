#!/usr/bin/env python3
"""
Simple startup script for Email Auditor application.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting Email Auditor...")
    print("📱 Web UI: http://localhost:5000")
    print("📚 API Docs: http://localhost:5000/docs")
    print("⏹️  Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=5000, debug=True) 