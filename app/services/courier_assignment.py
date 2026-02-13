from math import radians, sin, cos, sqrt, atan2

from extensions import db
from app.models.courier import CourierProfile
from app.models.delivery import DeliveryOrder, OrderStatus
from app.models.notification import Notification
from app.models.user import User
from app.services.email_service import EmailService


def haversine_distance_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km."""
    r = 6371.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c


def find_nearest_available_courier(pickup_lat, pickup_lng, max_distance_km=20):
    """Find nearest active, verified, available courier with location."""
    candidates = CourierProfile.query.filter(
        CourierProfile.is_available.is_(True),
        CourierProfile.is_verified.is_(True),
        CourierProfile.current_latitude.isnot(None),
        CourierProfile.current_longitude.isnot(None),
    ).all()

    nearest = None
    nearest_distance = None

    for courier in candidates:
        distance = haversine_distance_km(
            float(pickup_lat),
            float(pickup_lng),
            float(courier.current_latitude),
            float(courier.current_longitude),
        )

        if distance <= max_distance_km and (nearest_distance is None or distance < nearest_distance):
            nearest = courier
            nearest_distance = distance

    return nearest, nearest_distance


def auto_assign_courier(order_id):
    """Auto-assign nearest courier to a paid order."""
    order = DeliveryOrder.query.get(order_id)

    if not order:
        return {"success": False, "message": "Order not found"}

    if order.courier_id:
        return {"success": False, "message": "Order already has assigned courier"}

    if order.status not in [OrderStatus.PENDING, OrderStatus.ASSIGNED]:
        return {"success": False, "message": f"Order status {order.status.value} cannot be auto-assigned"}

    courier_profile, distance_km = find_nearest_available_courier(order.pickup_lat, order.pickup_lng)

    if not courier_profile:
        return {"success": False, "message": "No available courier found"}

    courier_user = User.query.get(courier_profile.user_id)
    if not courier_user:
        return {"success": False, "message": "Courier user not found"}

    order.courier_id = courier_user.id
    order.status = OrderStatus.ASSIGNED

    db.session.add(Notification(
        user_id=order.user_id,
        order_id=order.id,
        type='COURIER_ASSIGNED',
        message=f'Courier {courier_user.full_name} has been auto-assigned to your order #{order.tracking_number}'
    ))
    db.session.add(Notification(
        user_id=courier_user.id,
        order_id=order.id,
        type='NEW_ASSIGNMENT',
        message=f'You have been auto-assigned to order #{order.tracking_number}'
    ))

    customer = User.query.get(order.user_id)
    if customer and customer.email:
        EmailService.send_courier_assigned(
            user_email=customer.email,
            order_id=order.id,
            courier_name=courier_user.full_name,
            courier_phone=courier_user.phone,
        )

    return {
        "success": True,
        "courier_id": courier_user.id,
        "courier_name": courier_user.full_name,
        "distance_km": round(distance_km, 2) if distance_km is not None else None,
    }
