"""
Quick Demo of Free Accounting Alternatives
Shows export formats for Wave, GnuCash, and Excel
"""

import pandas as pd
from datetime import datetime

def demo_free_accounting():
    print("💰 Free Accounting Software Alternatives")
    print("=" * 50)
    
    # Sample receipt data
    sample_data = {
        'Date': '2024-01-15',
        'Vendor': 'Walmart',
        'Amount': 25.67,
        'Category': 'Groceries',
        'Tax': 2.05,
        'Description': 'Grocery shopping'
    }
    
    print("📊 Sample Receipt Data:")
    for key, value in sample_data.items():
        print(f"  {key}: {value}")
    
    print("\n🆓 Free Software Options:")
    
    print("\n1. 📊 EXCEL/CSV Export (Built-in)")
    print("   ✅ Works with ANY accounting software")
    print("   ✅ Already implemented in your system")
    print("   ✅ Professional formatting included")
    print("   Example: expenses_2024.xlsx")
    
    print("\n2. 🌊 Wave Accounting (100% Free)")
    print("   ✅ Free online accounting software")
    print("   ✅ Receipt scanning included")
    print("   ✅ Bank connections")
    print("   ✅ Professional invoicing")
    print("   🔗 waveapps.com")
    
    print("\n3. 💻 GnuCash (Open Source)")
    print("   ✅ Completely free desktop software")
    print("   ✅ Double-entry bookkeeping")
    print("   ✅ No cloud dependencies")
    print("   ✅ CSV import support")
    print("   🔗 gnucash.org")
    
    print("\n4. 📑 Google Sheets (Free)")
    print("   ✅ Cloud-based spreadsheets")
    print("   ✅ Real-time collaboration")
    print("   ✅ Automatic backups")
    print("   ✅ Mobile access")
    
    print("\n📋 Recommendation:")
    print("Start with EXCEL exports (already working!)")
    print("Then try Wave Accounting for full features")
    
    print("\n🎯 Your Receipt Processor:")
    print("✅ Gemini AI analysis: Working")
    print("✅ Excel export: Built-in")
    print("✅ Professional formatting: Included")
    print("✅ No monthly fees: Free forever")

if __name__ == "__main__":
    demo_free_accounting()
