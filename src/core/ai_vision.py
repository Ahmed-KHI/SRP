"""
AI Vision Analyzer - Multi-Provider Support

This module handles intelligent analysis of receipt images using either:
- OpenAI's GPT-4 Vision model
- Google's Gemini Vision model

It extracts structured data from receipts and provides confidence scoring.
"""

import base64
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    from PIL import Image
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import Config

logger = logging.getLogger(__name__)

@dataclass
class VisionAnalysisResult:
    """Results from GPT-4 Vision analysis of a receipt."""
    vendor: Optional[str]
    amount: Optional[float]
    date: Optional[str]
    items: List[str]
    confidence_score: float
    raw_data: Dict[str, Any]

class AIVisionAnalyzer:
    """Multi-provider AI vision analyzer for receipts (OpenAI GPT-4 Vision or Google Gemini)."""
    
    def __init__(self, config: Config):
        """Initialize the AI vision analyzer."""
        self.config = config
        
        # Initialize the appropriate AI service
        if config.AI_SERVICE == 'gemini' and GEMINI_AVAILABLE:
            self._init_gemini()
        elif config.AI_SERVICE == 'openai' and OPENAI_AVAILABLE:
            self._init_openai()
        else:
            raise ValueError(f"AI service '{config.AI_SERVICE}' not available or not configured")
        
        # Analysis prompt template
        self.analysis_prompt = """
        Analyze this receipt image and extract the following information in JSON format:
        
        {
            "vendor": "Name of the business/vendor",
            "amount": 0.00,  // Total amount as float
            "date": "YYYY-MM-DD",  // Transaction date
            "items": ["item1", "item2"],  // List of purchased items
            "tax_amount": 0.00,  // Tax amount if visible
            "payment_method": "cash/card/other",
            "address": "Business address if visible",
            "phone": "Business phone if visible",
            "confidence": 0.95,  // Your confidence in the extraction (0.0-1.0)
            "notes": "Any additional relevant information"
        }
        
        Guidelines:
        - Be precise with monetary amounts
        - Use standard date format (YYYY-MM-DD)
        - Include all line items you can clearly read
        - If information is unclear or missing, use null
        - Provide a realistic confidence score
        - Focus on business expense data
        """
        
        logger.info(f"{config.AI_SERVICE.upper()} vision analyzer initialized")
    
    def _init_gemini(self):
        """Initialize Google Gemini."""
        genai.configure(api_key=self.config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(self.config.GEMINI_MODEL)
        self.service_type = 'gemini'
    
    def _init_openai(self):
        """Initialize OpenAI GPT-4 Vision."""
        self.client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)
        self.model_name = self.config.OPENAI_MODEL
        self.service_type = 'openai'
    
    def analyze_receipt(self, image_path: str, ocr_text: str = "") -> VisionAnalysisResult:
        """
        Analyze a receipt image using the configured AI service.
        
        Args:
            image_path: Path to the receipt image
            ocr_text: Optional OCR text to supplement analysis
            
        Returns:
            VisionAnalysisResult with extracted data
        """
        try:
            if self.service_type == 'gemini':
                return self._analyze_with_gemini(image_path, ocr_text)
            else:
                return self._analyze_with_openai(image_path, ocr_text)
                
        except Exception as e:
            logger.error(f"AI vision analysis failed: {str(e)}")
            # Return a minimal result with low confidence
            return VisionAnalysisResult(
                vendor=None,
                amount=None,
                date=None,
                items=[],
                confidence_score=0.0,
                raw_data={"error": str(e)}
            )
    
    def _analyze_with_gemini(self, image_path: str, ocr_text: str) -> VisionAnalysisResult:
        """Analyze receipt using Google Gemini."""
        try:
            # Load image
            image = Image.open(image_path)
            
            # Prepare prompt
            prompt = self._build_analysis_prompt(ocr_text)
            
            # Generate response
            response = self.model.generate_content([prompt, image])
            
            logger.debug(f"Gemini response: {response.text}")
            return self._parse_vision_response(response.text)
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {str(e)}")
            raise
    
    def _analyze_with_openai(self, image_path: str, ocr_text: str) -> VisionAnalysisResult:
        """Analyze receipt using OpenAI GPT-4 Vision."""
        try:
            # Encode image to base64
            image_base64 = self._encode_image(image_path)
            
            # Prepare the message
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": self._build_analysis_prompt(ocr_text)
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            # Call GPT-4 Vision
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=1000,
                temperature=0.1  # Low temperature for consistent extraction
            )
            
            # Parse the response
            result_text = response.choices[0].message.content
            logger.debug(f"OpenAI response: {result_text}")
            
            return self._parse_vision_response(result_text)
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {str(e)}")
            raise
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string."""
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {str(e)}")
            raise
    
    def _build_analysis_prompt(self, ocr_text: str) -> str:
        """Build the complete analysis prompt with OCR context."""
        prompt = self.analysis_prompt
        
        if ocr_text.strip():
            prompt += f"\n\nAdditional OCR Text Context:\n{ocr_text}\n"
            prompt += "Use this OCR text to supplement your visual analysis, but prioritize what you can see in the image."
        
        return prompt
    
    def _parse_vision_response(self, response_text: str) -> VisionAnalysisResult:
        """Parse the JSON response from GPT-4 Vision."""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[start_idx:end_idx]
            data = json.loads(json_str)
            
            return VisionAnalysisResult(
                vendor=data.get('vendor'),
                amount=self._safe_float(data.get('amount')),
                date=data.get('date'),
                items=data.get('items', []) if data.get('items') else [],
                confidence_score=self._safe_float(data.get('confidence', 0.5)),
                raw_data=data
            )
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI vision response: {str(e)}")
            logger.debug(f"Raw response: {response_text}")
            
            # Attempt fallback parsing
            return self._fallback_parse(response_text)
    
    def _fallback_parse(self, response_text: str) -> VisionAnalysisResult:
        """Fallback parsing when JSON parsing fails."""
        logger.warning("Using fallback parsing for AI vision response")
        
        # Simple text-based extraction as fallback
        lines = response_text.split('\n')
        vendor = None
        amount = None
        
        for line in lines:
            line = line.strip().lower()
            if 'vendor' in line or 'business' in line:
                # Try to extract vendor name
                parts = line.split(':')
                if len(parts) > 1:
                    vendor = parts[1].strip().strip('"')
            elif '$' in line and any(char.isdigit() for char in line):
                # Try to extract amount
                import re
                amount_match = re.search(r'\$?(\d+\.?\d*)', line)
                if amount_match:
                    amount = float(amount_match.group(1))
        
        return VisionAnalysisResult(
            vendor=vendor,
            amount=amount,
            date=None,
            items=[],
            confidence_score=0.3,  # Low confidence for fallback
            raw_data={"fallback_parse": True, "raw_text": response_text}
        )
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def validate_analysis(self, result: VisionAnalysisResult) -> bool:
        """Validate the analysis result quality."""
        # Basic validation criteria
        has_vendor = result.vendor is not None and len(result.vendor.strip()) > 0
        has_amount = result.amount is not None and result.amount > 0
        good_confidence = result.confidence_score >= self.config.MIN_CONFIDENCE_SCORE
        
        is_valid = has_vendor and has_amount and good_confidence
        
        if not is_valid:
            logger.warning(f"Analysis validation failed: vendor={has_vendor}, amount={has_amount}, confidence={good_confidence}")
        
        return is_valid
