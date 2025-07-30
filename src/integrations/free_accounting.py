"""
Free Accounting Integrations

Alternatives to QuickBooks for small business expense tracking.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Any
from models.receipt import ProcessedReceipt

class FreeAccountingExporter:
    """Export receipts to free accounting software formats."""
    
    def __init__(self):
        self.supported_formats = [
            'excel', 'csv', 'json', 'wave_csv', 'gnucash_csv', 'google_sheets'
        ]
    
    def export_for_wave(self, receipts: List[ProcessedReceipt], output_path: str) -> str:
        """
        Export receipts in Wave Accounting CSV format.
        
        Wave CSV format:
        Date, Description, Amount, Account, Tax Amount, Customer, Vendor
        """
        wave_data = []
        
        for receipt in receipts:
            wave_data.append({
                'Date': receipt.date or datetime.now().strftime('%Y-%m-%d'),
                'Description': f"{receipt.vendor} - {receipt.description or 'Receipt'}",
                'Amount': receipt.amount or 0.0,
                'Account': self._map_category_to_account(receipt.category),
                'Tax Amount': receipt.tax_amount or 0.0,
                'Customer': '',  # Empty for expenses
                'Vendor': receipt.vendor or 'Unknown',
                'Receipt': receipt.original_image_path
            })
        
        df = pd.DataFrame(wave_data)
        wave_path = output_path.replace('.csv', '_wave.csv')
        df.to_csv(wave_path, index=False)
        
        print(f"✅ Wave Accounting CSV exported: {wave_path}")
        return wave_path
    
    def export_for_gnucash(self, receipts: List[ProcessedReceipt], output_path: str) -> str:
        """
        Export receipts in GnuCash CSV format.
        
        GnuCash CSV format:
        Date, Description, Account, Deposit, Withdrawal
        """
        gnucash_data = []
        
        for receipt in receipts:
            # Expense entry (withdrawal from cash/bank)
            gnucash_data.append({
                'Date': receipt.date or datetime.now().strftime('%Y-%m-%d'),
                'Description': f"{receipt.vendor} - {receipt.description or 'Receipt'}",
                'Account': 'Assets:Cash',  # Source account
                'Deposit': '',
                'Withdrawal': receipt.amount or 0.0
            })
            
            # Category entry (deposit to expense account)
            gnucash_data.append({
                'Date': receipt.date or datetime.now().strftime('%Y-%m-%d'),
                'Description': f"{receipt.vendor} - {receipt.description or 'Receipt'}",
                'Account': f"Expenses:{self._map_category_to_account(receipt.category)}",
                'Deposit': receipt.amount or 0.0,
                'Withdrawal': ''
            })
        
        df = pd.DataFrame(gnucash_data)
        gnucash_path = output_path.replace('.csv', '_gnucash.csv')
        df.to_csv(gnucash_path, index=False)
        
        print(f"✅ GnuCash CSV exported: {gnucash_path}")
        return gnucash_path
    
    def export_summary_report(self, receipts: List[ProcessedReceipt], output_path: str) -> str:
        """
        Export a comprehensive summary report for any accounting software.
        """
        # Calculate totals by category
        category_totals = {}
        monthly_totals = {}
        
        for receipt in receipts:
            category = receipt.category or 'Uncategorized'
            amount = receipt.amount or 0.0
            
            # Category totals
            category_totals[category] = category_totals.get(category, 0.0) + amount
            
            # Monthly totals
            if receipt.date:
                try:
                    month = datetime.strptime(receipt.date, '%Y-%m-%d').strftime('%Y-%m')
                except:
                    month = datetime.now().strftime('%Y-%m')
            else:
                month = datetime.now().strftime('%Y-%m')
            
            monthly_totals[month] = monthly_totals.get(month, 0.0) + amount
        
        # Create summary workbook with multiple sheets
        summary_path = output_path.replace('.xlsx', '_summary.xlsx')
        
        with pd.ExcelWriter(summary_path, engine='openpyxl') as writer:
            # Receipt details
            receipt_df = pd.DataFrame([{
                'Date': r.date,
                'Vendor': r.vendor,
                'Amount': r.amount,
                'Category': r.category,
                'Tax': r.tax_amount,
                'Description': r.description,
                'Confidence': r.confidence_score
            } for r in receipts])
            receipt_df.to_excel(writer, sheet_name='Receipt Details', index=False)
            
            # Category summary
            category_df = pd.DataFrame([
                {'Category': cat, 'Total': total} 
                for cat, total in category_totals.items()
            ])
            category_df.to_excel(writer, sheet_name='Category Summary', index=False)
            
            # Monthly summary
            monthly_df = pd.DataFrame([
                {'Month': month, 'Total': total} 
                for month, total in monthly_totals.items()
            ])
            monthly_df.to_excel(writer, sheet_name='Monthly Summary', index=False)
        
        print(f"✅ Summary report exported: {summary_path}")
        return summary_path
    
    def _map_category_to_account(self, category: str) -> str:
        """Map expense categories to accounting accounts."""
        category_mapping = {
            'Groceries': 'Meals and Entertainment',
            'Office Supplies': 'Office Expenses',
            'Travel': 'Travel',
            'Technology': 'Equipment',
            'Marketing': 'Advertising',
            'Utilities': 'Utilities',
            'Professional Services': 'Professional Fees',
            'Insurance': 'Insurance',
            'Maintenance & Repairs': 'Repairs and Maintenance',
            'Miscellaneous': 'Other Expenses'
        }
        
        return category_mapping.get(category, 'Other Expenses')

class GoogleSheetsExporter:
    """Export receipts to Google Sheets (requires Google Sheets API setup)."""
    
    def __init__(self):
        self.setup_instructions = """
        Google Sheets Setup:
        1. Go to console.cloud.google.com
        2. Create a new project
        3. Enable Google Sheets API
        4. Create credentials (Service Account)
        5. Download JSON credentials file
        6. Share your Google Sheet with the service account email
        """
    
    def export_to_sheets(self, receipts: List[ProcessedReceipt], sheet_id: str) -> str:
        """
        Export receipts to Google Sheets.
        Requires: pip install gspread google-auth
        """
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            
            # This would require credentials setup
            # For now, we'll export to CSV that can be imported to Sheets
            csv_path = "receipts_for_google_sheets.csv"
            
            df = pd.DataFrame([{
                'Date': r.date,
                'Vendor': r.vendor,
                'Amount': r.amount,
                'Category': r.category,
                'Tax Amount': r.tax_amount,
                'Description': r.description
            } for r in receipts])
            
            df.to_csv(csv_path, index=False)
            
            print(f"✅ CSV ready for Google Sheets import: {csv_path}")
            print("📋 Import steps:")
            print("1. Open Google Sheets")
            print("2. File → Import → Upload")
            print(f"3. Select {csv_path}")
            print("4. Choose 'Create new spreadsheet'")
            
            return csv_path
            
        except ImportError:
            print("❌ Google Sheets integration requires: pip install gspread google-auth")
            return None

def demo_free_exports():
    """Demonstrate free accounting software exports."""
    print("💰 Free Accounting Software Integration Demo")
    print("=" * 50)
    
    # Sample receipt data
    sample_receipt = ProcessedReceipt(
        original_image_path="sample_receipt.jpg",
        vendor="Walmart",
        amount=25.67,
        date="2024-01-15",
        category="Groceries",
        description="Grocery shopping",
        tax_amount=2.05,
        confidence_score=0.95,
        ocr_text="Sample OCR text",
        processing_timestamp=datetime.now().isoformat()
    )
    
    exporter = FreeAccountingExporter()
    
    # Export for different software
    print("📊 Exporting for different accounting software:")
    
    # Wave Accounting
    wave_file = exporter.export_for_wave([sample_receipt], "expenses.csv")
    
    # GnuCash
    gnucash_file = exporter.export_for_gnucash([sample_receipt], "expenses.csv")
    
    # Summary report
    summary_file = exporter.export_summary_report([sample_receipt], "expenses.xlsx")
    
    print("\n✅ All exports completed!")
    print("\n📋 Next steps:")
    print("1. Choose your preferred free accounting software")
    print("2. Import the appropriate CSV/Excel file")
    print("3. Set up automatic processing with your receipt processor")

if __name__ == "__main__":
    demo_free_exports()
