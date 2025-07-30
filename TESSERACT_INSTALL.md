# Tesseract OCR Installation Guide

## For Windows Users

### Option 1: Automated Download (Recommended)
Run this PowerShell script to automatically download and install Tesseract:

```powershell
# Download Tesseract installer
$url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0/tesseract-ocr-w64-setup-5.3.0.20221214.exe"
$output = "$env:TEMP\tesseract-installer.exe"

Write-Host "Downloading Tesseract OCR installer..."
Invoke-WebRequest -Uri $url -OutFile $output

Write-Host "Starting Tesseract installation..."
Start-Process -FilePath $output -Wait

Write-Host "Installation complete! Please restart your terminal."
```

### Option 2: Manual Download
1. **Visit:** https://github.com/UB-Mannheim/tesseract/wiki
2. **Download:** Latest Windows installer (tesseract-ocr-w64-setup-*.exe)
3. **Run installer** and follow the setup wizard
4. **Default installation path:** `C:\Program Files\Tesseract-OCR\`

### Option 3: Using Package Manager
If you have Chocolatey installed:
```powershell
choco install tesseract
```

If you have Scoop installed:
```powershell
scoop install tesseract
```

## Verification Steps

After installation, verify Tesseract is working:

```bash
# Check version
tesseract --version

# Test OCR on sample image
tesseract sample.png output.txt
```

## Configuration for Receipt Processor

The system will automatically detect Tesseract in these locations:
1. `C:\Program Files\Tesseract-OCR\tesseract.exe` (default)
2. System PATH environment variable
3. Custom path in `.env` file: `TESSERACT_PATH=your_path_here`

## Language Packs (Optional)

For better accuracy with different languages:
```bash
# Download additional language packs during installation
# Or add them later from: https://github.com/tesseract-ocr/tessdata
```

## Testing Receipt OCR

Once installed, test with your receipt processor:
```bash
python main.py process receipt.jpg
```
