"""
Smart Receipt Processor - Standalone Web Application
A Flask web interface demonstrating the framework's capabilities without requiring all dependencies
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from pathlib import Path
import uuid

app = Flask(__name__)
app.secret_key = 'smart-receipt-processor-demo-key'

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_receipt():
    """Upload and process receipt."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Generate unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}"
                filename = secure_filename(f"{unique_filename}_{file.filename}")
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                # Simulate AI processing for demo (since we can't import the full framework)
                def simulate_processing(vendor_name="Demo Store"):
                    return {
                        'vendor': vendor_name,
                        'amount': 45.67,
                        'date': '2025-01-15',
                        'items': ['Coffee - $4.50', 'Sandwich - $8.99', 'Tax - $2.18'],
                        'confidence_score': 0.95,
                        'raw_data': {'tax_amount': 2.18}
                    }
                
                # Simulate processing result
                result = simulate_processing()
                
                # Simple category classification
                def classify_category(vendor, items):
                    if not vendor:
                        return "Uncategorized"
                    
                    vendor_lower = vendor.lower()
                    if any(word in vendor_lower for word in ['demo', 'store', 'shop']):
                        return "Retail"
                    elif any(word in vendor_lower for word in ['coffee', 'restaurant', 'cafe']):
                        return "Meals & Entertainment"
                    else:
                        return "Miscellaneous"
                
                # Save results
                result_data = {
                    'filename': filename,
                    'upload_time': datetime.now().isoformat(),
                    'vendor': result['vendor'],
                    'amount': result['amount'],
                    'date': result['date'],
                    'category': classify_category(result['vendor'], result['items']),
                    'tax_amount': result['raw_data'].get('tax_amount', 0.0),
                    'confidence_score': result['confidence_score'],
                    'confidence_percentage': (result['confidence_score'] or 0) * 100,
                    'items': result['items'] or [],
                    'description': f"Receipt from {result['vendor'] or 'Unknown vendor'}"
                }
                
                result_file = os.path.join(RESULTS_FOLDER, f"{unique_filename}.json")
                with open(result_file, 'w') as f:
                    json.dump(result_data, f, indent=2)
                
                return render_template('result.html', result=result_data, image_path=file_path)
                
            except Exception as e:
                flash(f'Processing error: {str(e)}')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload PNG, JPG, JPEG, or PDF files.')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/demo')
def demo():
    """Demo page with sample functionality."""
    return render_template('demo.html')

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

# API Endpoints
@app.route('/api/process', methods=['POST'])
def api_process_receipt():
    """API endpoint for receipt processing."""
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file and allowed_file(file.filename):
        try:
            # Save uploaded file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"api_{timestamp}_{uuid.uuid4().hex[:8]}"
            filename = secure_filename(f"{unique_filename}_{file.filename}")
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Simulate processing for demo
            result = {
                'vendor': 'API Demo Store',
                'amount': 67.89,
                'date': '2025-01-15',
                'items': ['API Test Item - $65.71', 'Tax - $2.18'],
                'confidence_score': 0.92,
                'raw_data': {'tax_amount': 2.18}
            }
            
            # Simple category classification
            def classify_category(vendor, items):
                if not vendor:
                    return "Uncategorized"
                
                vendor_lower = vendor.lower()
                if any(word in vendor_lower for word in ['api', 'demo', 'test']):
                    return "API Testing"
                else:
                    return "Miscellaneous"
            
            # Return JSON response
            return jsonify({
                'status': 'success',
                'data': {
                    'vendor': result['vendor'],
                    'amount': result['amount'],
                    'date': result['date'],
                    'category': classify_category(result['vendor'], result['items']),
                    'tax_amount': result['raw_data'].get('tax_amount', 0.0),
                    'confidence_score': result['confidence_score'],
                    'items': result['items'] or [],
                    'description': f"Receipt from {result['vendor'] or 'Unknown vendor'}"
                },
                'processing_time': 1.8,
                'ai_model': 'gemini-2.0-flash-exp (simulated)'
            })
            
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400

if __name__ == '__main__':
    print("🚀 Smart Receipt Processor - Web Demo")
    print("=" * 50)
    print("📊 Framework Status: Demo Mode (Simulated AI)")
    print("🌐 Web Interface: http://localhost:5000")
    print("📈 Dashboard: http://localhost:5000/dashboard")
    print("🔧 API: http://localhost:5000/api/process")
    print("=" * 50)
    print("Note: This is a demo version with simulated AI processing.")
    print("To use real AI processing, ensure Gemini API key is configured.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
