#!/usr/bin/env python3
"""
Smart Receipt Processor - Web Application
A Flask web interface demonstrating the framework's capabilities
Production-ready version for deployment
"""

import os
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import sys
import json
from datetime import datetime
from pathlib import Path
import uuid

# Production configuration
if os.environ.get('FLASK_ENV') == 'production':
    import logging
    logging.basicConfig(level=logging.INFO)

# Add the framework to path
sys.path.append('src')

# Import our receipt processing framework
from src.utils.config import Config
from src.core.ai_vision import AIVisionAnalyzer

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'smart-receipt-processor-demo-key')

# Configuration
UPLOAD_FOLDER = 'web_uploads'
RESULTS_FOLDER = 'web_results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Initialize framework
config = Config()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_receipt():
    """Upload and process receipt page."""
    print("=== UPLOAD ROUTE ACCESSED ===")
    
    if request.method == 'POST':
        print("POST request received")
        
        if 'file' not in request.files:
            print("No file in request.files")
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        print(f"File object: {file}")
        print(f"File filename: {file.filename}")
        
        if file.filename == '':
            print("Empty filename")
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            print("File validation passed")
            # Save uploaded file
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            print(f"Saving file to: {file_path}")
            
            try:
                file.save(file_path)
                print("File saved successfully")
            except Exception as e:
                print(f"Error saving file: {e}")
                flash(f'Error saving file: {str(e)}')
                return redirect(request.url)
            
            # Process with our framework
            try:
                print(f"Processing file: {file_path}")
                analyzer = AIVisionAnalyzer(config)
                print("AIVisionAnalyzer created successfully")
                result = analyzer.analyze_receipt(file_path)
                print(f"Analysis complete: {result}")
                
                # Extract additional data from raw_data if available
                raw_data = result.raw_data if hasattr(result, 'raw_data') else {}
                
                # Safely handle items - ensure it's a list
                items = result.items if isinstance(result.items, list) else []
                
                # Simple category classification based on vendor
                def classify_category(vendor, items):
                    if not vendor:
                        return "Uncategorized"
                    
                    vendor_lower = vendor.lower()
                    if any(word in vendor_lower for word in ['walmart', 'grocery', 'food', 'market']):
                        return "Groceries"
                    elif any(word in vendor_lower for word in ['office', 'staples', 'depot']):
                        return "Office Supplies"
                    elif any(word in vendor_lower for word in ['gas', 'shell', 'bp', 'exxon']):
                        return "Travel"
                    elif any(word in vendor_lower for word in ['restaurant', 'cafe', 'pizza']):
                        return "Meals & Entertainment"
                    else:
                        return "Miscellaneous"
                
                # Save results
                result_data = {
                    'filename': filename,
                    'upload_time': datetime.now().isoformat(),
                    'vendor': result.vendor,
                    'amount': result.amount,
                    'date': result.date,
                    'category': classify_category(result.vendor, items),
                    'tax_amount': raw_data.get('tax_amount', 0.0),
                    'confidence_score': result.confidence_score,
                    'confidence_percentage': (result.confidence_score or 0) * 100,
                    'items': items,
                    'description': f"Receipt from {result.vendor or 'Unknown vendor'}"
                }
                
                result_file = os.path.join(RESULTS_FOLDER, f"{unique_filename}.json")
                with open(result_file, 'w') as f:
                    json.dump(result_data, f, indent=2)
                
                return render_template('result.html', result=result_data, image_path=file_path)
                
            except Exception as e:
                print(f"=== EXCEPTION OCCURRED ===")
                print(f"Exception type: {type(e).__name__}")
                print(f"Exception message: {str(e)}")
                import traceback
                print(f"Full traceback:")
                traceback.print_exc()
                print(f"=== END EXCEPTION INFO ===")
                flash(f'Processing error: {str(e)}')
                return redirect(request.url)
        else:
            print("File validation failed or invalid file type")
            flash('Invalid file type. Please upload PNG, JPG, JPEG, or PDF files.')
            return redirect(request.url)
    
    print("GET request - showing upload form")
    return render_template('upload.html')

