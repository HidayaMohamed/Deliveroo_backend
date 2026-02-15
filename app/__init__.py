from flask import Flask
from flask_migrate import Migrate
from flask_mail import Mail
from flask_cors import CORS
from config import Config
from extensions import db, jwt



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
    mail.init_app(app)
    
    # Configure CORS - allow all origins for development
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
                 "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials", "X-Requested-With"],
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

    # Register Order routes as Blueprint (uses Flask Blueprint pattern)
    from app.routes.order_routes import orders_bp
    app.register_blueprint(orders_bp)

    # Register Admin resources
    from app.routes.admin_routes import AdminOrdersResource, AdminAssignCourierResource, AdminStatsResource
    api.add_resource(AdminOrdersResource, "/api/admin/orders")
    api.add_resource(AdminAssignCourierResource, "/api/admin/orders/<int:order_id>/assign")
    api.add_resource(AdminStatsResource, "/api/admin/dashboard")

    # Register Courier resources
    from app.routes.courier_routes import CourierOrdersResource, CourierUpdateStatusResource, CourierUpdateLocationResource
    api.add_resource(CourierOrdersResource, "/api/courier/orders")
    api.add_resource(CourierUpdateStatusResource, "/api/courier/orders/<int:order_id>/status")
    api.add_resource(CourierUpdateLocationResource, "/api/courier/location")

    # Register Payment routes as Blueprint
    from app.routes.payment_routes import payments_bp
    app.register_blueprint(payments_bp)

    return app
