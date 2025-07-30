"""
Example: Batch Receipt Processing

This example demonstrates batch processing of multiple receipts.
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
    """Batch receipt processing example."""
    
    # Setup logging
    logger = setup_logger("example_batch", "INFO")
    logger.info("Starting batch receipt processing example")
    
    try:
        # Initialize configuration
        config = Config()
        
        # Check prerequisites
        if not config.is_openai_configured():
            logger.error("OpenAI API key not configured")
            return
        
        # Initialize processor
        processor = ReceiptProcessor(config)
        
        # Process receipts folder
        receipts_folder = "examples/sample_receipts"
        output_file = "batch_processed_receipts.xlsx"
        
        if os.path.exists(receipts_folder):
            logger.info(f"Processing receipts in folder: {receipts_folder}")
            
            # Process all receipts in folder
            results = processor.process_folder(receipts_folder, output_file)
            
            # Display summary
            print("\n" + "="*60)
            print("BATCH PROCESSING SUMMARY")
            print("="*60)
            print(f"Total receipts processed: {len(results)}")
            
            if results:
                total_amount = sum(r.amount or 0 for r in results)
                print(f"Total amount: ${total_amount:,.2f}")
                
                # Category breakdown
                categories = {}
                for result in results:
                    cat = result.category
                    categories[cat] = categories.get(cat, 0) + (result.amount or 0)
                
                print(f"\nCategory breakdown:")
                for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {category}: ${amount:,.2f}")
                
                # Review summary
                needs_review = sum(1 for r in results if r.requires_review)
                print(f"\nReview status:")
                print(f"  Needs review: {needs_review}")
                print(f"  Auto-approved: {len(results) - needs_review}")
                
                print(f"\nResults exported to: {output_file}")
            
            print("="*60)
            
        else:
            logger.error(f"Receipts folder not found: {receipts_folder}")
            logger.info("Please create the folder and add sample receipt images")
    
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")

if __name__ == "__main__":
    main()
