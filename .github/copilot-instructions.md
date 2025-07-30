<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Smart Receipt Processor - AI-Powered Finance Automation

This project implements an intelligent receipt processing system that combines computer vision, OCR, and AI to automate expense categorization and bookkeeping workflows.

## Project Architecture

### Core Components
- **Receipt Processor**: Main orchestration engine (`src/core/receipt_processor.py`)
- **AI Vision**: GPT-4 Vision integration for intelligent receipt analysis (`src/core/ai_vision.py`)
- **OCR Engine**: Tesseract integration for text extraction (`src/core/ocr_engine.py`)
- **Categorizer**: AI-powered expense categorization (`src/core/categorizer.py`)

### Integrations
- **Excel Exporter**: Professional Excel export with charts (`src/integrations/excel_exporter.py`)
- **QuickBooks API**: Integration with QuickBooks Online (`src/integrations/quickbooks_api.py`)
- **Data Validator**: Comprehensive validation and quality control (`src/integrations/data_validator.py`)

### Data Models
- **Receipt**: Raw receipt data structure (`src/models/receipt.py`)
- **Expense**: Business expense models and rules (`src/models/expense.py`)

### Utilities
- **Config**: Environment and configuration management (`src/utils/config.py`)
- **Logger**: Centralized logging system (`src/utils/logger.py`)
- **Image Processor**: Image preprocessing and enhancement (`src/utils/image_processor.py`)

## Development Guidelines

### Code Style
- Follow PEP 8 conventions
- Use type hints for all function parameters and return values
- Include comprehensive docstrings for all classes and methods
- Use dataclasses for data structures where appropriate

### Error Handling
- Implement comprehensive error handling with logging
- Use custom exceptions where appropriate
- Provide graceful degradation when AI services are unavailable

### AI Integration Best Practices
- Always validate AI responses before processing
- Implement confidence scoring for all AI-generated results
- Provide fallback mechanisms when AI analysis fails
- Log all AI interactions for debugging and improvement

### Configuration Management
- Use environment variables for all sensitive configuration
- Provide sensible defaults for optional settings
- Validate configuration on startup
- Support both development and production environments

### Testing Strategy
- Write unit tests for all core functionality
- Include integration tests for AI services
- Test with various receipt formats and qualities
- Validate error handling and edge cases

## API Keys and Environment Setup

The system requires the following environment variables:
- `OPENAI_API_KEY`: Required for GPT-4 Vision analysis
- `QB_CLIENT_ID`, `QB_CLIENT_SECRET`: Optional for QuickBooks integration
- `TESSERACT_PATH`: Path to Tesseract executable (Windows)

See `.env.example` for complete configuration template.

## Business Logic

### Expense Categories
The system uses predefined categories in `config/expense_categories.json`:
- Office Supplies
- Meals & Entertainment  
- Travel
- Technology
- Marketing
- Utilities
- Professional Services
- Insurance
- Maintenance & Repairs
- Miscellaneous

### Categorization Logic
1. **Vendor-based**: Direct mapping of known vendors to categories
2. **Item-based**: Analysis of purchased items using keyword matching
3. **Text analysis**: Full receipt text analysis with confidence scoring
4. **Amount-based**: Heuristics based on expense amounts

### Data Validation
- Mandatory field validation (vendor, amount)
- Business rule enforcement
- Duplicate detection
- Confidence threshold validation
- Data quality assessment

## Common Patterns

### Processing Pipeline
```python
# 1. Image preprocessing
processed_image = image_processor.preprocess(image_path)

# 2. OCR text extraction
ocr_text = ocr_engine.extract_text(processed_image)

# 3. AI vision analysis
vision_result = vision_analyzer.analyze_receipt(processed_image, ocr_text)

# 4. Expense categorization
category = categorizer.categorize_expense(receipt)

# 5. Data validation
validation_result = validator.validate_processed_receipt(processed_receipt)
```

### Error Handling Pattern
```python
try:
    result = process_receipt(image_path)
    logger.info(f"Successfully processed: {result.vendor}")
    return result
except Exception as e:
    logger.error(f"Processing failed for {image_path}: {str(e)}")
    # Return default/fallback result or re-raise
```

### Configuration Access
```python
config = Config()
if not config.is_openai_configured():
    raise ValueError("OpenAI API key required")
```

## Integration Points

### QuickBooks API Flow
1. OAuth2 authorization flow
2. Token management and refresh
3. Expense creation with proper account mapping
4. Vendor management
5. Error handling and retry logic

### Excel Export Features
- Professional formatting with styles
- Summary sheets with analytics
- Charts and visualizations
- Template-based export
- Batch processing support

## Performance Considerations

- Image preprocessing optimizations
- Batch processing for multiple receipts
- Caching of AI responses where appropriate
- Efficient file handling for large images
- Memory management for batch operations

## Security Notes

- Never log sensitive data (API keys, tokens)
- Validate all file uploads
- Sanitize file paths
- Use secure temporary file handling
- Implement rate limiting for AI API calls
