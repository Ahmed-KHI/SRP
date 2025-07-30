"""
Example: Basic Receipt Processing

This example demonstrates basic usage of the Smart Receipt Processor.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.receipt_processor import ReceiptProcessor
from utils.config import Config
from utils.logger import setup_logger

def main():
    """Basic receipt processing example."""
    
    # Setup logging
    logger = setup_logger("example_basic", "INFO")
    logger.info("Starting basic receipt processing example")
    
    try:
        # Initialize configuration
        config = Config()
        
        # Check if OpenAI is configured
        if not config.is_openai_configured():
            logger.error("OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
            return
        
        # Initialize processor
        processor = ReceiptProcessor(config)
        
        # Example: Process a single receipt
        receipt_path = "examples/sample_receipts/receipt1.jpg"
        
        if os.path.exists(receipt_path):
            logger.info(f"Processing receipt: {receipt_path}")
            
            # Process the receipt
            result = processor.process_receipt(receipt_path)
            
            # Display results
            print("\n" + "="*50)
            print("RECEIPT PROCESSING RESULTS")
            print("="*50)
            print(f"Vendor: {result.vendor}")
            print(f"Amount: ${result.amount:.2f}" if result.amount else "Amount: N/A")
            print(f"Date: {result.date}")
            print(f"Category: {result.category}")
            print(f"Description: {result.description}")
            print(f"Confidence: {result.confidence_score:.2f}")
            print(f"Status: {result.status}")
            print(f"Requires Review: {'Yes' if result.requires_review else 'No'}")
            
            if result.items:
                print(f"Items: {', '.join(result.items[:3])}")
                if len(result.items) > 3:
                    print(f"  ... and {len(result.items) - 3} more items")
            
            print("="*50)
            
            # Export to Excel if configured
            if config.AUTO_SAVE:
                excel_file = "example_output.xlsx"
                processor.export_to_excel([result], excel_file)
                logger.info(f"Results exported to: {excel_file}")
            
        else:
            logger.error(f"Sample receipt not found: {receipt_path}")
            logger.info("Please add sample receipt images to examples/sample_receipts/")
    
    except Exception as e:
        logger.error(f"Example failed: {str(e)}")

if __name__ == "__main__":
    main()
