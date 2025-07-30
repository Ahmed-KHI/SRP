"""
Tesseract OCR Auto-Installer for Windows
Automatically downloads and installs Tesseract OCR for receipt processing
"""

import subprocess
import sys
import os
import requests
from pathlib import Path
import tempfile

def check_tesseract_installed():
    """Check if Tesseract is already installed."""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract is already installed!")
            print(f"Version: {result.stdout.split()[1]}")
            return True
    except FileNotFoundError:
        pass
    
    # Check common installation paths
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"✅ Tesseract found at: {path}")
            return True
    
    return False

def download_tesseract():
    """Download Tesseract installer."""
    print("📥 Downloading Tesseract OCR installer...")
    
    # Tesseract Windows installer URL
    url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
    
    # Download to temp directory
    temp_dir = tempfile.gettempdir()
    installer_path = os.path.join(temp_dir, "tesseract-installer.exe")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(installer_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}%", end='', flush=True)
        
        print(f"\n✅ Downloaded to: {installer_path}")
        return installer_path
        
    except Exception as e:
        print(f"❌ Download failed: {str(e)}")
        return None

def install_tesseract(installer_path):
    """Run Tesseract installer."""
    print("\n🔧 Starting Tesseract installation...")
    print("📋 Installation Instructions:")
    print("1. Click 'Next' through the installer")
    print("2. Accept the license agreement")
    print("3. Use default installation path: C:\\Program Files\\Tesseract-OCR\\")
    print("4. Select 'Additional language data' if you need other languages")
    print("5. Click 'Install' and wait for completion")
    
    try:
        # Run installer (will open GUI)
        subprocess.run([installer_path], check=True)
        print("✅ Installer launched successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to launch installer: {str(e)}")
        return False

def update_env_file():
    """Update .env file with Tesseract path."""
    env_file = Path(".env")
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        if 'TESSERACT_PATH' not in content:
            with open(env_file, 'a') as f:
                f.write(f'\nTESSERACT_PATH={tesseract_path}\n')
            print(f"✅ Added TESSERACT_PATH to .env file")
    else:
        print("⚠️  .env file not found - you may need to set TESSERACT_PATH manually")

def test_installation():
    """Test if Tesseract installation was successful."""
    print("\n🧪 Testing Tesseract installation...")
    
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract installation successful!")
            print(f"Version: {result.stdout.split()[1]}")
            return True
    except FileNotFoundError:
        pass
    
    # If not in PATH, check default location
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_path):
        try:
            result = subprocess.run([tesseract_path, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Tesseract installed at: {tesseract_path}")
                print(f"Version: {result.stdout.split()[1]}")
                return True
        except Exception:
            pass
    
    print("❌ Tesseract installation verification failed")
    print("📋 Manual verification steps:")
    print("1. Restart your command prompt/terminal")
    print("2. Try: tesseract --version")
    print("3. Check installation at: C:\\Program Files\\Tesseract-OCR\\")
    
    return False

def main():
    """Main installation process."""
    print("🔧 Tesseract OCR Auto-Installer")
    print("=" * 40)
    
    # Check if already installed
    if check_tesseract_installed():
        print("✅ Tesseract is ready to use!")
        return
    
    print("📦 Tesseract OCR not found. Installing...")
    
    # Download installer
    installer_path = download_tesseract()
    if not installer_path:
        print("❌ Download failed. Please install manually:")
        print("https://github.com/UB-Mannheim/tesseract/wiki")
        return
    
    # Run installer
    if install_tesseract(installer_path):
        print("\n⏳ Please complete the installation in the opened window...")
        input("Press Enter after installation is complete...")
        
        # Update configuration
        update_env_file()
        
        # Test installation
        if test_installation():
            print("\n🎉 Tesseract installation complete!")
            print("\n📋 Next steps:")
            print("1. Restart your terminal/command prompt")
            print("2. Test receipt processing: python demo_with_ocr.py")
            print("3. Process real receipts: python main.py process receipt.jpg")
        else:
            print("\n⚠️  Installation may need manual verification")
    
    # Cleanup
    try:
        os.remove(installer_path)
        print(f"🧹 Cleaned up installer file")
    except:
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
    except Exception as e:
        print(f"\n❌ Installation error: {str(e)}")
        print("Please install manually from: https://github.com/UB-Mannheim/tesseract/wiki")
