#!/usr/bin/env python3
"""
WSGI Application Entry Point for Production Deployment
Compatible with Vercel, Heroku, Railway, and other platforms
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the simplified Flask application
try:
    from app_simple import app
except ImportError:
    # Fallback to basic app if import fails
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return jsonify({
            "message": "Smart Receipt Processor",
            "status": "running",
            "deployment": "vercel"
        })

# Production configuration
app.config.update(
    DEBUG=False,
    TESTING=False,
    SECRET_KEY=os.environ.get('SECRET_KEY', 'smart-receipt-processor-prod-key'),
)

# Vercel serverless function compatibility
def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, lambda status, headers: None)

# Standard WSGI application
application = app

if __name__ == "__main__":
    # For local production testing
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
