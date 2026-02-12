"""
Users Routes Blueprint
Flask Blueprint for user-related endpoints

This module provides API endpoints for fetching all users
and user-related operations.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from app.models.user import User


# Create Blueprint for users routes
users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_users():
    """
    Get all users in the database.
    
    Returns:
        JSON list of all users excluding passwords
        Each user includes: id, name, email, role, etc.
        
    Example Response:
        [
            {
                "id": 1,
                "full_name": "John Doe",
                "email": "john@email.com",
                "role": "customer"
            },
            {
                "id": 2,
                "full_name": "Jane Smith",
                "email": "jane@email.com",
                "role": "courier"
            }
        ]
    """
    try:
        # Fetch all users from database
        users = User.query.all()
        
        # Serialize users (password_hash is already excluded via serialize_rules)
        users_data = [user.to_dict() for user in users]
        
        return jsonify({
            'success': True,
            'total_users': len(users_data),
            'users': users_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch users: {str(e)}'
        }), 500


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_by_id(user_id):
    """
    Get a specific user by ID.
    
    Args:
        user_id (int): The user's ID
        
    Returns:
        JSON response with user details or error message
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch user: {str(e)}'
        }), 500
