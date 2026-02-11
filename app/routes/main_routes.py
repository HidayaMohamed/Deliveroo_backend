"""
Main Routes Blueprint
Flask Blueprint for main application routes (health check, root, test-email)
"""
from flask import Blueprint, jsonify
from flask_mail import Message, Mail

# Create Blueprint for main routes
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    API root endpoint with available routes (dynamically extracted from url_map)
    Returns JSON with message, status, and all registered API endpoints
    """
    from flask import current_app
    endpoints = []
    
    # Iterate through all registered routes
    for rule in current_app.url_map.iter_rules():
        # Skip static routes and the root health check
        if rule.endpoint in ['static', 'health']:
            continue
        
        # Skip routes with no methods (usually internal routes)
        if not rule.methods:
            continue
        
        # Convert methods set to sorted list, excluding HEAD and OPTIONS
        methods = sorted([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
        
        # Skip if no valid HTTP methods remain
        if not methods:
            continue
        
        # Format the rule string
        endpoint = rule.rule
        
        endpoints.append({
            'endpoint': endpoint,
            'methods': methods
        })
    
    return {
        'message': 'Backend running successfully',
        'status': 'OK',
        'endpoints': endpoints
    }, 200


@main_bp.route('/health')
def health_check():
    """Simple health check endpoint"""
    from extensions import db
    from flask import current_app
    
    return {
        'status': 'healthy',
        'message': 'Deliveroo API is running',
        'database': 'connected' if db.engine.url else 'not configured'
    }, 200


@main_bp.route('/test-email')
def test_email():
    """
    Test email sending route.
    Sends a test email to a specified email address.
    
    Query Parameters:
        email: Target email address (required)
        
    Returns:
        JSON response with success/failure status
    """
    from flask import request, current_app
    from flask_mail import Mail
    
    mail = Mail(current_app)
    target_email = request.args.get('email')
    
    if not target_email:
        return {
            'success': False,
            'message': 'Email address is required. Use ?email=your@email.com',
            'example': '/test-email?email=user@example.com'
        }, 400
    
    try:
        msg = Message(
            subject='Deliveroo - Test Email',
            recipients=[target_email],
            body=f"""
Hello,

This is a test email from Deliveroo Backend.

Your email configuration is working correctly!

Best regards,
Deliveroo Team
"""
        )
        mail.send(msg)
        
        return {
            'success': True,
            'message': f'Test email sent successfully to {target_email}',
            'recipient': target_email
        }, 200
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to send email: {str(e)}',
            'error_type': type(e).__name__
        }, 500
