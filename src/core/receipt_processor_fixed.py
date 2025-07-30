"""
Receipt Processor - Core Processing Engine

This module coordinates the entire receipt processing workflow:
1. Image preprocessing and OCR text extraction
2. AI-powered analysis using GPT-4 Vision
3. Expense categorization and data validation
4. Integration with Excel and QuickBooks
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import List, Optional, Dict
import logging
from datetime import datetime

from core.ai_vision import AIVisionAnalyzer
from core.ocr_engine import OCREngine
from core.categorizer import ExpenseCategorizer
from models.receipt import Receipt, ProcessedReceipt
from integrations.excel_exporter import ExcelExporter
from integrations.quickbooks_api import QuickBooksAPI
from utils.image_processor import ImageProcessor
from utils.config import Config

logger = logging.getLogger(__name__)

class ReceiptProcessor:
    """Main receipt processing engine that orchestrates all components."""
    
    def __init__(self, config: Config):
        """Initialize the receipt processor with required components."""
        self.config = config
        self.image_processor = ImageProcessor(config)
        self.ocr_engine = OCREngine(config)
        self.vision_analyzer = AIVisionAnalyzer(config)
        self.categorizer = ExpenseCategorizer(config)
        self.excel_exporter = ExcelExporter(config)
        self.quickbooks_api = QuickBooksAPI(config) if config.QB_CLIENT_ID else None
        
        logger.info("Receipt processor initialized successfully")
    
    def process_receipt(self, image_path: str) -> ProcessedReceipt:
        """
        Process a single receipt image and extract expense data.
        
        Args:
            image_path: Path to the receipt image file
            
        Returns:
            ProcessedReceipt object with extracted data
        """
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Receipt image not found: {image_path}")
            
            logger.info(f"Processing receipt: {image_path}")
            
            # Step 1: Preprocess image
            processed_image = self.image_processor.process_image(str(image_path))
            
            # Step 2: Extract text using OCR
            ocr_text = self.ocr_engine.extract_text(processed_image)
            
            # Step 3: Analyze with AI vision
            vision_result = self.vision_analyzer.analyze_receipt(str(image_path))
            
            # Step 4: Categorize expense
            category = self.categorizer.categorize_expense(
                vendor=vision_result.vendor,
                amount=vision_result.amount,
                description=vision_result.description
            )
            
            # Step 5: Create processed receipt
            processed_receipt = ProcessedReceipt(
                original_image_path=str(image_path),
                vendor=vision_result.vendor,
                amount=vision_result.amount,
                date=vision_result.date,
                category=category,
                description=vision_result.description,
                tax_amount=vision_result.tax_amount,
                confidence_score=vision_result.confidence_score,
                ocr_text=ocr_text,
                processing_timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"Successfully processed receipt: {vision_result.vendor} - ${vision_result.amount}")
            return processed_receipt
            
        except Exception as e:
            logger.error(f"Error processing receipt {image_path}: {str(e)}")
            raise
    
    def process_folder(self, folder_path: str) -> List[ProcessedReceipt]:
        """
        Process all receipt images in a folder.
        
        Args:
            folder_path: Path to folder containing receipt images
            
        Returns:
            List of ProcessedReceipt objects
        """
        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        # Supported image extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf'}
        
        results = []
        image_files = [f for f in folder.iterdir() 
                      if f.suffix.lower() in image_extensions]
        
        logger.info(f"Found {len(image_files)} receipt images in {folder_path}")
        
        for image_file in image_files:
            try:
                result = self.process_receipt(str(image_file))
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {image_file}: {str(e)}")
                continue
        
        logger.info(f"Successfully processed {len(results)} out of {len(image_files)} receipts")
        return results
    
    def export_to_excel(self, receipts: List[ProcessedReceipt], output_path: str) -> str:
        """
        Export processed receipts to Excel.
        
        Args:
            receipts: List of processed receipts
            output_path: Path for the Excel file
            
        Returns:
            Path to the created Excel file
        """
        return self.excel_exporter.export_receipts(receipts, output_path)
    
    def sync_to_quickbooks(self, receipts: List[ProcessedReceipt]) -> List[str]:
        """
        Sync processed receipts to QuickBooks.
        
        Args:
            receipts: List of processed receipts
            
        Returns:
            List of QuickBooks expense IDs
        """
        if not self.quickbooks_api:
            raise ValueError("QuickBooks API not configured")
        
        expense_ids = []
        for receipt in receipts:
            try:
                expense_id = self.quickbooks_api.create_expense(receipt)
                expense_ids.append(expense_id)
                logger.info(f"Created QuickBooks expense: {expense_id}")
            except Exception as e:
                logger.error(f"Failed to sync receipt to QuickBooks: {str(e)}")
                continue
        
        return expense_ids
    
    def get_expense_summary(self, receipts: List[ProcessedReceipt]) -> Dict[str, float]:
        """
        Generate expense summary by category.
        
        Args:
            receipts: List of processed receipts
            
        Returns:
            Dictionary with category totals
        """
        summary = {}
        for receipt in receipts:
            category = receipt.category or "Uncategorized"
            amount = receipt.amount or 0.0
            summary[category] = summary.get(category, 0.0) + amount
        
        return summary
