"""
QuickBooks API Integration

This module provides integration with QuickBooks Online API for automated
expense entry and synchronization.
"""

import logging
from typing import Optional, Dict, Any, List
import requests
from datetime import datetime
import json

from models.receipt import ProcessedReceipt
from utils.config import Config

logger = logging.getLogger(__name__)

class QuickBooksAPI:
    """QuickBooks Online API integration for expense management."""
    
    def __init__(self, config: Config):
        """Initialize QuickBooks API client."""
        self.config = config
        self.client_id = config.QB_CLIENT_ID
        self.client_secret = config.QB_CLIENT_SECRET
        self.environment = getattr(config, 'QB_ENVIRONMENT', 'sandbox')
        self.redirect_uri = getattr(config, 'QB_REDIRECT_URI', 'http://localhost:8080/callback')
        
        # API endpoints
        if self.environment == 'production':
            self.base_url = "https://quickbooks-api.intuit.com"
            self.discovery_url = "https://developer.api.intuit.com/openid_connect/discovery/production"
        else:
            self.base_url = "https://sandbox-quickbooks.api.intuit.com"
            self.discovery_url = "https://developer.api.intuit.com/openid_connect/discovery/sandbox"
        
        # Session state
        self.access_token = None
        self.refresh_token = None
        self.company_id = None
        self.token_expires_at = None
        
        logger.info(f"QuickBooks API initialized for {self.environment} environment")
    
    def get_authorization_url(self) -> str:
        """
        Generate QuickBooks OAuth authorization URL.
        
        Returns:
            Authorization URL for user to visit
        """
        from urllib.parse import urlencode
        
        params = {
            'client_id': self.client_id,
            'scope': 'com.intuit.quickbooks.accounting',
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'access_type': 'offline'
        }
        
        auth_url = f"https://appcenter.intuit.com/connect/oauth2"
        return f"{auth_url}?{urlencode(params)}"
    
    def exchange_code_for_tokens(self, authorization_code: str, realm_id: str) -> bool:
        """
        Exchange authorization code for access tokens.
        
        Args:
            authorization_code: Code received from OAuth callback
            realm_id: Company ID from OAuth callback
            
        Returns:
            True if token exchange successful
        """
        try:
            token_url = f"{self.discovery_url.replace('discovery', 'oauth2/v1/tokens')}"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': self.redirect_uri
            }
            
            # Basic auth with client credentials
            import base64
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            headers['Authorization'] = f"Basic {encoded_credentials}"
            
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
            self.company_id = realm_id
            
            # Calculate token expiration
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now().timestamp() + expires_in
            
            logger.info("Successfully obtained QuickBooks access tokens")
            return True
            
        except Exception as e:
            logger.error(f"Failed to exchange authorization code: {str(e)}")
            return False
    
    def refresh_access_token(self) -> bool:
        """
        Refresh the access token using refresh token.
        
        Returns:
            True if refresh successful
        """
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False
        
        try:
            token_url = f"{self.discovery_url.replace('discovery', 'oauth2/v1/tokens')}"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            
            # Basic auth
            import base64
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            headers['Authorization'] = f"Basic {encoded_credentials}"
            
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            if 'refresh_token' in token_data:
                self.refresh_token = token_data['refresh_token']
            
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now().timestamp() + expires_in
            
            logger.info("Successfully refreshed QuickBooks access token")
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh access token: {str(e)}")
            return False
    
    def _ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token."""
        if not self.access_token:
            logger.error("No access token available")
            return False
        
        # Check if token is expired
        if self.token_expires_at and datetime.now().timestamp() >= self.token_expires_at - 300:  # 5 min buffer
            logger.info("Access token expired, attempting refresh")
            return self.refresh_access_token()
        
        return True
    
    def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make authenticated API request to QuickBooks.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data for POST/PUT requests
            
        Returns:
            Response data or None if failed
        """
        if not self._ensure_valid_token():
            return None
        
        if not self.company_id:
            logger.error("No company ID available")
            return None
        
        url = f"{self.base_url}/v3/company/{self.company_id}/{endpoint}"
        
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'Accept': 'application/json'
        }
        
        if data:
            headers['Content-Type'] = 'application/json'
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=json.dumps(data) if data else None)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"QuickBooks API request failed: {str(e)}")
            return None
    
    def create_expense(self, processed_receipt: ProcessedReceipt) -> Optional[str]:
        """
        Create an expense entry in QuickBooks.
        
        Args:
            processed_receipt: Processed receipt to create expense from
            
        Returns:
            QuickBooks expense ID if successful, None otherwise
        """
        try:
            # Prepare expense data
            expense_data = {
                "PurchaseByVendor": {
                    "VendorRef": {
                        "value": "1"  # Default vendor - should be mapped properly
                    },
                    "Line": [{
                        "Amount": processed_receipt.amount,
                        "DetailType": "AccountBasedExpenseLineDetail",
                        "AccountBasedExpenseLineDetail": {
                            "AccountRef": {
                                "value": self._get_account_id(processed_receipt.category),
                                "name": processed_receipt.category
                            }
                        }
                    }],
                    "TotalAmt": processed_receipt.amount,
                    "PrivateNote": f"Auto-generated from receipt: {processed_receipt.description}"
                }
            }
            
            # Create the expense
            response = self._make_api_request('POST', 'purchase', expense_data)
            
            if response and 'QueryResponse' in response:
                expense_id = response['QueryResponse']['Purchase'][0]['Id']
                logger.info(f"Created QuickBooks expense: {expense_id}")
                return expense_id
            else:
                logger.error("Failed to create QuickBooks expense")
                return None
                
        except Exception as e:
            logger.error(f"Error creating QuickBooks expense: {str(e)}")
            return None
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """
        Get chart of accounts from QuickBooks.
        
        Returns:
            List of account dictionaries
        """
        response = self._make_api_request('GET', "accounts")
        
        if response and 'QueryResponse' in response:
            return response['QueryResponse'].get('Account', [])
        else:
            logger.error("Failed to retrieve QuickBooks accounts")
            return []
    
    def get_vendors(self) -> List[Dict[str, Any]]:
        """
        Get vendors from QuickBooks.
        
        Returns:
            List of vendor dictionaries
        """
        response = self._make_api_request('GET', "vendors")
        
        if response and 'QueryResponse' in response:
            return response['QueryResponse'].get('Vendor', [])
        else:
            logger.error("Failed to retrieve QuickBooks vendors")
            return []
    
    def create_vendor(self, vendor_name: str) -> Optional[str]:
        """
        Create a new vendor in QuickBooks.
        
        Args:
            vendor_name: Name of the vendor to create
            
        Returns:
            Vendor ID if successful, None otherwise
        """
        vendor_data = {
            "Vendor": {
                "Name": vendor_name
            }
        }
        
        response = self._make_api_request('POST', 'vendor', vendor_data)
        
        if response and 'QueryResponse' in response:
            vendor_id = response['QueryResponse']['Vendor'][0]['Id']
            logger.info(f"Created QuickBooks vendor: {vendor_id}")
            return vendor_id
        else:
            logger.error(f"Failed to create vendor: {vendor_name}")
            return None
    
    def _get_account_id(self, category: str) -> str:
        """
        Map expense category to QuickBooks account ID.
        
        Args:
            category: Expense category
            
        Returns:
            QuickBooks account ID
        """
        # Default mapping - should be customized based on company's chart of accounts
        category_mapping = {
            "Office Supplies": "64",  # Office Supplies expense account
            "Meals & Entertainment": "65",  # Meals and Entertainment
            "Travel": "66",  # Travel expense
            "Technology": "67",  # Equipment/Technology
            "Marketing": "68",  # Marketing and Advertising
            "Utilities": "69",  # Utilities
            "Professional Services": "70",  # Professional fees
            "Miscellaneous": "71"  # Miscellaneous expenses
        }
        
        return category_mapping.get(category, "71")  # Default to miscellaneous
    
    def sync_processed_receipts(self, receipts: List[ProcessedReceipt]) -> Dict[str, Any]:
        """
        Sync multiple processed receipts to QuickBooks.
        
        Args:
            receipts: List of processed receipts to sync
            
        Returns:
            Sync results summary
        """
        results = {
            'successful': 0,
            'failed': 0,
            'errors': [],
            'created_ids': []
        }
        
        for receipt in receipts:
            if receipt.status != 'approved':
                logger.warning(f"Skipping non-approved receipt: {receipt.receipt.id}")
                continue
            
            expense_id = self.create_expense(receipt)
            
            if expense_id:
                results['successful'] += 1
                results['created_ids'].append(expense_id)
                
                # Mark receipt as synced
                receipt.mark_synced('quickbooks')
            else:
                results['failed'] += 1
                results['errors'].append(f"Failed to sync receipt: {receipt.receipt.id}")
        
        logger.info(f"QuickBooks sync completed: {results['successful']} successful, {results['failed']} failed")
        return results
