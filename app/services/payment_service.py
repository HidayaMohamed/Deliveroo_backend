"""
M-Pesa Daraja API Integration for Deliveroo
Handles STK Push (Lipa Na M-Pesa Online) payments

Place this file in: app/services/payment_service.py
"""
import os
import requests
import logging
from datetime import datetime
from base64 import b64encode

logger = logging.getLogger(__name__)


class MpesaService:
    """M-Pesa Daraja API Service"""
    
    def __init__(self):
        # Load from environment or use sandbox defaults
        self.environment = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
        self.consumer_key = os.getenv(
            'MPESA_CONSUMER_KEY', 
            'PGpLACdDg3rcDq7cKE2shAk1ntG8v6TrTUTcVKdAnby3NoTN'
        )
        self.consumer_secret = os.getenv(
            'MPESA_CONSUMER_SECRET', 
            'xegydTwI5qolajTu8y6FAcjnnXmpGCGbmeoIZexXkdfYCSmpHm1DRgL5EHXOnmNj'
        )
        self.shortcode = os.getenv('MPESA_SHORTCODE', '174379')
        self.passkey = os.getenv(
            'MPESA_PASSKEY', 
            'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        )
        self.callback_url = os.getenv(
            'MPESA_CALLBACK_URL', 
            'https://your-ngrok-url.ngrok.io/api/payments/callback'
        )
        
        # Set base URL based on environment
        if self.environment == 'production':
            self.base_url = 'https://api.safaricom.co.ke'
        else:
            self.base_url = 'https://sandbox.safaricom.co.ke'
    
    def _get_access_token(self):
        """
        Generate OAuth access token from Daraja API
        
        Returns:
            str: Access token or None if failed
        """
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        
        # Encode credentials
        credentials = b64encode(
            f"{self.consumer_key}:{self.consumer_secret}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            logger.info("M-Pesa access token obtained successfully")
            return result.get('access_token')
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get M-Pesa access token: {e}")
            return None
    
    def _generate_password(self):
        """
        Generate Lipa Na M-Pesa password
        
        Returns:
            tuple: (password, timestamp)
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        password = b64encode(password_str.encode()).decode()
        return password, timestamp
    
    def _format_phone(self, phone):
        """
        Format phone number to 254XXXXXXXXX format
        
        Args:
            phone (str): Phone number in any format
            
        Returns:
            str: Formatted phone number
        """
        phone = str(phone).strip().replace(" ", "").replace("-", "")
        
        if phone.startswith("+"):
            phone = phone[1:]
        if phone.startswith("0"):
            phone = "254" + phone[1:]
        if not phone.startswith("254"):
            phone = "254" + phone
            
        return phone
    
    def initiate_stk_push(self, phone_number, amount, order_id, description=None):
        """
        Initiate M-Pesa STK Push to customer's phone
        
        Args:
            phone_number (str): Customer's phone number
            amount (int): Amount to charge (must be >= 1)
            order_id (int): Order ID for reference
            description (str): Optional transaction description
            
        Returns:
            dict: Response with success status and data
        """
        # Get access token
        access_token = self._get_access_token()
        if not access_token:
            return {
                'success': False,
                'error': 'Failed to authenticate with M-Pesa',
                'error_code': 'AUTH_FAILED'
            }
        
        # Format phone and generate password
        phone = self._format_phone(phone_number)
        password, timestamp = self._generate_password()
        
        # Prepare request
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": self.callback_url,
            "AccountReference": f"DELIVEROO-{order_id}",
            "TransactionDesc": description or f"Payment for Order #{order_id}"
        }
        
        logger.info(f"Initiating STK push to {phone} for KES {amount}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            result = response.json()
            
            # Check if STK push was initiated successfully
            if result.get('ResponseCode') == '0':
                logger.info(f"STK push sent successfully. CheckoutRequestID: {result.get('CheckoutRequestID')}")
                return {
                    'success': True,
                    'checkout_request_id': result.get('CheckoutRequestID'),
                    'merchant_request_id': result.get('MerchantRequestID'),
                    'response_description': result.get('ResponseDescription'),
                    'message': 'STK push sent. Check your phone to complete payment.'
                }
            else:
                logger.warning(f"STK push failed: {result}")
                return {
                    'success': False,
                    'error': result.get('errorMessage') or result.get('ResponseDescription'),
                    'error_code': result.get('errorCode') or result.get('ResponseCode'),
                    'raw_response': result
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa STK push request failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'REQUEST_FAILED'
            }
    
    def query_stk_status(self, checkout_request_id):
        """
        Query the status of an STK Push transaction
        
        Args:
            checkout_request_id (str): CheckoutRequestID from STK push response
            
        Returns:
            dict: Transaction status
        """
        access_token = self._get_access_token()
        if not access_token:
            return {
                'success': False,
                'error': 'Failed to authenticate with M-Pesa'
            }
        
        password, timestamp = self._generate_password()
        
        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            result = response.json()
            
            result_code = result.get('ResultCode')
            
            # ResultCode meanings
            status_map = {
                '0': ('completed', 'Transaction successful'),
                '1': ('failed', 'Insufficient balance'),
                '1032': ('cancelled', 'Transaction cancelled by user'),
                '1037': ('timeout', 'Transaction timed out'),
                '2001': ('failed', 'Wrong PIN entered'),
            }
            
            if str(result_code) in status_map:
                status, description = status_map[str(result_code)]
                return {
                    'success': True,
                    'status': status,
                    'result_code': result_code,
                    'result_description': result.get('ResultDesc', description),
                    'raw_response': result
                }
            else:
                return {
                    'success': True,
                    'status': 'unknown',
                    'result_code': result_code,
                    'result_description': result.get('ResultDesc'),
                    'raw_response': result
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa status query failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def parse_callback(callback_data):
        """
        Parse M-Pesa callback data
        
        Args:
            callback_data (dict): Raw callback from M-Pesa
            
        Returns:
            dict: Parsed payment result
        """
        try:
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            
            result = {
                'merchant_request_id': stk_callback.get('MerchantRequestID'),
                'checkout_request_id': stk_callback.get('CheckoutRequestID'),
                'result_code': stk_callback.get('ResultCode'),
                'result_description': stk_callback.get('ResultDesc')
            }
            
            # If successful (ResultCode 0), extract metadata
            if stk_callback.get('ResultCode') == 0:
                metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                
                for item in metadata:
                    name = item.get('Name')
                    value = item.get('Value')
                    
                    if name == 'Amount':
                        result['amount'] = value
                    elif name == 'MpesaReceiptNumber':
                        result['receipt_number'] = value
                    elif name == 'TransactionDate':
                        result['transaction_date'] = str(value)
                    elif name == 'PhoneNumber':
                        result['phone_number'] = str(value)
                
                result['success'] = True
                result['status'] = 'completed'
                
                logger.info(f"Payment successful - Receipt: {result.get('receipt_number')}")
            else:
                result['success'] = False
                result['status'] = 'failed'
                
                logger.warning(f"Payment failed - {result.get('result_description')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse M-Pesa callback: {e}")
            return {
                'success': False,
                'error': str(e),
                'raw_data': callback_data
            }


# Singleton instance for easy importing
mpesa_service = MpesaService()