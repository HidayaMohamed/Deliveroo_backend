"""
Order Validators for Deliveroo Delivery Platform
Handles all order data validation and request validation
"""

import re
from datetime import datetime


class OrderValidator:
    """
    Validator class for order-related data validation
    """
    
    # Kenyan phone number patterns
    PHONE_PATTERNS = [
        r'^254[71]\d{8}$',  # 2547XXXXXXXX or 2541XXXXXXXX
        r'^07[0-9]{8}$',     # 07XXXXXXXX
        r'^\+254[71]\d{8}$',  # +2547XXXXXXXX
    ]
    
    # Valid coordinate ranges for Kenya
    KENYA_LAT_RANGE = (-5.0, 6.0)
    KENYA_LNG_RANGE = (33.0, 42.0)
    
    @classmethod
    def validate_create_order(cls, data):
        """
        Validate data for creating a new order
        
        Args:
            data (dict): Order data from request
            
        Returns:
            tuple: (is_valid, validated_data, errors)
        """
        errors = []
        validated_data = {}
        
        # Required fields validation
        required_fields = [
            'pickup_lat', 'pickup_lng', 'pickup_address',
            'destination_lat', 'destination_lng', 'destination_address',
            'weight_kg'
        ]
        
        for field in required_fields:
            if field not in data or not data.get(field):
                errors.append(f"{field} is required")
            else:
                validated_data[field] = data[field]
        
        # If there are required field errors, return early
        if errors:
            return False, None, errors
        
        # Validate coordinates
        cls._validate_coordinates(
            validated_data.get('pickup_lat'),
            validated_data.get('pickup_lng'),
            'Pickup',
            errors
        )
        cls._validate_coordinates(
            validated_data.get('destination_lat'),
            validated_data.get('destination_lng'),
            'Destination',
            errors
        )
        
        # Validate weight
        weight_kg = float(validated_data.get('weight_kg', 0))
        if weight_kg <= 0:
            errors.append("Weight must be greater than 0 kg")
        elif weight_kg > 100:
            errors.append("Weight cannot exceed 100 kg")
        else:
            validated_data['weight_kg'] = weight_kg
        
        # Validate phone numbers (if provided)
        if data.get('pickup_phone'):
            if not cls.validate_phone_number(data['pickup_phone']):
                errors.append("Invalid pickup phone number format")
            else:
                validated_data['pickup_phone'] = cls.normalize_phone_number(data['pickup_phone'])
        
        if data.get('destination_phone'):
            if not cls.validate_phone_number(data['destination_phone']):
                errors.append("Invalid destination phone number format")
            else:
                validated_data['destination_phone'] = cls.normalize_phone_number(data['destination_phone'])
        
        # Validate optional boolean fields
        validated_data['fragile'] = data.get('fragile', False)
        validated_data['insurance_required'] = data.get('insurance_required', False)
        validated_data['is_express'] = data.get('is_express', False)
        validated_data['is_weekend'] = data.get('is_weekend', False)
        
        # Validate parcel description (optional)
        if data.get('parcel_description'):
            description = data['parcel_description'].strip()
            if len(description) < 3:
                errors.append("Parcel description must be at least 3 characters")
            elif len(description) > 500:
                errors.append("Parcel description cannot exceed 500 characters")
            else:
                validated_data['parcel_description'] = description
        
        # Validate parcel dimensions (optional, format: LxWxH)
        if data.get('parcel_dimensions'):
            if not cls.validate_dimensions(data['parcel_dimensions']):
                errors.append("Invalid parcel dimensions format (expected: LxWxH in cm)")
            else:
                validated_data['parcel_dimensions'] = data['parcel_dimensions']
        
        # Validate addresses
        cls._validate_address(validated_data.get('pickup_address'), 'Pickup address', errors)
        cls._validate_address(validated_data.get('destination_address'), 'Destination address', errors)
        
        # Check if coordinates are the same
        if (validated_data.get('pickup_lat') == validated_data.get('destination_lat') and
            validated_data.get('pickup_lng') == validated_data.get('destination_lng')):
            errors.append("Pickup and destination cannot be the same location")
        
        return len(errors) == 0, validated_data if errors else None, errors
    
    @classmethod
    def validate_update_destination(cls, data, current_status):
        """
        Validate data for updating order destination
        
        Args:
            data (dict): Update data from request
            current_status (str): Current order status
            
        Returns:
            tuple: (is_valid, validated_data, errors)
        """
        errors = []
        validated_data = {}
        
        # Required fields for destination update
        required_fields = ['destination_lat', 'destination_lng', 'destination_address']
        
        for field in required_fields:
            if field not in data or not data.get(field):
                errors.append(f"{field} is required")
            else:
                validated_data[field] = data[field]
        
        # If there are required field errors, return early
        if errors:
            return False, None, errors
        
        # Validate coordinates
        cls._validate_coordinates(
            validated_data.get('destination_lat'),
            validated_data.get('destination_lng'),
            'Destination',
            errors
        )
        
        # Validate address
        cls._validate_address(validated_data.get('destination_address'), 'Destination address', errors)
        
        # Validate optional phone
        if data.get('destination_phone'):
            if not cls.validate_phone_number(data['destination_phone']):
                errors.append("Invalid destination phone number format")
            else:
                validated_data['destination_phone'] = cls.normalize_phone_number(data['destination_phone'])
        
        return len(errors) == 0, validated_data if errors else None, errors
    
    @classmethod
    def validate_price_estimate(cls, data):
        """
        Validate data for price estimation
        
        Args:
            data (dict): Estimate request data
            
        Returns:
            tuple: (is_valid, validated_data, errors)
        """
        errors = []
        validated_data = {}
        
        required_fields = ['pickup_lat', 'pickup_lng', 'destination_lat', 'destination_lng', 'weight_kg']
        
        for field in required_fields:
            if field not in data or not data.get(field):
                errors.append(f"{field} is required")
            else:
                validated_data[field] = data[field]
        
        if errors:
            return False, None, errors
        
        # Validate coordinates
        cls._validate_coordinates(
            validated_data.get('pickup_lat'),
            validated_data.get('pickup_lng'),
            'Pickup',
            errors
        )
        cls._validate_coordinates(
            validated_data.get('destination_lat'),
            validated_data.get('destination_lng'),
            'Destination',
            errors
        )
        
        # Validate weight
        weight_kg = float(validated_data.get('weight_kg', 0))
        if weight_kg <= 0:
            errors.append("Weight must be greater than 0 kg")
        elif weight_kg > 100:
            errors.append("Weight cannot exceed 100 kg")
        else:
            validated_data['weight_kg'] = weight_kg
        
        # Optional fields
        validated_data['fragile'] = data.get('fragile', False)
        validated_data['insurance_required'] = data.get('insurance_required', False)
        validated_data['is_express'] = data.get('is_express', False)
        
        return len(errors) == 0, validated_data if errors else None, errors
    
    @classmethod
    def validate_coordinates(cls, lat, lng, prefix=''):
        """
        Validate latitude and longitude values
        
        Args:
            lat (float): Latitude
            lng (float): Longitude
            prefix (str): Prefix for error messages
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            lat = float(lat)
            lng = float(lng)
        except (TypeError, ValueError):
            return False, f"{prefix} coordinates must be valid numbers"
        
        if not (-90 <= lat <= 90):
            return False, f"{prefix} latitude must be between -90 and 90"
        if not (-180 <= lng <= 180):
            return False, f"{prefix} longitude must be between -180 and 180"
        
        return True, None
    
    @classmethod
    def _validate_coordinates(cls, lat, lng, prefix, errors):
        """Helper to validate coordinates and add to errors list"""
        is_valid, error = cls.validate_coordinates(lat, lng, prefix)
        if not is_valid:
            errors.append(error)
    
    @classmethod
    def validate_phone_number(cls, phone):
        """
        Validate Kenyan phone number format
        
        Args:
            phone (str): Phone number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not phone:
            return False
        
        phone = str(phone).strip()
        
        for pattern in cls.PHONE_PATTERNS:
            if re.match(pattern, phone):
                return True
        
        return False
    
    @classmethod
    def normalize_phone_number(cls, phone):
        """
        Normalize phone number to standard format (254XXXXXXXXX)
        
        Args:
            phone (str): Phone number to normalize
            
        Returns:
            str: Normalized phone number
        """
        phone = str(phone).strip()
        
        # Remove any spaces or dashes
        phone = re.sub(r'[\s-]', '', phone)
        
        # Convert +254 format to 254 format
        if phone.startswith('+254'):
            phone = phone[1:]
        
        # Convert 07 format to 2547 format
        if phone.startswith('07'):
            phone = '254' + phone[1:]
        
        return phone
    
    @classmethod
    def validate_dimensions(cls, dimensions):
        """
        Validate parcel dimensions format (LxWxH in cm)
        
        Args:
            dimensions (str): Dimensions string like "30x20x15"
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not dimensions:
            return True  # Optional field
        
        pattern = r'^\d+(\.\d+)?x\d+(\.\d+)?x\d+(\.\d+)?$'
        return bool(re.match(pattern, str(dimensions)))
    
    @classmethod
    def _validate_address(cls, address, field_name, errors):
        """Helper to validate address and add to errors list"""
        if not address or not address.strip():
            errors.append(f"{field_name} is required")
            return
        
        address = address.strip()
        
        if len(address) < 5:
            errors.append(f"{field_name} must be at least 5 characters")
        elif len(address) > 500:
            errors.append(f"{field_name} cannot exceed 500 characters")
    
    @staticmethod
    def validate_status_update(data, current_status):
        """
        Validate status update data
        
        Args:
            data (dict): Status update data
            current_status (str): Current order status
            
        Returns:
            tuple: (is_valid, new_status, errors)
        """
        errors = []
        
        if 'status' not in data:
            return False, None, ["status is required"]
        
        new_status = data['status'].upper()
        
        # Define valid status transitions
        valid_transitions = {
            'PENDING': ['PICKED_UP', 'CANCELLED'],
            'PICKED_UP': ['IN_TRANSIT', 'CANCELLED'],
            'IN_TRANSIT': ['DELIVERED'],
            'DELIVERED': [],
            'CANCELLED': []
        }
        
        if current_status not in valid_transitions:
            return False, None, [f"Invalid current status: {current_status}"]
        
        if new_status not in valid_transitions.get(current_status, []):
            valid_next = valid_transitions.get(current_status, [])
            if valid_next:
                errors.append(f"Cannot change status from {current_status} to {new_status}. "
                            f"Valid transitions: {', '.join(valid_next)}")
            else:
                errors.append(f"Cannot change status from {current_status} - order is final")
            return False, None, errors
        
        return True, new_status, errors
    
    @staticmethod
    def sanitize_input(data):
        """
        Sanitize string input to prevent injection attacks
        
        Args:
            data (dict): Input data
            
        Returns:
            dict: Sanitized data
        """
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Remove potential XSS content
                value = re.sub(r'<[^>]+>', '', value)
                # Trim whitespace
                value = value.strip()
                sanitized[key] = value
            else:
                sanitized[key] = value
        
        return sanitized
