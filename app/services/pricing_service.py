"""
Pricing Service for Deliveroo Delivery Platform
Handles all price calculations, weight categories, and delivery time estimates
"""

from decimal import Decimal
from enum import Enum
from datetime import datetime, timedelta


class WeightCategory(Enum):
    """Weight categories for pricing"""
    SMALL = 'SMALL'      # < 5kg
    MEDIUM = 'MEDIUM'    # 5-20kg
    LARGE = 'LARGE'      # 20-50kg
    XLARGE = 'XLARGE'    # > 50kg


class PricingService:
    """
    Service for calculating delivery prices and estimated delivery times
    All prices in Kenyan Shillings (KES)
    """
    
    # Base pricing configuration
    BASE_PRICE = Decimal('150.00')  # Base price for first 2km
    PRICE_PER_KM = Decimal('30.00')  # Price per km after first 2km
    FREE_DISTANCE_KM = 2.0  # Free distance included in base price
    
    # Weight-based pricing per kg (after first 5kg)
    PRICE_PER_KG = Decimal('10.00')
    FREE_WEIGHT_KG = 5.0  # Free weight included in base price
    
    # Extra charges
    FRAGILE_CHARGE = Decimal('50.00')
    INSURANCE_CHARGE = Decimal('100.00')
    WEEKEND_MULTIPLIER = Decimal('1.20')  # 20% extra on weekends
    EXPRESS_MULTIPLIER = Decimal('1.50')  # 50% extra for express delivery
    
    @staticmethod
    def determine_weight_category(weight_kg):
        """
        Determine weight category based on package weight
        
        Args:
            weight_kg (float): Weight of the package in kilograms
            
        Returns:
            WeightCategory: The weight category enum value
        """
        if weight_kg < 5:
            return WeightCategory.SMALL
        elif weight_kg < 20:
            return WeightCategory.MEDIUM
        elif weight_kg < 50:
            return WeightCategory.LARGE
        else:
            return WeightCategory.XLARGE
    
    @staticmethod
    def calculate_distance_price(distance_km):
        """
        Calculate price based on distance
        
        Args:
            distance_km (float): Total distance in kilometers
            
        Returns:
            Decimal: Price for the distance
        """
        if distance_km <= PricingService.FREE_DISTANCE_KM:
            return PricingService.BASE_PRICE
        
        extra_km = distance_km - PricingService.FREE_DISTANCE_KM
        return PricingService.BASE_PRICE + (Decimal(str(extra_km)) * PricingService.PRICE_PER_KM)
    
    @staticmethod
    def calculate_weight_price(weight_kg):
        """
        Calculate price based on weight
        
        Args:
            weight_kg (float): Weight of the package in kilograms
            
        Returns:
            Decimal: Price for the weight
        """
        if weight_kg <= PricingService.FREE_WEIGHT_KG:
            return Decimal('0.00')
        
        extra_kg = weight_kg - PricingService.FREE_WEIGHT_KG
        return Decimal(str(extra_kg)) * PricingService.PRICE_PER_KG
    
    @staticmethod
    def calculate_fragile_charge(is_fragile):
        """
        Calculate additional charge for fragile items
        
        Args:
            is_fragile (bool): Whether the package contains fragile items
            
        Returns:
            Decimal: Additional charge for fragile handling
        """
        return PricingService.FRAGILE_CHARGE if is_fragile else Decimal('0.00')
    
    @staticmethod
    def calculate_insurance_charge(needs_insurance):
        """
        Calculate insurance charge if required
        
        Args:
            needs_insurance (bool): Whether insurance is required
            
        Returns:
            Decimal: Insurance charge
        """
        return PricingService.INSURANCE_CHARGE if needs_insurance else Decimal('0.00')
    
    @staticmethod
    def is_weekend_delivery():
        """Check if current day is weekend"""
        return datetime.utcnow().weekday() >= 5  # 5 = Saturday, 6 = Sunday
    
    @classmethod
    def calculate_weekend_surcharge(cls, is_weekend, subtotal):
        """
        Calculate weekend surcharge
        
        Args:
            is_weekend (bool): Whether delivery is on weekend
            subtotal (Decimal): Base subtotal before weekend charge
            
        Returns:
            Decimal: Weekend surcharge amount
        """
        if is_weekend:
            return subtotal * (cls.WEEKEND_MULTIPLIER - Decimal('1.00'))
        return Decimal('0.00')
    
    @classmethod
    def calculate_express_surcharge(cls, is_express, subtotal):
        """
        Calculate express delivery surcharge
        
        Args:
            is_express (bool): Whether express delivery is requested
            subtotal (Decimal): Base subtotal before express charge
            
        Returns:
            Decimal: Express surcharge amount
        """
        if is_express:
            return subtotal * (cls.EXPRESS_MULTIPLIER - Decimal('1.00'))
        return Decimal('0.00')
    
    @classmethod
    def calculate_price_breakdown(cls, distance_km, weight_kg, is_fragile=False, 
                                   needs_insurance=False, is_express=False, 
                                   is_weekend=None):
        """
        Calculate complete price breakdown for a delivery
        
        Args:
            distance_km (float): Distance in kilometers
            weight_kg (float): Package weight in kilograms
            is_fragile (bool): Whether package is fragile
            needs_insurance (bool): Whether insurance is required
            is_express (bool): Whether express delivery is requested
            is_weekend (bool): Whether delivery is on weekend (auto-detected if None)
            
        Returns:
            dict: Complete price breakdown with all components
        """
        # Auto-detect weekend if not specified
        if is_weekend is None:
            is_weekend = cls.is_weekend_delivery()
        
        # Calculate individual components
        base_price = cls.calculate_distance_price(distance_km)
        weight_price = cls.calculate_weight_price(weight_kg)
        fragile_charge = cls.calculate_fragile_charge(is_fragile)
        insurance_charge = cls.calculate_insurance_charge(needs_insurance)
        
        # Subtotal before multipliers
        subtotal = base_price + weight_price + fragile_charge + insurance_charge
        
        # Calculate surcharges
        weekend_surcharge = cls.calculate_weekend_surcharge(is_weekend, subtotal)
        express_surcharge = cls.calculate_express_surcharge(is_express, subtotal)
        
        # Total extra charges
        extra_charges = fragile_charge + insurance_charge + weekend_surcharge + express_surcharge
        
        # Total price
        total_price = subtotal + weekend_surcharge + express_surcharge
        
        return {
            'base_price': float(base_price),
            'distance_price': float(base_price),
            'weight_price': float(weight_price),
            'fragile_charge': float(fragile_charge),
            'insurance_charge': float(insurance_charge),
            'weekend_surcharge': float(weekend_surcharge),
            'express_surcharge': float(express_surcharge),
            'extra_charges': {
                'fragile': float(fragile_charge),
                'insurance': float(insurance_charge),
                'weekend': float(weekend_surcharge),
                'express': float(express_surcharge),
                'total': float(extra_charges)
            },
            'subtotal_before_multipliers': float(subtotal),
            'total_price': float(total_price),
            'currency': 'KES'
        }
    
    @classmethod
    def calculate_estimated_delivery_time(cls, distance_km, is_express=False):
        """
        Calculate estimated delivery time in minutes
        
        Args:
            distance_km (float): Distance in kilometers
            is_express (bool): Whether express delivery is requested
            
        Returns:
            int: Estimated delivery time in minutes
        """
        # Base calculation: average speed of 30 km/h in city traffic
        base_minutes = (distance_km / 30) * 60  # Convert hours to minutes
        
        # Add preparation time
        preparation_time = 15  # 15 minutes for preparation
        
        # Express delivery is faster
        if is_express:
            base_minutes = base_minutes * 0.7  # 30% faster
        
        total_minutes = int(preparation_time + base_minutes)
        
        # Minimum 30 minutes, maximum based on distance
        return max(30, total_minutes)
    
    @classmethod
    def create_order_summary(cls, order_data):
        """
        Create complete order summary with pricing and delivery estimates
        
        Args:
            order_data (dict): Order data containing pickup, destination, and package info
            
        Returns:
            dict: Complete order summary including price breakdown and delivery estimates
        """
        # Extract relevant data
        pickup_lat = order_data.get('pickup_lat')
        pickup_lng = order_data.get('pickup_lng')
        destination_lat = order_data.get('destination_lat')
        destination_lng = order_data.get('destination_lng')
        weight_kg = float(order_data.get('weight_kg', 1))
        is_fragile = order_data.get('fragile', False)
        needs_insurance = order_data.get('insurance_required', False)
        is_express = order_data.get('is_express', False)
        is_weekend = order_data.get('is_weekend', False)
        
        # Calculate distance
        from app.services.maps_service import MapsService
        maps_service = MapsService()
        
        distance_result = maps_service.calculate_distance(
            origin=(pickup_lat, pickup_lng),
            destination=(destination_lat, destination_lng)
        )
        
        distance_km = distance_result.get('distance_km', 0)
        duration_minutes = distance_result.get('duration_minutes', 0)
        
        # Calculate price breakdown
        price_breakdown = cls.calculate_price_breakdown(
            distance_km=distance_km,
            weight_kg=weight_kg,
            is_fragile=is_fragile,
            needs_insurance=needs_insurance,
            is_express=is_express,
            is_weekend=is_weekend
        )
        
        # Calculate estimated delivery time
        estimated_delivery_minutes = cls.calculate_estimated_delivery_time(
            distance_km=distance_km,
            is_express=is_express
        )
        
        # Determine weight category
        weight_category = cls.determine_weight_category(weight_kg)
        
        return {
            'distance': {
                'km': distance_km,
                'duration_minutes': duration_minutes
            },
            'price_breakdown': price_breakdown,
            'estimated_delivery': {
                'minutes': estimated_delivery_minutes,
                'hours': round(estimated_delivery_minutes / 60, 1)
            },
            'weight_category': weight_category.value,
            'weight_kg': weight_kg
        }
    
    @staticmethod
    def validate_price_input(distance_km, weight_kg):
        """
        Validate price calculation inputs
        
        Args:
            distance_km (float): Distance in kilometers
            weight_kg (float): Package weight in kilograms
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if distance_km <= 0:
            return False, "Distance must be greater than 0"
        if weight_kg <= 0:
            return False, "Weight must be greater than 0"
        if weight_kg > 100:
            return False, "Weight cannot exceed 100kg"
        return True, None
    
    @staticmethod
    def format_price(amount):
        """
        Format price for display
        
        Args:
            amount (float): Price amount
            
        Returns:
            str: Formatted price string
        """
        return f"KES {amount:,.2f}"
