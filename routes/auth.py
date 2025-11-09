from flask import Blueprint, request, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import logging
import traceback
from app import db
from models.user import User
from utils.responses import success_response, error_response
from utils.validators import validate_email, validate_password, validate_username, sanitize_string

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

def get_db():
    """Get db instance from current app"""
    return current_app.extensions['sqlalchemy']

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        db_instance = get_db()
        
        data = request.get_json()
        logger.info("Registration attempt")
        
        if not data:
            logger.warning("Registration failed: No request body")
            return error_response('Request body is required', 'INVALID_REQUEST', 400)
        
        # Extract and validate email
        email = data.get('email')
        is_valid, error_msg = validate_email(email)
        if not is_valid:
            logger.warning(f"Registration failed: Invalid email - {error_msg}")
            return error_response(error_msg, 'INVALID_EMAIL', 400)
        
        # Extract and validate password
        password = data.get('password')
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            logger.warning(f"Registration failed: Invalid password - {error_msg}")
            return error_response(error_msg, 'INVALID_PASSWORD', 400)
        
        # Extract and validate optional fields
        username = sanitize_string(data.get('username'))
        if username:
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                logger.warning(f"Registration failed: Invalid username - {error_msg}")
                return error_response(error_msg, 'INVALID_USERNAME', 400)
        
        first_name = sanitize_string(data.get('first_name'), max_length=100)
        last_name = sanitize_string(data.get('last_name'), max_length=100)
        
        # Check if user already exists  
        existing_user = db_instance.session.scalar(select(User).filter_by(email=email.lower().strip()))
        if existing_user:
            logger.warning(f"Registration failed: Email already exists - {email}")
            return error_response('User with this email already exists', 'EMAIL_EXISTS', 409)
        
        if username:
            existing_username = db_instance.session.scalar(select(User).filter_by(username=username))
            if existing_username:
                logger.warning(f"Registration failed: Username already taken - {username}")
                return error_response('Username already taken', 'USERNAME_EXISTS', 409)
        
        # Create new user
        user = User(
            email=email,
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        db_instance.session.add(user)
        db_instance.session.commit()
        
        logger.info(f"User registered successfully: {user.id} ({user.email})")
        return success_response(
            data={
                'user': user.to_dict()
            },
            message='User registered successfully',
            status_code=201
        )
        
    except IntegrityError as e:
        db_instance.session.rollback()
        logger.error(f"Registration failed: Database integrity error - {str(e)}")
        return error_response('User with this email or username already exists', 'DUPLICATE_USER', 409)
    except Exception as e:
        db_instance.session.rollback()
        logger.error(
            f"Registration error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        return error_response(f'An error occurred during registration: {str(e)}', 'REGISTRATION_ERROR', 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        db_instance = get_db()
        
        data = request.get_json()
        logger.info("Login attempt")
        
        if not data:
            logger.warning("Login failed: No request body")
            return error_response('Request body is required', 'INVALID_REQUEST', 400)
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            logger.warning("Login failed: Missing credentials")
            return error_response('Email and password are required', 'MISSING_CREDENTIALS', 400)
        
        # Find user by email
        user = db_instance.session.scalar(select(User).filter_by(email=email.lower().strip()))
        
        if not user or not user.check_password(password):
            logger.warning(f"Login failed: Invalid credentials for email - {email}")
            return error_response('Invalid email or password', 'INVALID_CREDENTIALS', 401)
        
        if not user.is_active:
            logger.warning(f"Login failed: Account deactivated - {user.id}")
            return error_response('Account is deactivated', 'ACCOUNT_DEACTIVATED', 403)
        
        # Update last login
        user.update_last_login()
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        logger.info(f"Login successful: {user.id} ({user.email})")
        return success_response(
            data={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            },
            message='Login successful'
        )
        
    except Exception as e:
        logger.error(
            f"Login error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        return error_response(f'An error occurred during login: {str(e)}', 'LOGIN_ERROR', 500)

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.debug(f"Get current user request: {user_id}")
        
        user = db_instance.session.get(User, user_id)
        
        if not user:
            logger.warning(f"Get current user failed: User not found - {user_id}")
            return error_response('User not found', 'USER_NOT_FOUND', 404)
        
        logger.debug(f"Get current user successful: {user_id}")
        return success_response(data={'user': user.to_dict()})
        
    except Exception as e:
        logger.error(
            f"Get current user error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        return error_response('An error occurred', 'SERVER_ERROR', 500)

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_user():
    """Update current user profile"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.info(f"Update user profile request: {user_id}")
        
        user = db_instance.session.get(User, user_id)
        
        if not user:
            logger.warning(f"Update user failed: User not found - {user_id}")
            return error_response('User not found', 'USER_NOT_FOUND', 404)
        
        data = request.get_json()
        if not data:
            logger.warning(f"Update user failed: No request body - {user_id}")
            return error_response('Request body is required', 'INVALID_REQUEST', 400)
        
        # Update username if provided
        if 'username' in data:
            username = sanitize_string(data.get('username'))
            if username:
                is_valid, error_msg = validate_username(username)
                if not is_valid:
                    logger.warning(f"Update user failed: Invalid username - {error_msg}")
                    return error_response(error_msg, 'INVALID_USERNAME', 400)
                
                # Check if username is already taken by another user
                existing_user = db_instance.session.scalar(select(User).filter_by(username=username))
                if existing_user and existing_user.id != user.id:
                    logger.warning(f"Update user failed: Username already taken - {username}")
                    return error_response('Username already taken', 'USERNAME_EXISTS', 409)
                
                user.username = username
        
        # Update first_name if provided
        if 'first_name' in data:
            user.first_name = sanitize_string(data.get('first_name'), max_length=100)
        
        # Update last_name if provided
        if 'last_name' in data:
            user.last_name = sanitize_string(data.get('last_name'), max_length=100)
        
        user.updated_at = datetime.utcnow()
        db_instance.session.commit()
        
        logger.info(f"User profile updated successfully: {user_id}")
        return success_response(
            data={'user': user.to_dict()},
            message='Profile updated successfully'
        )
        
    except IntegrityError as e:
        db_instance.session.rollback()
        logger.error(f"Update user failed: Database integrity error - {str(e)}")
        return error_response('Username already taken', 'USERNAME_EXISTS', 409)
    except Exception as e:
        db_instance.session.rollback()
        logger.error(
            f"Update user error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        return error_response('An error occurred during update', 'UPDATE_ERROR', 500)

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.info(f"Change password request: {user_id}")
        
        user = db_instance.session.get(User, user_id)
        
        if not user:
            logger.warning(f"Change password failed: User not found - {user_id}")
            return error_response('User not found', 'USER_NOT_FOUND', 404)
        
        data = request.get_json()
        if not data:
            logger.warning(f"Change password failed: No request body - {user_id}")
            return error_response('Request body is required', 'INVALID_REQUEST', 400)
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            logger.warning(f"Change password failed: Missing passwords - {user_id}")
            return error_response('Current password and new password are required', 'MISSING_PASSWORDS', 400)
        
        # Verify current password
        if not user.check_password(current_password):
            logger.warning(f"Change password failed: Incorrect current password - {user_id}")
            return error_response('Current password is incorrect', 'INVALID_PASSWORD', 401)
        
        # Validate new password
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            logger.warning(f"Change password failed: Invalid new password - {error_msg}")
            return error_response(error_msg, 'INVALID_PASSWORD', 400)
        
        # Check if new password is different from current
        if user.check_password(new_password):
            logger.warning(f"Change password failed: New password same as current - {user_id}")
            return error_response('New password must be different from current password', 'SAME_PASSWORD', 400)
        
        # Update password
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db_instance.session.commit()
        
        logger.info(f"Password changed successfully: {user_id}")
        return success_response(message='Password changed successfully')
        
    except Exception as e:
        db_instance.session.rollback()
        logger.error(
            f"Change password error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        return error_response('An error occurred during password change', 'PASSWORD_CHANGE_ERROR', 500)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.debug(f"Token refresh request: {user_id}")
        
        user = db_instance.session.scalar(select(User).filter_by(id=user_id))
        
        if not user or not user.is_active:
            logger.warning(f"Token refresh failed: User not found or inactive - {user_id}")
            return error_response('User not found or inactive', 'USER_NOT_FOUND', 404)
        
        # Create new access token and refresh token
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        logger.debug(f"Token refreshed successfully: {user_id}")
        return success_response(
            data={
                'access_token': access_token,
                'refresh_token': refresh_token
            },
            message='Token refreshed successfully'
        )
        
    except Exception as e:
        logger.error(
            f"Token refresh error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        return error_response('An error occurred during token refresh', 'REFRESH_ERROR', 500)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (token revocation can be added here)"""
    try:
        user_id = get_jwt_identity()
        logger.info(f"Logout request: {user_id}")
        
        # In a production system, you might want to blacklist the token here
        # For now, we'll just return success
        # Token blacklisting would require storing tokens in Redis or database
        
        logger.info(f"Logout successful: {user_id}")
        return success_response(message='Logged out successfully')
        
    except Exception as e:
        logger.error(
            f"Logout error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        return error_response('An error occurred during logout', 'LOGOUT_ERROR', 500)

