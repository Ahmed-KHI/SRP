#!/usr/bin/env python3
"""
Smart Receipt Processor - Minimal Web Application
Simplified version for Vercel deployment with minimal dependencies
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# Basic configuration
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'smart-receipt-processor-demo-key')

# Check if AI is configured
def is_ai_configured():
    """Check if Gemini AI is configured"""
    return bool(os.environ.get('GEMINI_API_KEY'))

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        ai_status = "configured" if is_ai_configured() else "not configured"
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Smart Receipt Processor</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h1 class="card-title mb-0">
                                    <i class="fas fa-receipt"></i> Smart Receipt Processor
                                </h1>
                            </div>
                            <div class="card-body">
                                <div class="alert alert-info">
                                    <h4><i class="fas fa-rocket"></i> Deployment Successful!</h4>
                                    <p>Your Smart Receipt Processor is now live on Vercel!</p>
                                    <ul>
                                        <li><strong>Framework:</strong> Flask + Google Gemini AI</li>
                                        <li><strong>AI Status:</strong> {ai_status}</li>
                                        <li><strong>Deployment:</strong> Vercel Serverless</li>
                                        <li><strong>Repository:</strong> <a href="https://github.com/Ahmed-KHI/SRP" target="_blank">GitHub.com/Ahmed-KHI/SRP</a></li>
                                    </ul>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="card border-success">
                                            <div class="card-body">
                                                <h5><i class="fas fa-check-circle text-success"></i> Features</h5>
                                                <ul>
                                                    <li>AI-powered receipt analysis</li>
                                                    <li>Expense categorization</li>
                                                    <li>Web interface & REST API</li>
                                                    <li>Professional documentation</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="card border-info">
                                            <div class="card-body">
                                                <h5><i class="fas fa-cog text-info"></i> Tech Stack</h5>
                                                <ul>
                                                    <li>Python Flask</li>
                                                    <li>Google Gemini AI</li>
                                                    <li>Bootstrap UI</li>
                                                    <li>Vercel Deployment</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mt-4">
                                    <a href="/api/status" class="btn btn-primary">
                                        <i class="fas fa-api"></i> API Status
                                    </a>
                                    <a href="/demo" class="btn btn-success">
                                        <i class="fas fa-play"></i> Demo Mode
                                    </a>
                                    <a href="https://github.com/Ahmed-KHI/SRP" class="btn btn-outline-dark" target="_blank">
                                        <i class="fab fa-github"></i> View Source
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    try:
        status = {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "ai_configured": is_ai_configured(),
            "framework": "Flask",
            "deployment": "Vercel",
            "repository": "https://github.com/Ahmed-KHI/SRP"
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/demo')
def demo():
    """Demo page"""
    try:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SRP Demo</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="card">
                    <div class="card-header">
                        <h2>Smart Receipt Processor - Demo</h2>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-success">
                            <h4>🎉 Deployment Successful!</h4>
                            <p>Your Smart Receipt Processor is working on Vercel!</p>
                        </div>
                        
                        <h5>What this system can do:</h5>
                        <ul>
                            <li>Process receipt images using AI</li>
                            <li>Extract vendor, amount, and items</li>
                            <li>Categorize expenses automatically</li>
                            <li>Export to Excel and QuickBooks</li>
                            <li>Provide REST API access</li>
                        </ul>
                        
                        <a href="/" class="btn btn-primary">← Back to Home</a>
                        <a href="/api/status" class="btn btn-info">API Status</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
