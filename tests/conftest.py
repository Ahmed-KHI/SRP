# Test Configuration
# This file contains test-specific settings and sample data

import os
import tempfile
from pathlib import Path

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_DATA_DIR.mkdir(exist_ok=True)

# Sample receipt data for testing
SAMPLE_RECEIPTS = [
    {
        "vendor": "Staples",
        "amount": 45.99,
        "date": "2024-01-15",
        "category": "Office Supplies",
        "items": ["Notebooks", "Pens", "Stapler"],
        "confidence": 0.95
    },
    {
        "vendor": "Starbucks",
        "amount": 12.50,
        "date": "2024-01-16", 
        "category": "Meals & Entertainment",
        "items": ["Coffee", "Pastry"],
        "confidence": 0.87
    },
    {
        "vendor": "Shell Gas Station",
        "amount": 65.00,
        "date": "2024-01-17",
        "category": "Travel",
        "items": ["Gasoline"],
        "confidence": 0.92
    }
]

# Test configuration values
TEST_CONFIG = {
    "OPENAI_API_KEY": "test_key_123",
    "OPENAI_MODEL": "gpt-4-vision-preview",
    "MIN_CONFIDENCE_SCORE": 0.8,
    "AUTO_SAVE": False,
    "LOG_LEVEL": "DEBUG"
}

# Mock OCR text samples
SAMPLE_OCR_TEXT = {
    "good_quality": """
    STAPLES
    123 Main Street
    Anytown, ST 12345
    
    Date: 01/15/2024
    
    Notebooks (3)      $15.99
    Pens (pack)        $8.99
    Stapler            $21.01
    
    Subtotal:          $45.99
    Tax:               $0.00
    Total:             $45.99
    
    Thank you!
    """,
    
    "poor_quality": """
    ST@PL3S
    123 M@in Str33t
    
    D@t3: 01/15/2024
    
    N0t3b00ks (3)      $15.99
    P3ns (p@ck)        $8.99
    St@pl3r            $21.01
    
    T0t@l:             $45.99
    """,
    
    "minimal": """
    STORE NAME
    $25.99
    01/15/2024
    """
}

def create_test_image(name: str = "test_receipt.jpg") -> str:
    """Create a simple test image file."""
    from PIL import Image
    import numpy as np
    
    # Create a simple white image with some text-like patterns
    img_array = np.ones((400, 600, 3), dtype=np.uint8) * 255
    
    # Add some dark rectangles to simulate text
    img_array[50:70, 50:200] = 0    # Header
    img_array[100:120, 50:150] = 0  # Line 1
    img_array[140:160, 50:180] = 0  # Line 2
    img_array[180:200, 50:120] = 0  # Line 3
    
    img = Image.fromarray(img_array)
    
    # Save to test data directory
    image_path = TEST_DATA_DIR / name
    img.save(image_path)
    
    return str(image_path)

def get_temp_file(suffix: str = ".xlsx") -> str:
    """Get a temporary file path for testing."""
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    temp_file.close()
    return temp_file.name

def cleanup_test_files():
    """Clean up test files and directories."""
    import shutil
    
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)

# Pytest fixtures
import pytest

@pytest.fixture
def sample_receipt_data():
    """Provide sample receipt data for testing."""
    return SAMPLE_RECEIPTS[0].copy()

@pytest.fixture  
def sample_ocr_text():
    """Provide sample OCR text for testing."""
    return SAMPLE_OCR_TEXT["good_quality"]

@pytest.fixture
def test_image_path():
    """Provide a test image file."""
    image_path = create_test_image()
    yield image_path
    # Cleanup
    if os.path.exists(image_path):
        os.remove(image_path)

@pytest.fixture
def temp_excel_file():
    """Provide a temporary Excel file path."""
    file_path = get_temp_file(".xlsx")
    yield file_path
    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)
