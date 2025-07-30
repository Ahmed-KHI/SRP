"""
Receipt Data Models

This module defines the data structures for representing receipts and processed expense data.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

@dataclass
class Receipt:
    """Raw receipt data extracted from image processing."""
    
    # Core identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    image_path: str = ""
    
    # Extracted data
    vendor: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[str] = None
    items: List[str] = field(default_factory=list)
    
    # Raw data
    ocr_text: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    # Processing metadata
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate and clean data after initialization."""
        # Clean vendor name
        if self.vendor:
            self.vendor = self.vendor.strip()
        
        # Validate amount
        if self.amount is not None and self.amount < 0:
            self.amount = abs(self.amount)
        
        # Clean items list
        if self.items:
            self.items = [item.strip() for item in self.items if item.strip()]
    
    @property
    def is_valid(self) -> bool:
        """Check if receipt has minimum required data."""
        return (
            self.vendor is not None and 
            self.amount is not None and 
            self.amount > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert receipt to dictionary format."""
        return {
            'id': self.id,
            'image_path': self.image_path,
            'vendor': self.vendor,
            'amount': self.amount,
            'date': self.date,
            'items': self.items,
            'ocr_text': self.ocr_text,
            'raw_data': self.raw_data,
            'created_at': self.created_at.isoformat(),
            'is_valid': self.is_valid
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Receipt':
        """Create receipt from dictionary data."""
        # Handle datetime conversion
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()
        
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            image_path=data.get('image_path', ''),
            vendor=data.get('vendor'),
            amount=data.get('amount'),
            date=data.get('date'),
            items=data.get('items', []),
            ocr_text=data.get('ocr_text', ''),
            raw_data=data.get('raw_data', {}),
            created_at=created_at
        )

@dataclass
class ProcessedReceipt:
    """Processed receipt with categorization and additional business logic."""
    
    # Core receipt data
    receipt: Receipt
    
    # Processing results
    category: str = "Uncategorized"
    confidence_score: float = 0.0
    description: str = ""
    
    # Business data
    account_code: Optional[str] = None
    department: Optional[str] = None
    project_code: Optional[str] = None
    
    # Status tracking
    status: str = "processed"  # processed, approved, rejected, synced
    requires_review: bool = False
    notes: str = ""
    
    # Processing metadata
    processing_timestamp: datetime = field(default_factory=datetime.now)
    processed_by: str = "ai_system"
    
    def __post_init__(self):
        """Set up derived fields after initialization."""
        # Generate description if not provided
        if not self.description and self.receipt.vendor:
            self.description = f"{self.receipt.vendor} - {self.category}"
        
        # Mark for review if confidence is low
        if self.confidence_score < 0.7:
            self.requires_review = True
        
        # Mark for review if amount is high
        if self.receipt.amount and self.receipt.amount > 1000:
            self.requires_review = True
            self.notes += "High amount expense - requires approval. "
    
    @property
    def vendor(self) -> Optional[str]:
        """Convenience property to access vendor."""
        return self.receipt.vendor
    
    @property
    def amount(self) -> Optional[float]:
        """Convenience property to access amount."""
        return self.receipt.amount
    
    @property
    def date(self) -> Optional[str]:
        """Convenience property to access date."""
        return self.receipt.date
    
    @property
    def items(self) -> List[str]:
        """Convenience property to access items."""
        return self.receipt.items
    
    def approve(self, approved_by: str = "user"):
        """Mark the processed receipt as approved."""
        self.status = "approved"
        self.requires_review = False
        self.notes += f"Approved by {approved_by} at {datetime.now().isoformat()}. "
    
    def reject(self, reason: str = "", rejected_by: str = "user"):
        """Mark the processed receipt as rejected."""
        self.status = "rejected"
        self.requires_review = False
        self.notes += f"Rejected by {rejected_by}: {reason}. "
    
    def mark_synced(self, system: str = "quickbooks"):
        """Mark as synced to external system."""
        self.status = "synced"
        self.notes += f"Synced to {system} at {datetime.now().isoformat()}. "
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for export."""
        return {
            'id': self.receipt.id,
            'vendor': self.vendor,
            'amount': self.amount,
            'date': self.date,
            'category': self.category,
            'description': self.description,
            'items': self.items,
            'confidence_score': self.confidence_score,
            'account_code': self.account_code,
            'department': self.department,
            'project_code': self.project_code,
            'status': self.status,
            'requires_review': self.requires_review,
            'notes': self.notes,
            'processing_timestamp': self.processing_timestamp.isoformat(),
            'processed_by': self.processed_by,
            'image_path': self.receipt.image_path,
            'ocr_text': self.receipt.ocr_text
        }
    
    def to_excel_row(self) -> Dict[str, Any]:
        """Convert to Excel row format."""
        return {
            'Date': self.date,
            'Vendor': self.vendor,
            'Amount': self.amount,
            'Category': self.category,
            'Description': self.description,
            'Account Code': self.account_code,
            'Department': self.department,
            'Project Code': self.project_code,
            'Status': self.status,
            'Requires Review': 'Yes' if self.requires_review else 'No',
            'Confidence Score': f"{self.confidence_score:.2f}",
            'Notes': self.notes,
            'Processing Date': self.processing_timestamp.strftime('%Y-%m-%d %H:%M'),
            'Image File': self.receipt.image_path
        }
    
    def to_quickbooks_expense(self) -> Dict[str, Any]:
        """Convert to QuickBooks expense format."""
        return {
            'Line': [{
                'Amount': self.amount,
                'DetailType': 'AccountBasedExpenseLineDetail',
                'AccountBasedExpenseLineDetail': {
                    'AccountRef': {
                        'value': self.account_code or '1',
                        'name': self.category
                    },
                    'CustomerRef': {
                        'value': '1'  # Default customer
                    }
                }
            }],
            'PaymentType': 'Cash',
            'TotalAmt': self.amount,
            'PrivateNote': f"{self.description} | Processed by AI | Confidence: {self.confidence_score:.2f}"
        }
