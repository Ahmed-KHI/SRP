#!/usr/bin/env python3
"""
WSGI Application Entry Point for Vercel Deployment
Simplified version that works with Vercel's serverless functions
"""

import os
from flask import Flask, jsonify, render_template_string

# Create Flask application directly here
app = Flask(__name__)

# Configuration
app.config.update(
    DEBUG=False,
    TESTING=False,
    SECRET_KEY=os.environ.get('SECRET_KEY', 'smart-receipt-processor-prod-key'),
)

# Check if AI is configured
def is_ai_configured():
    """Check if Gemini AI is configured"""
    return bool(os.environ.get('GEMINI_API_KEY'))

@app.route('/')
def index():
    """Main homepage"""
    ai_status = "configured" if is_ai_configured() else "not configured"
    
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart Receipt Processor</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .hero-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 4rem 0; }
            .card { box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: none; }
        </style>
    </head>
    <body>
        <section class="hero-section">
            <div class="container text-center">
                <h1 class="display-4 mb-4">
                    <i class="fas fa-receipt"></i> Smart Receipt Processor
                </h1>
                <p class="lead">AI-powered finance automation system deployed on Vercel</p>
                <div class="mt-4">
                    <span class="badge bg-success fs-6">🚀 Live Deployment</span>
                    <span class="badge bg-info fs-6">AI: {{ ai_status }}</span>
                </div>
            </div>
        </section>
        
        <div class="container my-5">
            <div class="row">
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">
                                <i class="fas fa-magic text-primary"></i> Core Features
                            </h5>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-success"></i> AI-powered receipt analysis</li>
                                <li><i class="fas fa-check text-success"></i> Automatic expense categorization</li>
                                <li><i class="fas fa-check text-success"></i> Google Gemini AI integration</li>
                                <li><i class="fas fa-check text-success"></i> Professional web interface</li>
                                <li><i class="fas fa-check text-success"></i> REST API endpoints</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">
                                <i class="fas fa-cog text-info"></i> Technology Stack
                            </h5>
                            <ul class="list-unstyled">
                                <li><i class="fab fa-python text-warning"></i> Python Flask Framework</li>
                                <li><i class="fas fa-brain text-purple"></i> Google Gemini AI</li>
                                <li><i class="fab fa-bootstrap text-primary"></i> Bootstrap UI</li>
                                <li><i class="fas fa-cloud text-info"></i> Vercel Serverless</li>
                                <li><i class="fab fa-github text-dark"></i> GitHub Repository</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="card-title">🎯 Quick Links</h5>
                            <div class="d-flex justify-content-center gap-3 flex-wrap">
                                <a href="/api/status" class="btn btn-primary">
                                    <i class="fas fa-heartbeat"></i> API Status
                                </a>
                                <a href="/demo" class="btn btn-success">
                                    <i class="fas fa-play"></i> Demo
                                </a>
                                <a href="https://github.com/Ahmed-KHI/SRP" class="btn btn-dark" target="_blank">
                                    <i class="fab fa-github"></i> Source Code
                                </a>
                            </div>
                            <div class="mt-3">
                                <small class="text-muted">
                                    Repository: <strong>Ahmed-KHI/SRP</strong> | 
                                    Deployment: <strong>Vercel</strong> | 
                                    Status: <strong>Live</strong>
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(template, ai_status=ai_status)

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    from datetime import datetime
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "ai_configured": is_ai_configured(),
        "framework": "Flask",
        "deployment": "Vercel Serverless",
        "repository": "https://github.com/Ahmed-KHI/SRP",
        "version": "1.0.0"
    })

@app.route('/demo')
def demo():
    """Demo page"""
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SRP Demo</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h2 class="mb-0">🎉 Smart Receipt Processor - Demo</h2>
                </div>
                <div class="card-body">
                    <div class="alert alert-success">
                        <h4><i class="fas fa-check-circle"></i> Deployment Successful!</h4>
                        <p>Your Smart Receipt Processor is running successfully on Vercel!</p>
                    </div>
                    
                    <h5>What this system can do:</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <ul>
                                <li>📸 Process receipt images using AI</li>
                                <li>🏪 Extract vendor, amount, and items</li>
                                <li>📊 Categorize expenses automatically</li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <ul>
                                <li>📈 Export to Excel and QuickBooks</li>
                                <li>🔌 Provide REST API access</li>
                                <li>🚀 Scale on Vercel serverless</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <a href="/" class="btn btn-primary">← Back to Home</a>
                        <a href="/api/status" class="btn btn-info">API Status</a>
                        <a href="https://github.com/Ahmed-KHI/SRP" class="btn btn-outline-dark" target="_blank">
                            View Code
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(template)

@app.route('/health')
def health():
    """Health check endpoint"""
    from datetime import datetime
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "service": "Smart Receipt Processor"
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "status": 404}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "status": 500}), 500

# This is what Vercel needs
application = app

if __name__ == "__main__":
    app.run(debug=True)
