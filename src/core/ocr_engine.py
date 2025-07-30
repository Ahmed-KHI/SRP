"""
OCR Engine - Tesseract Integration

This module provides optical character recognition capabilities using Tesseract OCR.
It preprocesses images and extracts text to supplement AI vision analysis.
"""

import logging
import subprocess
import os
from typing import Optional, Dict, Any
from pathlib import Path

import pytesseract
from PIL import Image
import cv2
import numpy as np

from utils.config import Config

logger = logging.getLogger(__name__)

class OCREngine:
    """Tesseract OCR engine for text extraction from receipt images."""
    
    def __init__(self, config: Config):
        """Initialize the OCR engine."""
        self.config = config
        
        # Set Tesseract path if specified
        if config.TESSERACT_PATH and os.path.exists(config.TESSERACT_PATH):
            pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
        
        # OCR configuration
        self.ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+-=[]{}|;:\'\",./<>? '
        
        # Test OCR availability
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Tesseract OCR: {str(e)}")
            logger.warning("OCR functionality may be limited")
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from a receipt image using OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text string
        """
        try:
            # Load and preprocess the image
            image = self._load_image(image_path)
            processed_image = self._preprocess_for_ocr(image)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.config.TESSERACT_LANG,
                config=self.ocr_config
            )
            
            # Clean up the extracted text
            cleaned_text = self._clean_text(text)
            
            logger.debug(f"OCR extracted {len(cleaned_text)} characters from {image_path}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"OCR extraction failed for {image_path}: {str(e)}")
            return ""
    
    def extract_structured_data(self, image_path: str) -> Dict[str, Any]:
        """
        Extract structured data from receipt using OCR with confidence scores.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with extracted data and confidence scores
        """
        try:
            image = self._load_image(image_path)
            processed_image = self._preprocess_for_ocr(image)
            
            # Get detailed OCR data with bounding boxes and confidence
            ocr_data = pytesseract.image_to_data(
                processed_image,
                lang=self.config.TESSERACT_LANG,
                config=self.ocr_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Process the structured data
            structured_data = self._process_ocr_data(ocr_data)
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Structured OCR extraction failed for {image_path}: {str(e)}")
            return {}
    
    def _load_image(self, image_path: str) -> np.ndarray:
        """Load image using OpenCV."""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        return image
    
    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image to improve OCR accuracy.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image optimized for OCR
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding to handle varying lighting
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply morphological operations to clean up small noise
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Optional: Resize image if too small (improves OCR accuracy)
        height, width = cleaned.shape
        if height < 800:
            scale_factor = 800 / height
            new_width = int(width * scale_factor)
            cleaned = cv2.resize(cleaned, (new_width, 800), interpolation=cv2.INTER_CUBIC)
        
        return cleaned
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted OCR text."""
        if not text:
            return ""
        
        # Basic text cleaning
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove excessive whitespace
            line = ' '.join(line.split())
            
            # Skip very short lines (likely noise)
            if len(line.strip()) < 2:
                continue
                
            # Skip lines with too many special characters (likely noise)
            if sum(1 for c in line if not c.isalnum() and c != ' ') > len(line) * 0.5:
                continue
            
            cleaned_lines.append(line.strip())
        
        return '\n'.join(cleaned_lines)
    
    def _process_ocr_data(self, ocr_data: Dict) -> Dict[str, Any]:
        """Process detailed OCR data to extract structured information."""
        structured_data = {
            'text_blocks': [],
            'confidence_scores': [],
            'potential_amounts': [],
            'potential_dates': [],
            'high_confidence_text': []
        }
        
        import re
        
        # Process each detected text element
        for i, text in enumerate(ocr_data['text']):
            if int(ocr_data['conf'][i]) > 30:  # Only consider high-confidence text
                text = text.strip()
                if len(text) > 1:
                    structured_data['text_blocks'].append(text)
                    structured_data['confidence_scores'].append(int(ocr_data['conf'][i]))
                    
                    if int(ocr_data['conf'][i]) > 70:
                        structured_data['high_confidence_text'].append(text)
                    
                    # Look for potential monetary amounts
                    amount_pattern = r'\$?\d+[.,]\d{2}'
                    if re.search(amount_pattern, text):
                        structured_data['potential_amounts'].append(text)
                    
                    # Look for potential dates
                    date_patterns = [
                        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
                        r'\d{2,4}[/-]\d{1,2}[/-]\d{1,2}',
                        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{2,4}'
                    ]
                    for pattern in date_patterns:
                        if re.search(pattern, text, re.IGNORECASE):
                            structured_data['potential_dates'].append(text)
                            break
        
        return structured_data
    
    def get_text_confidence(self, image_path: str) -> float:
        """
        Get overall confidence score for OCR text extraction.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Average confidence score (0.0 to 1.0)
        """
        try:
            structured_data = self.extract_structured_data(image_path)
            confidence_scores = structured_data.get('confidence_scores', [])
            
            if confidence_scores:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                return avg_confidence / 100.0  # Convert to 0-1 scale
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Failed to get OCR confidence for {image_path}: {str(e)}")
            return 0.0
