import os
from flask import Flask
from flask_migrate import Migrate
from flask_mail import Mail
from flask_cors import CORS
from extensions import db, jwt, bcrypt
from dotenv import load_dotenv

# Load backend .env BEFORE importing Config (Config reads env at import time)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(BASE_DIR, '.env'))

from config import Config


migrate = Migrate()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models so Alembic can detect them
    from app import models
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    
    # Configure CORS with proper settings for preflight requests
    # Allow specific origin for frontend with credentials
    CORS(app,
         resources={
             r"/api/*": {
                 "origins": app.config.get("CORS_ORIGINS", ["http://localhost:5173"]),
                 "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
                 "supports_credentials": True,
                 "preflight_max_age": 86400  # 24 hours
             }
         },
         supports_credentials=True,
         expose_headers=["Content-Type", "Authorization"],
         max_age=86400
    )

    # Create API Instance
    from flask_restful import Api
    api = Api(app)


    # Register Auth resources
    from app.routes.auth_routes import RegisterResource, LoginResource, MeResource, RefreshResource
    api.add_resource(RegisterResource, "/api/auth/register")
    api.add_resource(LoginResource, "/api/auth/login")
    api.add_resource(MeResource, "/api/auth/me")
    api.add_resource(RefreshResource, "/api/auth/refresh")

    # Register admin resources
    from app.routes.admin_routes import (
        AdminUsersResource,
        AdminOrdersResource, 
        AdminAssignCourierResource,
        AdminStatsResource, 
        AdminUpdateOrderStatusResource
    )

    api.add_resource(AdminUsersResource, "/api/admin/users")
    api.add_resource(AdminOrdersResource, "/api/admin/orders")
    api.add_resource(AdminAssignCourierResource, "/api/admin/orders/<int:order_id>/assign")
    api.add_resource(AdminStatsResource, "/api/admin/stats")
    api.add_resource(AdminUpdateOrderStatusResource, "/api/admin/orders/<int:order_id>/status")


    # Register courier routes
    from app.routes.courier_routes import (
        CourierOrdersResource,
        CourierOrderDetailResource,
        CourierUpdateStatusResource,
        CourierUpdateLocationResource,
        CourierStatsResource
    )

    api.add_resource(CourierOrdersResource, "/api/courier/orders")
    api.add_resource(CourierOrderDetailResource,  "/api/courier/orders/<int:order_id>")
    api.add_resource(CourierUpdateStatusResource, "/api/courier/orders/<int:order_id>/status")
    api.add_resource(CourierUpdateLocationResource, "/api/courier/orders/<int:order_id>/location")
    api.add_resource(CourierStatsResource, "/api/courier/stats")

    # Register Blueprint routes
    from app.routes.order_routes import orders_bp
    app.register_blueprint(orders_bp)

    from app.routes.payment_routes import payments_bp
    app.register_blueprint(payments_bp)
    
    # Register users routes blueprint
    from app.routes.users_routes import users_bp
    app.register_blueprint(users_bp)
    
    # Register main routes blueprint
    from app.routes.main_routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

