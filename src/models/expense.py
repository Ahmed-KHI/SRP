"""
Expense Data Models

Additional models for expense management and categorization.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ExpenseStatus(Enum):
    """Expense processing status."""
    PENDING = "pending"
    PROCESSED = "processed"
    APPROVED = "approved"
    REJECTED = "rejected"
    SYNCED = "synced"

class ExpenseCategory(Enum):
    """Standard expense categories."""
    OFFICE_SUPPLIES = "Office Supplies"
    MEALS_ENTERTAINMENT = "Meals & Entertainment"
    TRAVEL = "Travel"
    TECHNOLOGY = "Technology"
    MARKETING = "Marketing"
    UTILITIES = "Utilities"
    PROFESSIONAL_SERVICES = "Professional Services"
    MISCELLANEOUS = "Miscellaneous"
    UNCATEGORIZED = "Uncategorized"

@dataclass
class ExpenseRule:
    """Business rule for expense categorization and validation."""
    
    name: str
    category: str
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    priority: int = 0
    active: bool = True
    
    def applies_to(self, expense_data: Dict[str, Any]) -> bool:
        """Check if this rule applies to the given expense data."""
        for field, condition in self.conditions.items():
            if field not in expense_data:
                return False
            
            value = expense_data[field]
            
            if isinstance(condition, dict):
                # Complex condition
                if 'min' in condition and value < condition['min']:
                    return False
                if 'max' in condition and value > condition['max']:
                    return False
                if 'contains' in condition and condition['contains'].lower() not in str(value).lower():
                    return False
                if 'equals' in condition and value != condition['equals']:
                    return False
            else:
                # Simple equality condition
                if value != condition:
                    return False
        
        return True
    
    def apply_actions(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the rule actions to expense data."""
        for action, value in self.actions.items():
            if action == 'set_category':
                expense_data['category'] = value
            elif action == 'set_account_code':
                expense_data['account_code'] = value
            elif action == 'set_department':
                expense_data['department'] = value
            elif action == 'require_approval':
                expense_data['requires_review'] = value
            elif action == 'add_note':
                current_notes = expense_data.get('notes', '')
                expense_data['notes'] = f"{current_notes} {value}".strip()
        
        return expense_data

@dataclass
class BudgetCategory:
    """Budget tracking for expense categories."""
    
    category: str
    budget_amount: float
    spent_amount: float = 0.0
    period: str = "monthly"  # monthly, quarterly, yearly
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    @property
    def remaining_budget(self) -> float:
        """Calculate remaining budget amount."""
        return max(0, self.budget_amount - self.spent_amount)
    
    @property
    def utilization_percentage(self) -> float:
        """Calculate budget utilization percentage."""
        if self.budget_amount == 0:
            return 0.0
        return (self.spent_amount / self.budget_amount) * 100
    
    @property
    def is_over_budget(self) -> bool:
        """Check if spending exceeds budget."""
        return self.spent_amount > self.budget_amount
    
    def add_expense(self, amount: float):
        """Add an expense to this budget category."""
        self.spent_amount += amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'category': self.category,
            'budget_amount': self.budget_amount,
            'spent_amount': self.spent_amount,
            'remaining_budget': self.remaining_budget,
            'utilization_percentage': self.utilization_percentage,
            'is_over_budget': self.is_over_budget,
            'period': self.period,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None
        }

@dataclass
class ExpenseReport:
    """Expense report summary and analytics."""
    
    title: str
    period_start: datetime
    period_end: datetime
    total_expenses: float = 0.0
    expense_count: int = 0
    categories: Dict[str, float] = field(default_factory=dict)
    vendors: Dict[str, float] = field(default_factory=dict)
    
    # Analytics
    average_expense: float = 0.0
    largest_expense: float = 0.0
    smallest_expense: float = 0.0
    
    # Status breakdown
    approved_amount: float = 0.0
    pending_amount: float = 0.0
    rejected_amount: float = 0.0
    
    def add_expense(self, processed_receipt):
        """Add an expense to the report."""
        amount = processed_receipt.amount or 0.0
        
        # Update totals
        self.total_expenses += amount
        self.expense_count += 1
        
        # Update categories
        category = processed_receipt.category
        self.categories[category] = self.categories.get(category, 0) + amount
        
        # Update vendors
        vendor = processed_receipt.vendor or "Unknown"
        self.vendors[vendor] = self.vendors.get(vendor, 0) + amount
        
        # Update analytics
        self.average_expense = self.total_expenses / self.expense_count
        self.largest_expense = max(self.largest_expense, amount)
        if self.smallest_expense == 0.0 or amount < self.smallest_expense:
            self.smallest_expense = amount
        
        # Update status amounts
        if processed_receipt.status == "approved":
            self.approved_amount += amount
        elif processed_receipt.status == "rejected":
            self.rejected_amount += amount
        else:
            self.pending_amount += amount
    
    def get_top_categories(self, limit: int = 5) -> List[tuple]:
        """Get top expense categories by amount."""
        return sorted(
            self.categories.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:limit]
    
    def get_top_vendors(self, limit: int = 5) -> List[tuple]:
        """Get top vendors by expense amount."""
        return sorted(
            self.vendors.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:limit]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format."""
        return {
            'title': self.title,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'total_expenses': self.total_expenses,
            'expense_count': self.expense_count,
            'average_expense': self.average_expense,
            'largest_expense': self.largest_expense,
            'smallest_expense': self.smallest_expense,
            'approved_amount': self.approved_amount,
            'pending_amount': self.pending_amount,
            'rejected_amount': self.rejected_amount,
            'categories': self.categories,
            'vendors': self.vendors,
            'top_categories': self.get_top_categories(),
            'top_vendors': self.get_top_vendors()
        }
