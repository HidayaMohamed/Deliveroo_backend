"""
Route Validation Utilities
Provides functions to validate and test all registered routes in the Flask application.
"""
from flask import Flask


def validate_all_routes(flask_app: Flask):
    """
    Validate all registered endpoints in the Flask application.
    This utility function:
    - Iterates through all registered routes
    - Logs them in the console
    - Ensures each route is properly registered
    - Returns a validation report
    
    Args:
        flask_app: Flask application instance
        
    Returns:
        dict: Validation report with status and list of endpoints
    """
    validation_results = {
        'total_routes': 0,
        'valid_routes': 0,
        'invalid_routes': 0,
        'routes': [],
        'status': 'OK'
    }
    
    print("\n" + "=" * 60)
    print("🔍 ROUTE VALIDATION REPORT")
    print("=" * 60)
    
    for rule in flask_app.url_map.iter_rules():
        # Skip static routes
        if rule.endpoint == 'static':
            continue
            
        validation_results['total_routes'] += 1
        
        # Get methods for this route
        methods = sorted([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
        
        # Check if route has valid methods
        if not methods:
            validation_results['invalid_routes'] += 1
            route_info = {
                'endpoint': rule.rule,
                'endpoint_name': rule.endpoint,
                'methods': list(rule.methods),
                'status': 'INVALID - No valid HTTP methods'
            }
            validation_results['routes'].append(route_info)
            print(f"❌ {rule.rule} - INVALID (no valid methods)")
            continue
        
        # Route is valid
        validation_results['valid_routes'] += 1
        route_info = {
            'endpoint': rule.rule,
            'endpoint_name': rule.endpoint,
            'methods': methods,
            'status': 'VALID'
        }
        validation_results['routes'].append(route_info)
        print(f"✅ {rule.rule} - {', '.join(methods)}")
    
    print("=" * 60)
    print(f"📊 Total Routes: {validation_results['total_routes']}")
    print(f"✅ Valid Routes: {validation_results['valid_routes']}")
    print(f"❌ Invalid Routes: {validation_results['invalid_routes']}")
    print("=" * 60 + "\n")
    
    return validation_results


def test_all_routes(flask_app: Flask):
    """
    Test basic route responses to confirm they respond correctly.
    
    Args:
        flask_app: Flask application instance
        
    Returns:
        dict: Test results for each route
    """
    from flask import Flask
    
    test_results = {
        'tested_routes': 0,
        'successful_routes': 0,
        'failed_routes': 0,
        'results': []
    }
    
    print("\n" + "=" * 60)
    print("🧪 ROUTE RESPONSE TEST")
    print("=" * 60)
    
    with flask_app.test_client() as client:
        # Test the root endpoint
        test_results['tested_routes'] += 1
        try:
            response = client.get('/')
            if response.status_code == 200:
                test_results['successful_routes'] += 1
                test_results['results'].append({
                    'endpoint': '/',
                    'method': 'GET',
                    'status_code': response.status_code,
                    'status': 'SUCCESS'
                })
                print(f"✅ GET / - Status: {response.status_code}")
            else:
                test_results['failed_routes'] += 1
                test_results['results'].append({
                    'endpoint': '/',
                    'method': 'GET',
                    'status_code': response.status_code,
                    'status': 'FAILED'
                })
                print(f"❌ GET / - Status: {response.status_code}")
        except Exception as e:
            test_results['failed_routes'] += 1
            test_results['results'].append({
                'endpoint': '/',
                'method': 'GET',
                'status_code': None,
                'status': f'ERROR: {str(e)}'
            })
            print(f"❌ GET / - ERROR: {str(e)}")
        
        # Test health endpoint
        test_results['tested_routes'] += 1
        try:
            response = client.get('/health')
            if response.status_code == 200:
                test_results['successful_routes'] += 1
                test_results['results'].append({
                    'endpoint': '/health',
                    'method': 'GET',
                    'status_code': response.status_code,
                    'status': 'SUCCESS'
                })
                print(f"✅ GET /health - Status: {response.status_code}")
            else:
                test_results['failed_routes'] += 1
                test_results['results'].append({
                    'endpoint': '/health',
                    'method': 'GET',
                    'status_code': response.status_code,
                    'status': 'FAILED'
                })
                print(f"❌ GET /health - Status: {response.status_code}")
        except Exception as e:
            test_results['failed_routes'] += 1
            test_results['results'].append({
                'endpoint': '/health',
                'method': 'GET',
                'status_code': None,
                'status': f'ERROR: {str(e)}'
            })
            print(f"❌ GET /health - ERROR: {str(e)}")
    
    print("=" * 60)
    print(f"📊 Tested: {test_results['tested_routes']}")
    print(f"✅ Successful: {test_results['successful_routes']}")
    print(f"❌ Failed: {test_results['failed_routes']}")
    print("=" * 60 + "\n")
    
    return test_results


def check_mail_configuration(flask_app: Flask):
    """
    Verify Flask-Mail is properly configured.
    Checks all required configuration settings.
    
    Args:
        flask_app: Flask application instance
        
    Returns:
        dict: Configuration status and details
    """
    config_status = {
        'MAIL_SERVER': False,
        'MAIL_PORT': False,
        'MAIL_USERNAME': False,
        'MAIL_PASSWORD': False,
        'MAIL_USE_TLS': False,
        'MAIL_USE_SSL': False,
        'is_configured': False,
        'details': {}
    }
    
    print("\n" + "=" * 60)
    print("📧 FLASK-MAIL CONFIGURATION CHECK")
    print("=" * 60)
    
    # Check each configuration
    if flask_app.config.get('MAIL_SERVER'):
        config_status['MAIL_SERVER'] = True
        config_status['details']['MAIL_SERVER'] = flask_app.config['MAIL_SERVER']
        print(f"✅ MAIL_SERVER: {flask_app.config['MAIL_SERVER']}")
    else:
        print("❌ MAIL_SERVER: Not configured")
    
    if flask_app.config.get('MAIL_PORT'):
        config_status['MAIL_PORT'] = True
        config_status['details']['MAIL_PORT'] = flask_app.config['MAIL_PORT']
        print(f"✅ MAIL_PORT: {flask_app.config['MAIL_PORT']}")
    else:
        print("❌ MAIL_PORT: Not configured")
    
    if flask_app.config.get('MAIL_USERNAME'):
        config_status['MAIL_USERNAME'] = True
        config_status['details']['MAIL_USERNAME'] = flask_app.config['MAIL_USERNAME']
        print(f"✅ MAIL_USERNAME: {flask_app.config['MAIL_USERNAME']}")
    else:
        print("❌ MAIL_USERNAME: Not configured")
    
    if flask_app.config.get('MAIL_PASSWORD'):
        config_status['MAIL_PASSWORD'] = True
        config_status['details']['MAIL_PASSWORD'] = '***(configured)***'
        print(f"✅ MAIL_PASSWORD: ***(configured)***")
    else:
        print("❌ MAIL_PASSWORD: Not configured")
    
    if flask_app.config.get('MAIL_USE_TLS'):
        config_status['MAIL_USE_TLS'] = True
        config_status['details']['MAIL_USE_TLS'] = flask_app.config['MAIL_USE_TLS']
        print(f"✅ MAIL_USE_TLS: {flask_app.config['MAIL_USE_TLS']}")
    else:
        print("⚠️  MAIL_USE_TLS: Not set (optional)")
    
    if flask_app.config.get('MAIL_USE_SSL'):
        config_status['MAIL_USE_SSL'] = True
        config_status['details']['MAIL_USE_SSL'] = flask_app.config['MAIL_USE_SSL']
        print(f"✅ MAIL_USE_SSL: {flask_app.config['MAIL_USE_SSL']}")
    else:
        print("⚠️  MAIL_USE_SSL: Not set (optional)")
    
    # Overall configuration status
    required_configured = all([
        config_status['MAIL_SERVER'],
        config_status['MAIL_PORT'],
        config_status['MAIL_USERNAME'],
        config_status['MAIL_PASSWORD']
    ])
    
    config_status['is_configured'] = required_configured
    
    print("=" * 60)
    if required_configured:
        print("✅ Flask-Mail is properly configured")
    else:
        print("❌ Flask-Mail is NOT properly configured")
    print("=" * 60 + "\n")
    
    return config_status
