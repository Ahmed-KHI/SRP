"""
Smart Receipt Processor - Main Application Entry Point

This module provides the main interface for the AI-powered receipt processing system.
It integrates GPT-4 Vision, OCR, and automated accounting workflows.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.receipt_processor import ReceiptProcessor
from src.utils.config import Config
from src.utils.logger import setup_logger

def main():
    """Main application entry point."""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    logger = setup_logger()
    logger.info("Starting Smart Receipt Processor")
    
    try:
        # Initialize configuration
        config = Config()
        
        # Check if AI service is configured
        if not config.is_ai_configured():
            logger.error("No AI service configured. Please set either OPENAI_API_KEY or GEMINI_API_KEY in .env file")
            print("Error: No AI service configured.")
            print("Please add either:")
            print("  OPENAI_API_KEY=your_key  (for OpenAI GPT-4 Vision)")
            print("  GEMINI_API_KEY=your_key  (for Google Gemini)")
            return
        
        logger.info(f"Using AI service: {config.AI_SERVICE.upper()}")
        
        # Initialize the receipt processor
        processor = ReceiptProcessor(config)
        
        # Example usage - process a single receipt
        if len(sys.argv) > 1:
            receipt_path = sys.argv[1]
            if os.path.exists(receipt_path):
                logger.info(f"Processing receipt: {receipt_path}")
                result = processor.process_receipt(receipt_path)
                
                print(f"\n--- Receipt Processing Results ---")
                print(f"Vendor: {result.vendor}")
                print(f"Amount: ${result.amount}")
                print(f"Date: {result.date}")
                print(f"Category: {result.category}")
                print(f"Description: {result.description}")
                print(f"Confidence: {result.confidence_score:.2f}")
                
                # Export to Excel if configured
                if config.AUTO_SAVE:
                    excel_file = "processed_receipts.xlsx"
                    processor.export_to_excel([result], excel_file)
                    print(f"\nData exported to: {excel_file}")
                    
            else:
                print(f"Error: File '{receipt_path}' not found.")
        else:
            print("Smart Receipt Processor")
            print("Usage: python main.py <receipt_image_path>")
            print("\nExample: python main.py examples/sample_receipts/receipt1.jpg")
            
            # Interactive mode
            while True:
                receipt_path = input("\nEnter receipt path (or 'quit' to exit): ").strip()
                if receipt_path.lower() == 'quit':
                    break
                    
                if os.path.exists(receipt_path):
                    result = processor.process_receipt(receipt_path)
                    print(f"\nProcessed: {result.vendor} - ${result.amount} ({result.category})")
                else:
                    print("File not found. Please try again.")
                    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"Error: {str(e)}")
    finally:
        logger.info("Smart Receipt Processor stopped")

if __name__ == "__main__":
    main()
