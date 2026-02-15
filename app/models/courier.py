from extensions import db
from datetime import datetime

class CourierProfile(db.Model):
    __tablename__ = 'courier_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Vehicle info
    vehicle_type = db.Column(db.String(50))
    vehicle_registration = db.Column(db.String(50))
    license_number = db.Column(db.String(50))
    
    # Status
    is_available = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Stats
    total_deliveries = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=5.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='courier_profile')