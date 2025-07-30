"""
Smart Receipt Processor - Quick Demo
Demonstrates Gemini AI integration for receipt analysis
"""

import os
from pathlib import Path

# Load environment variables
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key.strip()] = value.strip()

def demo_gemini_receipt_analysis():
    """Demonstrate receipt analysis with Gemini."""
    print("🧾 Smart Receipt Processor - Gemini Demo")
    print("=" * 50)
    
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        
        if not api_key:
            print("❌ GEMINI_API_KEY not found in .env file")
            return
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        print(f"✅ Connected to Gemini model: {model_name}")
        
        # Demo receipt text analysis
        receipt_text = """
        WALMART SUPERCENTER
        123 MAIN ST
        ANYTOWN, ST 12345
        
        GROCERIES
        Bananas          $2.99
        Milk 1 Gal       $3.49
        Bread            $2.19
        
        Subtotal:        $8.67
        Tax:             $0.65
        Total:          $9.32
        
        Payment: VISA ****1234
        Date: 01/15/2024
        """
        
        prompt = f"""
        Analyze this receipt text and extract the following information in JSON format:
        - vendor (store name)
        - amount (total amount paid)
        - date (transaction date)
        - category (expense category like "Groceries", "Office Supplies", etc.)
        - tax_amount (tax paid)
        - items (list of purchased items)
        
        Receipt text:
        {receipt_text}
        
        Return only valid JSON without any markdown formatting.
        """
        
        print("🔄 Analyzing receipt with Gemini...")
        response = model.generate_content(prompt)
        
        print("✅ Analysis complete!")
        print("\n📊 Extracted Data:")
        print("-" * 30)
        print(response.text)
        
        # Demo categorization
        print("\n🏷️  Category Suggestions:")
        print("-" * 30)
        
        category_prompt = """
        Based on this receipt from Walmart with groceries (bananas, milk, bread), 
        suggest the most appropriate expense category from these options:
        - Groceries
        - Office Supplies  
        - Travel
        - Entertainment
        - Utilities
        - Other
        
        Just return the category name.
        """
        
        category_response = model.generate_content(category_prompt)
        print(f"Suggested Category: {category_response.text.strip()}")
        
        # Demo Excel export format
        print("\n📊 Excel Export Preview:")
        print("-" * 30)
        print("Date       | Vendor   | Amount | Category  | Tax   ")
        print("-----------|----------|--------|-----------|-------")
        print("01/15/2024 | Walmart  | $9.32  | Groceries | $0.65 ")
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext Steps:")
        print("1. Add receipt images to process folder")
        print("2. Install Tesseract OCR for image text extraction")
        print("3. Run full processing: python main.py process receipt.jpg")
        
    except ImportError:
        print("❌ Google Gemini library not installed")
        print("Install with: pip install google-generativeai")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    demo_gemini_receipt_analysis()
