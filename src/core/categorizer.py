"""
Expense Categorizer - AI-Powered Expense Classification

This module provides intelligent expense categorization using a combination of:
- Predefined business rules and categories
- Machine learning-based classification
- Vendor-based categorization
- Custom business logic
"""

import logging
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re

from models.receipt import Receipt
from utils.config import Config

logger = logging.getLogger(__name__)

class ExpenseCategorizer:
    """AI-powered expense categorization engine."""
    
    def __init__(self, config: Config):
        """Initialize the expense categorizer."""
        self.config = config
        self.categories = self._load_expense_categories()
        self.vendor_mappings = self._load_vendor_mappings()
        self.keyword_patterns = self._build_keyword_patterns()
        
        logger.info(f"Expense categorizer initialized with {len(self.categories)} categories")
    
    def categorize_expense(self, receipt: Receipt) -> str:
        """
        Categorize an expense based on receipt data.
        
        Args:
            receipt: Receipt object with extracted data
            
        Returns:
            Expense category string
        """
        try:
            # Method 1: Direct vendor mapping
            if receipt.vendor:
                vendor_category = self._categorize_by_vendor(receipt.vendor)
                if vendor_category:
                    logger.debug(f"Categorized by vendor: {vendor_category}")
                    return vendor_category
            
            # Method 2: Item-based categorization
            if receipt.items:
                item_category = self._categorize_by_items(receipt.items)
                if item_category:
                    logger.debug(f"Categorized by items: {item_category}")
                    return item_category
            
            # Method 3: Text analysis categorization
            text_category = self._categorize_by_text_analysis(receipt)
            if text_category:
                logger.debug(f"Categorized by text analysis: {text_category}")
                return text_category
            
            # Method 4: Amount-based heuristics
            amount_category = self._categorize_by_amount(receipt.amount)
            if amount_category:
                logger.debug(f"Categorized by amount: {amount_category}")
                return amount_category
            
            # Default category
            default_category = "Miscellaneous"
            logger.debug(f"Using default category: {default_category}")
            return default_category
            
        except Exception as e:
            logger.error(f"Error categorizing expense: {str(e)}")
            return "Uncategorized"
    
    def get_category_confidence(self, receipt: Receipt, category: str) -> float:
        """
        Calculate confidence score for a given categorization.
        
        Args:
            receipt: Receipt object
            category: Proposed category
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence_factors = []
        
        # Vendor confidence
        if receipt.vendor:
            vendor_score = self._get_vendor_confidence(receipt.vendor, category)
            confidence_factors.append(vendor_score)
        
        # Items confidence
        if receipt.items:
            items_score = self._get_items_confidence(receipt.items, category)
            confidence_factors.append(items_score)
        
        # Text analysis confidence
        text_score = self._get_text_confidence(receipt, category)
        confidence_factors.append(text_score)
        
        # Calculate weighted average
        if confidence_factors:
            return sum(confidence_factors) / len(confidence_factors)
        else:
            return 0.5  # Neutral confidence
    
    def suggest_categories(self, receipt: Receipt, top_n: int = 3) -> List[Tuple[str, float]]:
        """
        Suggest multiple possible categories with confidence scores.
        
        Args:
            receipt: Receipt object
            top_n: Number of suggestions to return
            
        Returns:
            List of (category, confidence) tuples
        """
        category_scores = {}
        
        # Score all categories
        for category in self.categories.keys():
            confidence = self.get_category_confidence(receipt, category)
            category_scores[category] = confidence
        
        # Sort by confidence and return top N
        sorted_categories = sorted(
            category_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return sorted_categories[:top_n]
    
    def _load_expense_categories(self) -> Dict:
        """Load expense categories from configuration file."""
        try:
            config_path = Path(__file__).parent.parent.parent / "config" / "expense_categories.json"
            
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                # Return default categories if config file doesn't exist
                return self._get_default_categories()
                
        except Exception as e:
            logger.error(f"Failed to load expense categories: {str(e)}")
            return self._get_default_categories()
    
    def _get_default_categories(self) -> Dict:
        """Get default expense categories."""
        return {
            "Office Supplies": {
                "keywords": ["paper", "pen", "pencil", "stapler", "folder", "binder", "supplies"],
                "vendors": ["staples", "office depot", "best buy"],
                "description": "General office supplies and materials"
            },
            "Meals & Entertainment": {
                "keywords": ["restaurant", "food", "lunch", "dinner", "coffee", "catering"],
                "vendors": ["mcdonalds", "starbucks", "subway", "dominos"],
                "description": "Business meals and entertainment expenses"
            },
            "Travel": {
                "keywords": ["hotel", "flight", "airline", "uber", "taxi", "gas", "parking"],
                "vendors": ["hilton", "marriott", "delta", "united", "shell", "exxon"],
                "description": "Travel and transportation expenses"
            },
            "Technology": {
                "keywords": ["computer", "software", "laptop", "phone", "tablet", "tech"],
                "vendors": ["apple", "microsoft", "amazon", "best buy"],
                "description": "Technology equipment and software"
            },
            "Marketing": {
                "keywords": ["advertising", "marketing", "promotion", "print", "design"],
                "vendors": ["facebook", "google", "adobe"],
                "description": "Marketing and advertising expenses"
            },
            "Utilities": {
                "keywords": ["electric", "water", "gas", "internet", "phone", "utility"],
                "vendors": ["verizon", "att", "comcast"],
                "description": "Utility bills and services"
            },
            "Professional Services": {
                "keywords": ["consultant", "legal", "accounting", "professional", "service"],
                "vendors": ["law", "cpa", "consulting"],
                "description": "Professional services and consulting"
            },
            "Miscellaneous": {
                "keywords": ["misc", "other", "various"],
                "vendors": [],
                "description": "Other business expenses"
            }
        }
    
    def _load_vendor_mappings(self) -> Dict[str, str]:
        """Load vendor-to-category mappings."""
        mappings = {}
        
        for category, config in self.categories.items():
            for vendor in config.get("vendors", []):
                mappings[vendor.lower()] = category
        
        return mappings
    
    def _build_keyword_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Build compiled regex patterns for keyword matching."""
        patterns = {}
        
        for category, config in self.categories.items():
            category_patterns = []
            for keyword in config.get("keywords", []):
                pattern = re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE)
                category_patterns.append(pattern)
            patterns[category] = category_patterns
        
        return patterns
    
    def _categorize_by_vendor(self, vendor: str) -> Optional[str]:
        """Categorize expense based on vendor name."""
        vendor_lower = vendor.lower()
        
        # Direct mapping
        if vendor_lower in self.vendor_mappings:
            return self.vendor_mappings[vendor_lower]
        
        # Partial matching
        for mapped_vendor, category in self.vendor_mappings.items():
            if mapped_vendor in vendor_lower or vendor_lower in mapped_vendor:
                return category
        
        return None
    
    def _categorize_by_items(self, items: List[str]) -> Optional[str]:
        """Categorize expense based on purchased items."""
        item_text = " ".join(items).lower()
        
        category_scores = {}
        
        for category, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(pattern.findall(item_text))
                score += matches
            
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return None
    
    def _categorize_by_text_analysis(self, receipt: Receipt) -> Optional[str]:
        """Categorize expense based on full text analysis."""
        # Combine all available text
        text_parts = []
        
        if receipt.vendor:
            text_parts.append(receipt.vendor)
        if receipt.items:
            text_parts.extend(receipt.items)
        if receipt.ocr_text:
            text_parts.append(receipt.ocr_text)
        
        combined_text = " ".join(text_parts).lower()
        
        if not combined_text.strip():
            return None
        
        # Score each category
        category_scores = {}
        
        for category, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(pattern.findall(combined_text))
                score += matches
            
            # Weight by text length to normalize scores
            if len(combined_text) > 0:
                score = score / len(combined_text.split()) * 100
            
            category_scores[category] = score
        
        # Return category with highest score if above threshold
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0.1:  # Minimum threshold
                return best_category
        
        return None
    
    def _categorize_by_amount(self, amount: Optional[float]) -> Optional[str]:
        """Categorize expense based on amount heuristics."""
        if not amount:
            return None
        
        # Simple amount-based heuristics
        if amount < 10:
            return "Office Supplies"  # Small purchases likely supplies
        elif amount > 500:
            return "Technology"  # Large purchases likely equipment
        
        return None
    
    def _get_vendor_confidence(self, vendor: str, category: str) -> float:
        """Calculate confidence score for vendor-based categorization."""
        if not vendor:
            return 0.0
        
        vendor_lower = vendor.lower()
        category_config = self.categories.get(category, {})
        category_vendors = [v.lower() for v in category_config.get("vendors", [])]
        
        # Direct match
        if vendor_lower in category_vendors:
            return 0.9
        
        # Partial match
        for cat_vendor in category_vendors:
            if cat_vendor in vendor_lower or vendor_lower in cat_vendor:
                return 0.7
        
        return 0.1
    
    def _get_items_confidence(self, items: List[str], category: str) -> float:
        """Calculate confidence score for items-based categorization."""
        if not items:
            return 0.0
        
        item_text = " ".join(items).lower()
        patterns = self.keyword_patterns.get(category, [])
        
        total_matches = 0
        for pattern in patterns:
            total_matches += len(pattern.findall(item_text))
        
        # Normalize by number of items
        if len(items) > 0:
            confidence = min(total_matches / len(items), 1.0)
            return confidence
        
        return 0.0
    
    def _get_text_confidence(self, receipt: Receipt, category: str) -> float:
        """Calculate confidence score for text-based categorization."""
        # Simple heuristic based on keyword presence
        patterns = self.keyword_patterns.get(category, [])
        
        if not patterns:
            return 0.0
        
        # Check vendor name
        vendor_matches = 0
        if receipt.vendor:
            for pattern in patterns:
                vendor_matches += len(pattern.findall(receipt.vendor.lower()))
        
        # Check OCR text
        ocr_matches = 0
        if receipt.ocr_text:
            for pattern in patterns:
                ocr_matches += len(pattern.findall(receipt.ocr_text.lower()))
        
        total_matches = vendor_matches + ocr_matches
        
        # Simple confidence calculation
        if total_matches > 0:
            return min(total_matches * 0.2, 1.0)
        
        return 0.0
