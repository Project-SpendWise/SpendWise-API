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
        
        # Support both 'name' field (frontend) and 'first_name'/'last_name' (backend)
        name = sanitize_string(data.get('name'), max_length=200)
        first_name = sanitize_string(data.get('first_name'), max_length=100)
        last_name = sanitize_string(data.get('last_name'), max_length=100)
        
        # If 'name' is provided but not first_name/last_name, split it
        if name and not first_name and not last_name:
            name_parts = name.split(' ', 1)
            first_name = name_parts[0] if len(name_parts) > 0 else None
            last_name = name_parts[1] if len(name_parts) > 1 else None
        elif not first_name and not last_name and name:
            # If only name provided, use it as first_name
            first_name = name
        
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
        
        # Create tokens for registration (frontend expects tokens on register)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        logger.info(f"User registered successfully: {user.id} ({user.email})")
        return success_response(
            data={
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
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
        
        # Support both 'name' field (frontend) and 'first_name'/'last_name' (backend)
        if 'name' in data:
            name = sanitize_string(data.get('name'), max_length=200)
            if name:
                name_parts = name.split(' ', 1)
                user.first_name = name_parts[0] if len(name_parts) > 0 else None
                user.last_name = name_parts[1] if len(name_parts) > 1 else None
        
        # Update first_name if provided
        if 'first_name' in data:
            user.first_name = sanitize_string(data.get('first_name'), max_length=100)
        
        # Update last_name if provided
        if 'last_name' in data:
            user.last_name = sanitize_string(data.get('last_name'), max_length=100)
        
        # Update email if provided
        if 'email' in data:
            email = data.get('email')
            is_valid, error_msg = validate_email(email)
            if not is_valid:
                logger.warning(f"Update user failed: Invalid email - {error_msg}")
                return error_response(error_msg, 'INVALID_EMAIL', 400)
            
            # Check if email is already taken by another user
            existing_user = db_instance.session.scalar(select(User).filter_by(email=email.lower().strip()))
            if existing_user and existing_user.id != user.id:
                logger.warning(f"Update user failed: Email already taken - {email}")
                return error_response('Email already taken', 'EMAIL_EXISTS', 409)
            
            user.email = email.lower().strip()
        
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
        
        # Support both snake_case (backend) and camelCase (frontend)
        current_password = data.get('currentPassword') or data.get('current_password')
        new_password = data.get('newPassword') or data.get('new_password')
        
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
def refresh():
    """
    Refresh access token.
    Supports both Authorization header (Bearer token) and request body (refresh_token field).
    Frontend spec requires refresh_token in request body.
    """
    try:
        db_instance = get_db()
        
        # Try to get token from request body first (frontend spec)
        data = request.get_json() or {}
        refresh_token_from_body = data.get('refresh_token')
        
        # If not in body, try Authorization header (backward compatibility)
        auth_header = request.headers.get('Authorization', '')
        refresh_token_from_header = None
        if auth_header.startswith('Bearer '):
            refresh_token_from_header = auth_header[7:]
        
        # Use token from body if available, otherwise from header
        refresh_token_value = refresh_token_from_body or refresh_token_from_header
        
        if not refresh_token_value:
            logger.warning("Token refresh failed: No refresh token provided")
            return error_response('Refresh token is required', 'MISSING_TOKEN', 401)
        
        # Verify token and get user_id
        from flask_jwt_extended import decode_token
        try:
            decoded = decode_token(refresh_token_value)
            user_id = decoded.get('sub')
            
            if not user_id:
                logger.warning("Token refresh failed: Invalid token format")
                return error_response('Invalid refresh token', 'INVALID_TOKEN', 401)
        except Exception as e:
            logger.warning(f"Token refresh failed: Token decode error - {str(e)}")
            return error_response('Invalid or expired refresh token', 'INVALID_TOKEN', 401)
        
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

