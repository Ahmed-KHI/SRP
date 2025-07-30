"""
Smart Receipt Processor - Quick Demo

This script demonstrates the key features of the Smart Receipt Processor
without requiring actual API keys for initial testing.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demo_without_api():
    """Demonstrate the system without requiring API keys."""
    print("\n🧾 Smart Receipt Processor - Demo Mode")
    print("=" * 50)
    
    try:
        from src.utils.config import Config
        from src.utils.logger import setup_logger
        from src.models.receipt import Receipt, ProcessedReceipt
        
        # Setup basic logging
        logger = setup_logger("demo", "INFO")
        logger.info("Starting Smart Receipt Processor demo")
        
        # Show configuration (without sensitive data)
        print("\n📋 Configuration Status:")
        config = Config()
        config_status = config.to_dict()
        
        for key, value in config_status.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {value}")
        
        # Demonstrate data models
        print("\n🏗️ Data Models Demo:")
        
        # Create sample receipt
        sample_receipt = Receipt(
            vendor="Demo Coffee Shop",
            amount=12.50,
            date="2024-07-29",
            items=["Coffee", "Pastry"],
            ocr_text="DEMO COFFEE SHOP\n07/29/2024\nCoffee  $8.50\nPastry  $4.00\nTotal   $12.50"
        )
        
        print(f"📄 Sample Receipt:")
        print(f"  Vendor: {sample_receipt.vendor}")
        print(f"  Amount: ${sample_receipt.amount}")
        print(f"  Date: {sample_receipt.date}")
        print(f"  Items: {', '.join(sample_receipt.items)}")
        print(f"  Valid: {sample_receipt.is_valid}")
        
        # Create processed receipt
        processed = ProcessedReceipt(
            receipt=sample_receipt,
            category="Meals & Entertainment",
            confidence_score=0.95,
            description="Demo Coffee Shop - Business meal"
        )
        
        print(f"\n📊 Processed Receipt:")
        print(f"  Category: {processed.category}")
        print(f"  Confidence: {processed.confidence_score:.2f}")
        print(f"  Status: {processed.status}")
        print(f"  Requires Review: {'Yes' if processed.requires_review else 'No'}")
        
        # Show Excel export format
        print(f"\n📈 Excel Export Preview:")
        excel_data = processed.to_excel_row()
        for key, value in list(excel_data.items())[:6]:  # Show first 6 fields
            print(f"  {key}: {value}")
        
        print("\n✨ Features Available:")
        features = [
            "🤖 AI-powered receipt analysis (requires OpenAI API)",
            "🔍 OCR text extraction (requires Tesseract)",
            "📊 Excel export with charts and analytics",
            "💼 QuickBooks integration (requires API setup)",
            "✅ Data validation and quality control",
            "📁 Batch processing capabilities",
            "🏷️ Intelligent expense categorization",
            "📈 Business reporting and insights"
        ]
        
        for feature in features:
            print(f"  {feature}")
        
        print("\n🚀 Getting Started:")
        print("1. Install Tesseract OCR from: https://github.com/tesseract-ocr/tesseract")
        print("2. Get OpenAI API key from: https://platform.openai.com/")
        print("3. Copy .env.example to .env and add your API keys")
        print("4. Run: python main.py path/to/receipt.jpg")
        
        print("\n📖 Documentation:")
        print("- README.md - Complete setup and usage guide")
        print("- examples/ - Sample code and usage examples")
        print("- config/ - Expense categories and business rules")
        
        print("\n✅ Demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install requirements: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Demo error: {e}")

def show_project_structure():
    """Display the project structure."""
    print("\n📁 Project Structure:")
    print("""
smart-receipt-processor/
├── 📄 main.py                     # Main application entry
├── 📄 requirements.txt            # Python dependencies  
├── 📄 README.md                   # Documentation
├── 📄 .env.example                # Environment template
├── 📁 src/                        # Source code
│   ├── 📁 core/                   # Core processing
│   │   ├── receipt_processor.py   # Main orchestrator
│   │   ├── ai_vision.py          # GPT-4 Vision
│   │   ├── ocr_engine.py         # Tesseract OCR
│   │   └── categorizer.py        # AI categorization
│   ├── 📁 integrations/          # External integrations
│   │   ├── excel_exporter.py     # Excel automation
│   │   ├── quickbooks_api.py     # QuickBooks API
│   │   └── data_validator.py     # Quality control
│   ├── 📁 models/                # Data models
│   │   ├── receipt.py            # Receipt structures
│   │   └── expense.py            # Business models
│   └── 📁 utils/                 # Utilities
│       ├── config.py             # Configuration
│       ├── logger.py             # Logging
│       └── image_processor.py    # Image preprocessing
├── 📁 config/                    # Configuration files
│   └── expense_categories.json   # Business categories
├── 📁 examples/                  # Usage examples
│   ├── basic_processing.py       # Simple example
│   └── batch_processing.py       # Batch example
└── 📁 tests/                     # Test suite
    ├── test_receipt_processor.py  # Core tests
    └── conftest.py               # Test configuration
    """)

if __name__ == "__main__":
    print("🎯 Smart Receipt Processor - AI-Powered Finance Automation")
    print("🏢 Designed for office environments to streamline expense processing")
    
    show_project_structure()
    demo_without_api()
    
    print(f"\n🎉 Project setup complete! Ready for development.")
    print(f"💡 Next: Add your API keys to .env and start processing receipts!")
