"""
Configuration Management

This module handles configuration loading and validation for the Smart Receipt Processor.
"""

import os
import logging
from typing import Optional, List
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Config:
    """Configuration management class."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration from environment variables.
        
        Args:
            env_file: Optional path to .env file
        """
        # Load environment variables
        if env_file and Path(env_file).exists():
            load_dotenv(env_file)
        else:
            load_dotenv()  # Load from default .env file
        
        # AI Configuration - Support both OpenAI and Gemini
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-vision-preview')
        
        # Gemini Configuration
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        self.GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        
        # Determine which AI service to use
        self.AI_SERVICE = 'gemini' if self.GEMINI_API_KEY else 'openai'
        
        # QuickBooks Configuration
        self.QB_CLIENT_ID = os.getenv('QB_CLIENT_ID')
        self.QB_CLIENT_SECRET = os.getenv('QB_CLIENT_SECRET')
        self.QB_ENVIRONMENT = os.getenv('QB_ENVIRONMENT', 'sandbox')
        self.QB_REDIRECT_URI = os.getenv('QB_REDIRECT_URI', 'http://localhost:8080/callback')
        
        # Application Settings
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', '5242880'))  # 5MB default
        self.SUPPORTED_FORMATS = os.getenv('SUPPORTED_FORMATS', 'jpg,jpeg,png,pdf').split(',')
        
        # Excel Settings
        self.DEFAULT_EXCEL_TEMPLATE = os.getenv('DEFAULT_EXCEL_TEMPLATE')
        self.AUTO_SAVE = os.getenv('AUTO_SAVE', 'true').lower() == 'true'
        
        # OCR Settings
        self.TESSERACT_PATH = os.getenv('TESSERACT_PATH')
        self.TESSERACT_LANG = os.getenv('TESSERACT_LANG', 'eng')
        
        # Data Validation
        self.MIN_CONFIDENCE_SCORE = float(os.getenv('MIN_CONFIDENCE_SCORE', '0.8'))
        self.REQUIRE_MANUAL_REVIEW = os.getenv('REQUIRE_MANUAL_REVIEW', 'false').lower() == 'true'
        
        # Validate configuration
        self._validate_config()
        
        logger.info("Configuration loaded successfully")
    
    def _validate_config(self):
        """Validate critical configuration settings."""
        errors = []
        
        # Check required AI settings
        if not self.OPENAI_API_KEY and not self.GEMINI_API_KEY:
            errors.append("Either OPENAI_API_KEY or GEMINI_API_KEY is required")
        
        # Validate model names
        valid_openai_models = ['gpt-4-vision-preview', 'gpt-4o', 'gpt-4o-mini']
        valid_gemini_models = ['gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-1.5-flash']
        
        if self.AI_SERVICE == 'openai' and self.OPENAI_MODEL not in valid_openai_models:
            logger.warning(f"Unknown OpenAI model: {self.OPENAI_MODEL}")
        elif self.AI_SERVICE == 'gemini' and self.GEMINI_MODEL not in valid_gemini_models:
            logger.warning(f"Unknown Gemini model: {self.GEMINI_MODEL}")
        
        # Validate file size
        if self.MAX_IMAGE_SIZE <= 0:
            errors.append("MAX_IMAGE_SIZE must be positive")
        
        # Validate confidence score
        if not 0.0 <= self.MIN_CONFIDENCE_SCORE <= 1.0:
            errors.append("MIN_CONFIDENCE_SCORE must be between 0.0 and 1.0")
        
        # Check QuickBooks config if provided
        if self.QB_CLIENT_ID and not self.QB_CLIENT_SECRET:
            errors.append("QB_CLIENT_SECRET required when QB_CLIENT_ID is set")
        
        # Validate Tesseract path if provided
        if self.TESSERACT_PATH and not Path(self.TESSERACT_PATH).exists():
            logger.warning(f"Tesseract path does not exist: {self.TESSERACT_PATH}")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def is_ai_configured(self) -> bool:
        """Check if AI service is properly configured."""
        return bool(self.OPENAI_API_KEY or self.GEMINI_API_KEY)
    
    def is_openai_configured(self) -> bool:
        """Check if OpenAI is properly configured."""
        return bool(self.OPENAI_API_KEY)
    
    def is_gemini_configured(self) -> bool:
        """Check if Gemini is properly configured."""
        return bool(self.GEMINI_API_KEY)
    
    def is_quickbooks_configured(self) -> bool:
        """Check if QuickBooks is properly configured."""
        return bool(self.QB_CLIENT_ID and self.QB_CLIENT_SECRET)
    
    def is_tesseract_configured(self) -> bool:
        """Check if Tesseract is properly configured."""
        if self.TESSERACT_PATH:
            return Path(self.TESSERACT_PATH).exists()
        else:
            # Check if tesseract is in PATH
            import shutil
            return shutil.which('tesseract') is not None
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        extensions = []
        for fmt in self.SUPPORTED_FORMATS:
            fmt = fmt.strip().lower()
            if not fmt.startswith('.'):
                fmt = '.' + fmt
            extensions.append(fmt)
        return extensions
    
    def validate_image_file(self, file_path: str) -> bool:
        """
        Validate if an image file is supported and within size limits.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            True if file is valid, False otherwise
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            logger.error(f"File does not exist: {file_path}")
            return False
        
        # Check file extension
        if path.suffix.lower() not in self.get_supported_extensions():
            logger.error(f"Unsupported file format: {path.suffix}")
            return False
        
        # Check file size
        if path.stat().st_size > self.MAX_IMAGE_SIZE:
            logger.error(f"File too large: {path.stat().st_size} bytes (max: {self.MAX_IMAGE_SIZE})")
            return False
        
        return True
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary (excluding sensitive data)."""
        return {
            'AI_SERVICE': self.AI_SERVICE,
            'OPENAI_MODEL': self.OPENAI_MODEL,
            'GEMINI_MODEL': self.GEMINI_MODEL,
            'QB_ENVIRONMENT': self.QB_ENVIRONMENT,
            'LOG_LEVEL': self.LOG_LEVEL,
            'MAX_IMAGE_SIZE': self.MAX_IMAGE_SIZE,
            'SUPPORTED_FORMATS': self.SUPPORTED_FORMATS,
            'AUTO_SAVE': self.AUTO_SAVE,
            'TESSERACT_LANG': self.TESSERACT_LANG,
            'MIN_CONFIDENCE_SCORE': self.MIN_CONFIDENCE_SCORE,
            'REQUIRE_MANUAL_REVIEW': self.REQUIRE_MANUAL_REVIEW,
            'ai_configured': self.is_ai_configured(),
            'openai_configured': self.is_openai_configured(),
            'gemini_configured': self.is_gemini_configured(),
            'quickbooks_configured': self.is_quickbooks_configured(),
            'tesseract_configured': self.is_tesseract_configured()
        }
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        config_dict = self.to_dict()
        return f"Config({config_dict})"
