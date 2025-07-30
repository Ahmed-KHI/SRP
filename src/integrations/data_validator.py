"""
Data Validator - Expense Data Validation and Quality Control

This module provides validation and quality control for processed expense data.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import re
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from models.receipt import ProcessedReceipt
from models.expense import ExpenseRule
from utils.config import Config

logger = logging.getLogger(__name__)

class ValidationResult:
    """Result of data validation with errors and warnings."""
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.confidence_score = 1.0
    
    def add_error(self, message: str):
        """Add a validation error."""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        """Add a validation warning."""
        self.warnings.append(message)
    
    def reduce_confidence(self, amount: float):
        """Reduce confidence score."""
        self.confidence_score = max(0.0, self.confidence_score - amount)

class DataValidator:
    """Comprehensive data validation for expense processing."""
    
    def __init__(self, config: Config):
        """Initialize the data validator."""
        self.config = config
        self.validation_rules = self._load_validation_rules()
        
        # Common validation patterns
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.phone_pattern = re.compile(r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$')
        self.amount_pattern = re.compile(r'^\$?\d+\.?\d{0,2}$')
        
        logger.info("Data validator initialized")
    
    def validate_processed_receipt(self, receipt: ProcessedReceipt) -> ValidationResult:
        """
        Validate a processed receipt comprehensively.
        
        Args:
            receipt: Processed receipt to validate
            
        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult()
        
        # Core data validation
        self._validate_vendor(receipt, result)
        self._validate_amount(receipt, result)
        self._validate_date(receipt, result)
        self._validate_category(receipt, result)
        
        # Business logic validation
        self._validate_business_rules(receipt, result)
        
        # Data quality checks
        self._validate_data_quality(receipt, result)
        
        # Confidence-based validation
        self._validate_confidence(receipt, result)
        
        logger.debug(f"Validation completed for receipt {receipt.receipt.id}: "
                    f"valid={result.is_valid}, errors={len(result.errors)}, warnings={len(result.warnings)}")
        
        return result
    
    def validate_batch(self, receipts: List[ProcessedReceipt]) -> Dict[str, ValidationResult]:
        """
        Validate a batch of processed receipts.
        
        Args:
            receipts: List of processed receipts
            
        Returns:
            Dictionary mapping receipt IDs to validation results
        """
        results = {}
        
        for receipt in receipts:
            results[receipt.receipt.id] = self.validate_processed_receipt(receipt)
        
        # Cross-receipt validation
        self._validate_batch_consistency(receipts, results)
        
        return results
    
    def _validate_vendor(self, receipt: ProcessedReceipt, result: ValidationResult):
        """Validate vendor information."""
        vendor = receipt.vendor
        
        if not vendor:
            result.add_error("Vendor name is missing")
            return
        
        # Check vendor name length
        if len(vendor.strip()) < 2:
            result.add_error("Vendor name too short")
        
        if len(vendor) > 100:
            result.add_warning("Vendor name unusually long")
        
        # Check for suspicious patterns
        if vendor.lower() in ['unknown', 'n/a', 'na', 'none', 'test']:
            result.add_warning("Vendor name appears to be placeholder")
            result.reduce_confidence(0.3)
        
        # Check for special characters (might indicate OCR errors)
        special_char_count = sum(1 for c in vendor if not c.isalnum() and c not in ' -&.')
        if special_char_count > len(vendor) * 0.2:
            result.add_warning("Vendor name contains many special characters")
            result.reduce_confidence(0.2)
    
    def _validate_amount(self, receipt: ProcessedReceipt, result: ValidationResult):
        """Validate expense amount."""
        amount = receipt.amount
        
        if amount is None:
            result.add_error("Amount is missing")
            return
        
        # Check if amount is positive
        if amount <= 0:
            result.add_error("Amount must be positive")
        
        # Check for unreasonably high amounts
        if amount > 50000:
            result.add_warning("Amount is unusually high")
            result.reduce_confidence(0.1)
        
        # Check for suspiciously round numbers (might indicate estimation)
        if amount == int(amount) and amount >= 100:
            result.add_warning("Amount is a round number - verify accuracy")
            result.reduce_confidence(0.1)
        
        # Check decimal precision (receipts shouldn't have more than 2 decimal places)
        try:
            decimal_amount = Decimal(str(amount))
            if decimal_amount.as_tuple().exponent < -2:
                result.add_warning("Amount has more than 2 decimal places")
        except InvalidOperation:
            result.add_error("Amount format is invalid")
    
    def _validate_date(self, receipt: ProcessedReceipt, result: ValidationResult):
        """Validate expense date."""
        date_str = receipt.date
        
        if not date_str:
            result.add_warning("Date is missing")
            return
        
        try:
            # Try to parse the date
            if isinstance(date_str, str):
                # Common date formats
                date_formats = [
                    '%Y-%m-%d',
                    '%m/%d/%Y',
                    '%d/%m/%Y',
                    '%Y/%m/%d',
                    '%m-%d-%Y',
                    '%d-%m-%Y'
                ]
                
                parsed_date = None
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if parsed_date is None:
                    result.add_error(f"Invalid date format: {date_str}")
                    return
                
                # Check if date is reasonable
                today = datetime.now()
                one_year_ago = today - timedelta(days=365)
                one_month_future = today + timedelta(days=30)
                
                if parsed_date < one_year_ago:
                    result.add_warning("Date is more than one year old")
                
                if parsed_date > one_month_future:
                    result.add_warning("Date is in the future")
                    result.reduce_confidence(0.2)
                
        except Exception as e:
            result.add_error(f"Date validation failed: {str(e)}")
    
    def _validate_category(self, receipt: ProcessedReceipt, result: ValidationResult):
        """Validate expense category."""
        category = receipt.category
        
        if not category:
            result.add_error("Category is missing")
            return
        
        # Check if category is in known categories
        if category not in self._get_valid_categories():
            result.add_warning(f"Unknown category: {category}")
        
        # Check category-amount consistency
        self._validate_category_amount_consistency(receipt, result)
    
    def _validate_business_rules(self, receipt: ProcessedReceipt, result: ValidationResult):
        """Validate against business rules."""
        for rule in self.validation_rules:
            if rule.applies_to(receipt.to_dict()):
                # Apply rule validations
                self._apply_validation_rule(receipt, rule, result)
    
    def _validate_data_quality(self, receipt: ProcessedReceipt, result: ValidationResult):
        """Validate overall data quality."""
        
        # Check OCR text quality
        if receipt.receipt.ocr_text:
            ocr_quality = self._assess_ocr_quality(receipt.receipt.ocr_text)
            if ocr_quality < 0.5:
                result.add_warning("Poor OCR text quality detected")
                result.reduce_confidence(0.2)
        
        # Check data completeness
        completeness_score = self._calculate_completeness(receipt)
        if completeness_score < 0.7:
            result.add_warning("Incomplete data - manual review recommended")
            result.reduce_confidence(0.3)
    
    def _validate_confidence(self, receipt: ProcessedReceipt, result: ValidationResult):
        """Validate confidence scores."""
        confidence = receipt.confidence_score
        
        if confidence < self.config.MIN_CONFIDENCE_SCORE:
            result.add_warning(f"Low confidence score: {confidence:.2f}")
            result.reduce_confidence(0.2)
        
        if confidence < 0.5:
            result.add_error("Very low confidence - manual review required")
    
    def _validate_batch_consistency(self, receipts: List[ProcessedReceipt], results: Dict[str, ValidationResult]):
        """Validate consistency across a batch of receipts."""
        
        # Check for duplicate receipts
        self._check_duplicates(receipts, results)
        
        # Check for unusual patterns
        self._check_unusual_patterns(receipts, results)
    
    def _check_duplicates(self, receipts: List[ProcessedReceipt], results: Dict[str, ValidationResult]):
        """Check for potential duplicate receipts."""
        seen_receipts = []
        
        for receipt in receipts:
            # Check for duplicates based on vendor, amount, and date
            for seen_receipt in seen_receipts:
                if (receipt.vendor == seen_receipt.vendor and
                    receipt.amount == seen_receipt.amount and
                    receipt.date == seen_receipt.date):
                    
                    # Add warning to both receipts
                    for receipt_id in [receipt.receipt.id, seen_receipt.receipt.id]:
                        if receipt_id in results:
                            results[receipt_id].add_warning("Potential duplicate receipt detected")
            
            seen_receipts.append(receipt)
    
    def _check_unusual_patterns(self, receipts: List[ProcessedReceipt], results: Dict[str, ValidationResult]):
        """Check for unusual spending patterns."""
        if len(receipts) < 5:
            return  # Not enough data for pattern analysis
        
        amounts = [r.amount for r in receipts if r.amount]
        
        if amounts:
            avg_amount = sum(amounts) / len(amounts)
            
            # Flag unusually high amounts
            for receipt in receipts:
                if receipt.amount and receipt.amount > avg_amount * 5:
                    if receipt.receipt.id in results:
                        results[receipt.receipt.id].add_warning("Amount significantly higher than batch average")
    
    def _get_valid_categories(self) -> List[str]:
        """Get list of valid expense categories."""
        # This would typically come from the expense categories configuration
        return [
            "Office Supplies", "Meals & Entertainment", "Travel", "Technology",
            "Marketing", "Utilities", "Professional Services", "Insurance",
            "Maintenance & Repairs", "Miscellaneous"
        ]
    
    def _validate_category_amount_consistency(self, receipt: ProcessedReceipt, result: ValidationResult):
        """Validate that amount is reasonable for the category."""
        category = receipt.category
        amount = receipt.amount
        
        if not amount:
            return
        
        # Category-specific amount ranges (this could be configurable)
        category_ranges = {
            "Office Supplies": (1, 500),
            "Meals & Entertainment": (5, 200),
            "Travel": (10, 2000),
            "Technology": (25, 5000),
            "Marketing": (50, 10000),
            "Utilities": (25, 1000),
            "Professional Services": (100, 50000),
            "Insurance": (50, 5000),
            "Maintenance & Repairs": (25, 2000),
            "Miscellaneous": (1, 1000)
        }
        
        if category in category_ranges:
            min_amount, max_amount = category_ranges[category]
            
            if amount < min_amount:
                result.add_warning(f"Amount ${amount:.2f} is low for category '{category}'")
            elif amount > max_amount:
                result.add_warning(f"Amount ${amount:.2f} is high for category '{category}'")
    
    def _assess_ocr_quality(self, ocr_text: str) -> float:
        """Assess the quality of OCR text."""
        if not ocr_text:
            return 0.0
        
        # Simple quality metrics
        total_chars = len(ocr_text)
        if total_chars == 0:
            return 0.0
        
        # Count readable characters
        readable_chars = sum(1 for c in ocr_text if c.isalnum() or c.isspace())
        readability_score = readable_chars / total_chars
        
        # Check for common OCR artifacts
        artifacts = ['|||', '~~~', '###', '***']
        artifact_count = sum(ocr_text.count(artifact) for artifact in artifacts)
        artifact_penalty = min(artifact_count * 0.1, 0.5)
        
        quality_score = readability_score - artifact_penalty
        return max(0.0, min(1.0, quality_score))
    
    def _calculate_completeness(self, receipt: ProcessedReceipt) -> float:
        """Calculate data completeness score."""
        total_fields = 5  # vendor, amount, date, category, description
        complete_fields = 0
        
        if receipt.vendor:
            complete_fields += 1
        if receipt.amount:
            complete_fields += 1
        if receipt.date:
            complete_fields += 1
        if receipt.category:
            complete_fields += 1
        if receipt.description:
            complete_fields += 1
        
        return complete_fields / total_fields
    
    def _load_validation_rules(self) -> List[ExpenseRule]:
        """Load validation rules (placeholder for now)."""
        # This would typically load from configuration
        return []
    
    def _apply_validation_rule(self, receipt: ProcessedReceipt, rule: ExpenseRule, result: ValidationResult):
        """Apply a specific validation rule."""
        # Placeholder for rule application logic
        pass
