# Smart Receipt Processor
# Development and Testing Setup

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
copy .env.example .env

# Run basic tests
python -m pytest tests/ -v

# Run example
python main.py examples/sample_receipts/receipt1.jpg
