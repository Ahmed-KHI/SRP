# Smart Receipt Processor
# Python package initialization

"""
Smart Receipt Processor - AI-Powered Finance Automation

This package provides intelligent receipt processing using GPT-4 Vision, OCR,
and automated accounting integration.
"""

__version__ = "1.0.0"
__author__ = "Smart Receipt Processor Team"
__email__ = "support@smartreceiptprocessor.com"

# Core imports for easy access
from .core.receipt_processor import ReceiptProcessor
from .models.receipt import Receipt, ProcessedReceipt
from .utils.config import Config
from .utils.logger import setup_logger

__all__ = [
    'ReceiptProcessor',
    'Receipt', 
    'ProcessedReceipt',
    'Config',
    'setup_logger'
]