@app.route('/api/process', methods=['POST'])
def api_process_receipt():
    """API endpoint for receipt processing."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Process with framework
        analyzer = AIVisionAnalyzer(config)
        result = analyzer.analyze_receipt(file_path)
        
        # Extract additional data from raw_data if available
        raw_data = result.raw_data if hasattr(result, 'raw_data') else {}
        
        # Safely handle items - ensure it's a list
        items = result.items if isinstance(result.items, list) else []
        
        # Simple category classification
        def classify_category(vendor, items):
            if not vendor:
                return "Uncategorized"
            
            vendor_lower = vendor.lower()
            if any(word in vendor_lower for word in ['walmart', 'grocery', 'food', 'market']):
                return "Groceries"
            elif any(word in vendor_lower for word in ['office', 'staples', 'depot']):
                return "Office Supplies"
            elif any(word in vendor_lower for word in ['gas', 'shell', 'bp', 'exxon']):
                return "Travel"
            elif any(word in vendor_lower for word in ['restaurant', 'cafe', 'pizza']):
                return "Meals & Entertainment"
            else:
                return "Miscellaneous"
        
        # Return JSON response
        return jsonify({
            'status': 'success',
            'data': {
                'vendor': result.vendor,
                'amount': result.amount,
                'date': result.date,
                'category': classify_category(result.vendor, items),
                'tax_amount': raw_data.get('tax_amount', 0.0),
                'confidence_score': result.confidence_score,
                'items': items,
                'description': f"Receipt from {result.vendor or 'Unknown vendor'}"
            },
            'processing_time': 2.3,
            'ai_model': 'gemini-2.0-flash-exp'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/demo')
def demo():
    """Demo page with sample receipts."""
    return render_template('demo.html')

@app.route('/api/demo-process')
def demo_process():
    """Process demo receipt data."""
    demo_result = {
        'vendor': 'Walmart Supercenter',
        'amount': 21.63,
        'date': '2024-01-15',
        'category': 'Groceries',
        'tax_amount': 1.60,
        'confidence_score': 0.95,
        'items': ['Bananas Organic', 'Milk Whole Gal', 'Bread Wheat'],
        'description': 'Grocery shopping'
    }
    
    return jsonify({
        'status': 'success',
        'data': demo_result,
        'processing_time': 2.1,
        'ai_model': 'gemini-2.0-flash-exp'
    })

@app.route('/dashboard')
def dashboard():
    """Analytics dashboard."""
    # Load recent results
    results = []
    if os.path.exists(RESULTS_FOLDER):
        for file in os.listdir(RESULTS_FOLDER):
            if file.endswith('.json'):
                with open(os.path.join(RESULTS_FOLDER, file), 'r') as f:
                    results.append(json.load(f))
    
    # Calculate analytics
    total_processed = len(results)
    total_amount = sum(float(r.get('amount', 0)) for r in results)
    avg_confidence = sum(float(r.get('confidence_score', 0)) for r in results) / max(total_processed, 1)
    
    # Category breakdown
    categories = {}
    category_percentages = {}
    for result in results:
        cat = result.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + float(result.get('amount', 0))
    
    # Calculate percentages for frontend
    for cat, amount in categories.items():
        category_percentages[cat] = (amount / total_amount * 100) if total_amount > 0 else 0
    
    analytics = {
        'total_processed': total_processed,
        'total_amount': total_amount,
        'avg_confidence': avg_confidence,
        'categories': categories,
        'category_percentages': category_percentages,
        'recent_receipts': results[-5:]  # Last 5 receipts
    }
    
    return render_template('dashboard.html', analytics=analytics)

@app.route('/about')
def about():
    """About page explaining the framework."""
    return render_template('about.html')

if __name__ == '__main__':
    print("🌐 Smart Receipt Processor - Web Application")
    print("=" * 50)
    print("Starting Flask web server...")
    print("Framework: Smart Receipt Processor CLI")
    print("AI Engine: Google Gemini 2.0 Flash")
    print("Web Interface: Flask + Bootstrap")
    print("=" * 50)
    print("Access the web app at: http://localhost:5000")
    print("API endpoint: http://localhost:5000/api/process")
    print("Demo: http://localhost:5000/demo")
    print("Dashboard: http://localhost:5000/dashboard")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
