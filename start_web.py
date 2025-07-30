"""
Web Application Launcher
Quick start script for the Smart Receipt Processor web interface
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed."""
    required_packages = ['flask', 'werkzeug', 'google-generativeai']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def start_web_app():
    """Start the Flask web application."""
    print("🌐 Smart Receipt Processor - Web Application Launcher")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        return
    
    print("✅ All dependencies installed")
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  Warning: .env file not found")
        print("   Some features may not work without API configuration")
    else:
        print("✅ Configuration file found")
    
    print("\n🚀 Starting web application...")
    print("   Framework: Smart Receipt Processor CLI")
    print("   AI Engine: Google Gemini 2.0 Flash")
    print("   Web Interface: Flask + Bootstrap")
    print("   Port: 5000")
    
    try:
        # Start the Flask app
        print("\n📡 Server starting...")
        print("   Local URL: http://localhost:5000")
        print("   Network URL: http://0.0.0.0:5000")
        print("\n💡 Features available:")
        print("   • Upload & Process Receipts")
        print("   • Live AI Demo")
        print("   • Analytics Dashboard")
        print("   • REST API Endpoints")
        
        print("\n🎯 Ready! Opening web browser...")
        
        # Wait a moment then open browser
        time.sleep(2)
        try:
            webbrowser.open('http://localhost:5000')
        except:
            print("   (Could not auto-open browser)")
        
        # Start Flask
        subprocess.run([sys.executable, 'app.py'], check=True)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Web application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting web application: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure Flask is installed: pip install flask")
        print("2. Check port 5000 is not in use")
        print("3. Verify Python version compatibility")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    start_web_app()
