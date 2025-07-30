# 🧾 Smart Receipt Processor

An AI-powered receipt processing system that combines computer vision, OCR, and intelligent analysis to automate expense categorization and bookkeeping workflows.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/smart-receipt-processor)

## ✨ Features

- 🤖 **AI Vision Analysis** - Google Gemini 2.0 Flash integration for intelligent receipt parsing
- 📊 **Automatic Categorization** - Smart expense classification with confidence scoring  
- 📈 **Analytics Dashboard** - Real-time insights and expense tracking
- 🌐 **Web Interface** - Modern Bootstrap UI with drag-drop uploads
- � **REST API** - Programmatic access for integrations
- 🔍 **OCR Technology**: Tesseract OCR for accurate text extraction
- ⚡ **Error Reduction**: Eliminates manual data entry errors

## Quick Start

### Prerequisites
- Python 3.8+
- Tesseract OCR installed
- OpenAI API key
- QuickBooks Developer Account (optional)

### Installation

1. Clone or download this project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the application:
```bash
python main.py
```

## Usage

### Basic Receipt Processing
```python
from smart_receipt_processor import ReceiptProcessor

processor = ReceiptProcessor()
result = processor.process_receipt("path/to/receipt.jpg")
print(result.expense_category)  # e.g., "Office Supplies"
print(result.amount)           # e.g., 45.99
```

### Batch Processing
```python
processor.process_folder("receipts/", output_excel="expenses.xlsx")
```

## Project Structure

```
smart-receipt-processor/
├── src/
│   ├── core/
│   │   ├── receipt_processor.py    # Main processing engine
│   │   ├── ai_vision.py           # GPT-4 Vision integration
│   │   ├── ocr_engine.py          # Tesseract OCR wrapper
│   │   └── categorizer.py         # Expense categorization logic
│   ├── integrations/
│   │   ├── excel_exporter.py      # Excel automation
│   │   ├── quickbooks_api.py      # QuickBooks integration
│   │   └── data_validator.py      # Data validation
│   ├── models/
│   │   ├── receipt.py             # Receipt data models
│   │   └── expense.py             # Expense data models
│   └── utils/
│       ├── image_processor.py     # Image preprocessing
│       ├── config.py              # Configuration management
│       └── logger.py              # Logging utilities
├── tests/
├── config/
│   └── expense_categories.json    # Predefined categories
├── examples/
│   └── sample_receipts/           # Sample receipt images
├── main.py                        # Main application entry
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration

The system uses a configuration file for expense categories and business rules. Customize `config/expense_categories.json` to match your business needs.

## API Integration

### QuickBooks Setup
1. Create a QuickBooks Developer account
2. Get your Client ID and Secret
3. Configure OAuth2 flow (see examples/)

### OpenAI Setup
1. Get an OpenAI API key
2. Add to .env file
3. Configure model preferences in config.py

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please open a GitHub issue or contact the development team.
