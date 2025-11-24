from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select, desc
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import RequestEntityTooLarge
import os
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from app import db
from models.statement import Statement
from models.transaction import Transaction
from models.user import User
from utils.responses import success_response, error_response
from utils.file_utils import (
    validate_file_type,
    validate_file_size,
    generate_stored_filename,
    get_file_storage_path,
    save_file,
    delete_file_from_disk,
    sanitize_filename,
    ensure_directory_exists
)
from analyzers.fake_analyzer import FakeStatementAnalyzer

statements_bp = Blueprint('statements', __name__)
logger = logging.getLogger(__name__)

# Thread pool for async processing
executor = ThreadPoolExecutor(max_workers=3)

def get_db():
    """Get db instance from current app"""
    return current_app.extensions['sqlalchemy']


def process_statement_async(app_instance, statement_id: str, file_path: str, user_id: str):
    """
    Process statement asynchronously using fake analyzer.
    This function runs in a background thread.
    """
    logger.info(f"Async processing function called for statement: {statement_id}")
    try:
        with app_instance.app_context():
            logger.info(f"App context acquired for statement: {statement_id}")
            db_instance = None
            try:
                # Get db instance from app context
                db_instance = get_db()
                logger.info(f"DB instance obtained for statement: {statement_id}")
                
                statement = db_instance.session.get(Statement, statement_id)
                
                if not statement:
                    logger.error(f"Statement not found for processing: {statement_id}")
                    return
                
                logger.info(f"Statement found, current status: {statement.status}")
                
                # Status is already 'processing' from upload, so we can skip updating it
                logger.info(f"Starting fake analysis for statement: {statement_id}")
                
                # Run fake analyzer
                analyzer = FakeStatementAnalyzer()
                result = analyzer.analyze(file_path, user_id, statement_id)
                
                logger.info(f"Fake analyzer generated {len(result.transactions)} transactions for statement: {statement_id}")
                
                # Store transactions
                for txn in result.transactions:
                    db_instance.session.add(txn)
                
                # Update statement
                statement.statement_period_start = result.statement_period_start
                statement.statement_period_end = result.statement_period_end
                statement.transaction_count = len(result.transactions)
                statement.update_status('processed')
                
                db_instance.session.commit()
                
                logger.info(f"Statement processed successfully: {statement_id} ({len(result.transactions)} transactions)")
                
            except Exception as e:
                logger.error(
                    f"Error processing statement {statement_id}: {str(e)}\n"
                    f"Traceback: {traceback.format_exc()}"
                )
                try:
                    if db_instance is None:
                        db_instance = get_db()
                    statement = db_instance.session.get(Statement, statement_id)
                    if statement:
                        statement.update_status('failed', error_message=str(e))
                        db_instance.session.commit()
                except Exception as commit_error:
                    logger.error(f"Failed to update statement status: {str(commit_error)}")
                    if db_instance:
                        db_instance.session.rollback()
    except Exception as outer_error:
        logger.error(f"Outer error in async processing: {str(outer_error)}\nTraceback: {traceback.format_exc()}")


@statements_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_statement():
    """Upload a bank statement file"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.info(f"Statement upload request: {user_id}")
        
        # Verify user exists
        user = db_instance.session.get(User, user_id)
        if not user:
            logger.warning(f"Statement upload failed: User not found - {user_id}")
            return error_response('User not found', 'USER_NOT_FOUND', 404)
        
        # Check if file is in request
        if 'file' not in request.files:
            logger.warning(f"Statement upload failed: No file provided - {user_id}")
            return error_response('No file provided', 'NO_FILE', 400)
        
        file = request.files['file']
        
        # Check if file was actually selected
        if file.filename == '':
            logger.warning(f"Statement upload failed: No file selected - {user_id}")
            return error_response('No file selected', 'NO_FILE_SELECTED', 400)
        
        logger.debug(f"Statement upload attempt: {file.filename} ({user_id})")
        
        # Validate file type
        is_valid, error_msg, file_type = validate_file_type(file.filename)
        if not is_valid:
            logger.warning(f"Statement upload failed: Invalid file type - {file.filename} ({user_id})")
            return error_response(error_msg, 'INVALID_FILE_TYPE', 400)
        
        # Read file content
        file_content = file.read()
        file_size = len(file_content)
        
        logger.debug(f"File size: {file_size} bytes ({user_id})")
        
        # Validate file size
        is_valid, error_msg = validate_file_size(file_size)
        if not is_valid:
            logger.warning(f"Statement upload failed: File too large - {file_size} bytes ({user_id})")
            return error_response(error_msg, 'FILE_TOO_LARGE', 400)
        
        # Generate stored filename
        stored_filename = generate_stored_filename(file.filename, user_id)
        
        # Get storage path
        storage_path, relative_path = get_file_storage_path(user_id)
        ensure_directory_exists(storage_path)
        
        # Save file to disk
        success, error_msg, full_file_path = save_file(
            file_content,
            storage_path,
            stored_filename
        )
        
        if not success:
            logger.error(f"Statement upload failed: Save error - {error_msg} ({user_id})")
            return error_response(
                f'Failed to save file: {error_msg}',
                'SAVE_ERROR',
                500
            )
        
        # Get profile metadata from form data (all optional)
        profile_name = request.form.get('profileName', '').strip()
        profile_description = request.form.get('profileDescription', '').strip() or None
        account_type = request.form.get('accountType', '').strip() or None
        bank_name = request.form.get('bankName', '').strip() or None
        color = request.form.get('color', '').strip() or None
        icon = request.form.get('icon', '').strip() or None
        
        # Auto-generate profile name from filename if not provided
        if not profile_name:
            # Remove extension and use filename as profile name
            base_name = os.path.splitext(sanitize_filename(file.filename))[0]
            profile_name = base_name or 'Untitled Profile'
        
        # Check if this is user's first profile (no other statements exist)
        existing_statements = db_instance.session.query(Statement).filter_by(user_id=user_id).count()
        is_default = existing_statements == 0
        
        # Create statement record with profile metadata
        statement = Statement(
            user_id=user_id,
            file_name=sanitize_filename(file.filename),
            file_path=full_file_path,
            status='processing',
            profile_name=profile_name,
            profile_description=profile_description,
            account_type=account_type,
            bank_name=bank_name,
            color=color,
            icon=icon,
            is_default=is_default
        )
        
        db_instance.session.add(statement)
        db_instance.session.commit()
        
        # Queue async processing - pass app instance
        app_obj = current_app._get_current_object()
        logger.info(f"Queueing async processing for statement: {statement.id}")
        future = executor.submit(process_statement_async, app_obj, statement.id, full_file_path, user_id)
        logger.info(f"Async processing queued for statement: {statement.id}, future: {future}")
        
        logger.info(f"Statement uploaded successfully: {statement.id} ({file.filename}, {user_id})")
        return success_response(
            data=statement.to_dict(),
            message='Statement uploaded successfully',
            status_code=200
        )
        
    except RequestEntityTooLarge:
        logger.warning(f"Statement upload failed: File too large ({user_id})")
        return error_response(
            'File size exceeds maximum allowed size',
            'FILE_TOO_LARGE',
            413
        )
    except IntegrityError as e:
        db_instance.session.rollback()
        logger.error(f"Statement upload failed: Database integrity error - {str(e)} ({user_id})")
        return error_response(
            'Statement record creation failed',
            'DATABASE_ERROR',
            500
        )
    except Exception as e:
        db_instance.session.rollback()
        logger.error(
            f"Statement upload error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"User: {user_id}"
        )
        return error_response(
            f'An error occurred during upload: {str(e)}',
            'UPLOAD_ERROR',
            500
        )


@statements_bp.route('', methods=['GET'])
@jwt_required()
def list_statements():
    """Get all statements uploaded by the authenticated user"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        logger.debug(f"List statements request: {user_id}")
        
        # Get all statements for user, ordered by is_default DESC, then upload_date DESC
        query = select(Statement).filter_by(user_id=user_id).order_by(
            desc(Statement.is_default),
            desc(Statement.upload_date)
        )
        statements = db_instance.session.scalars(query).all()
        
        # Convert to dict
        statements_data = [stmt.to_dict() for stmt in statements]
        
        logger.debug(f"List statements successful: {len(statements_data)} statements returned ({user_id})")
        return success_response(
            data={'statements': statements_data}
        )
        
    except Exception as e:
        logger.error(
            f"List statements error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"User: {user_id}"
        )
        return error_response(
            'An error occurred while listing statements',
            'LIST_ERROR',
            500
        )


@statements_bp.route('/<statement_id>', methods=['GET'])
@jwt_required()
def get_statement(statement_id):
    """Get details of a specific statement"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.debug(f"Get statement request: {statement_id} ({user_id})")
        
        # Get statement
        statement = db_instance.session.get(Statement, statement_id)
        
        if not statement:
            logger.warning(f"Get statement failed: Statement not found - {statement_id} ({user_id})")
            return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404), 404
        
        # Verify ownership
        if statement.user_id != user_id:
            logger.warning(f"Get statement failed: Access denied - {statement_id} ({user_id})")
            return error_response(
                'You do not have permission to access this statement',
                'FORBIDDEN',
                403
            )
        
        logger.debug(f"Get statement successful: {statement_id} ({user_id})")
        return success_response(data=statement.to_dict())
        
    except Exception as e:
        logger.error(
            f"Get statement error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"Statement: {statement_id}, User: {user_id}"
        )
        return error_response(
            'An error occurred',
            'SERVER_ERROR',
            500
        )


@statements_bp.route('/<statement_id>/delete', methods=['POST'])
@jwt_required()
def delete_statement(statement_id):
    """Delete a statement and all its associated transactions"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.info(f"Statement delete request: {statement_id} ({user_id})")
        
        # Get statement
        statement = db_instance.session.get(Statement, statement_id)
        
        if not statement:
            logger.warning(f"Statement delete failed: Statement not found - {statement_id} ({user_id})")
            return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404)
        
        # Verify ownership
        if statement.user_id != user_id:
            logger.warning(f"Statement delete failed: Access denied - {statement_id} ({user_id})")
            return error_response(
                'You do not have permission to delete this statement',
                'FORBIDDEN',
                403
            )
        
        # Get file path before deletion
        file_path = statement.file_path
        
        # Delete from database (cascade will delete transactions)
        db_instance.session.delete(statement)
        db_instance.session.commit()
        
        # Delete file from filesystem
        if os.path.exists(file_path) and os.path.isfile(file_path):
            success, error_msg = delete_file_from_disk(file_path)
            if not success:
                # Log error but don't fail the request since DB record is deleted
                logger.warning(f"Statement delete warning: Failed to delete file from disk - {error_msg} ({statement_id}, {user_id})")
        
        logger.info(f"Statement deleted successfully: {statement_id} ({statement.file_name}, {user_id})")
        return success_response(
            data={'success': True, 'message': 'Statement deleted successfully'}
        )
        
    except Exception as e:
        db_instance.session.rollback()
        logger.error(
            f"Statement delete error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"Statement: {statement_id}, User: {user_id}"
        )
        return error_response(
            'An error occurred during deletion',
            'DELETE_ERROR',
            500
        )


@statements_bp.route('/profiles', methods=['GET'])
@jwt_required()
def list_profiles():
    """Get all profiles (statements) for the authenticated user - simplified list for profile selection"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.debug(f"List profiles request: {user_id}")
        
        # Get all statements for user, ordered by is_default DESC, then upload_date DESC
        query = select(Statement).filter_by(user_id=user_id).order_by(
            desc(Statement.is_default),
            desc(Statement.upload_date)
        )
        statements = db_instance.session.scalars(query).all()
        
        # Convert to simplified profile list
        profiles_data = []
        for stmt in statements:
            profiles_data.append({
                'id': stmt.id,
                'profileName': stmt.profile_name,
                'accountType': stmt.account_type,
                'bankName': stmt.bank_name,
                'color': stmt.color,
                'icon': stmt.icon,
                'isDefault': stmt.is_default,
                'transactionCount': stmt.transaction_count,
                'status': stmt.status
            })
        
        logger.debug(f"List profiles successful: {len(profiles_data)} profiles returned ({user_id})")
        return success_response(
            data={'profiles': profiles_data}
        )
        
    except Exception as e:
        logger.error(
            f"List profiles error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"User: {user_id}"
        )
        return error_response(
            'An error occurred while listing profiles',
            'LIST_ERROR',
            500
        )


@statements_bp.route('/<statement_id>/profile', methods=['PUT'])
@jwt_required()
def update_profile(statement_id):
    """Update profile metadata for a statement"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.info(f"Update profile request: {statement_id} ({user_id})")
        
        # Get statement
        statement = db_instance.session.get(Statement, statement_id)
        
        if not statement:
            logger.warning(f"Update profile failed: Statement not found - {statement_id} ({user_id})")
            return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404), 404
        
        # Verify ownership
        if statement.user_id != user_id:
            logger.warning(f"Update profile failed: Access denied - {statement_id} ({user_id})")
            return error_response(
                'You do not have permission to update this profile',
                'FORBIDDEN',
                403
            ), 403
        
        # Get JSON data
        data = request.get_json()
        if not data:
            return error_response('No data provided', 'NO_DATA', 400), 400
        
        # Update profile fields (all optional)
        if 'profileName' in data:
            statement.profile_name = data['profileName'].strip() if data['profileName'] else None
        
        if 'profileDescription' in data:
            statement.profile_description = data['profileDescription'].strip() if data['profileDescription'] else None
        
        if 'accountType' in data:
            statement.account_type = data['accountType'].strip() if data['accountType'] else None
        
        if 'bankName' in data:
            statement.bank_name = data['bankName'].strip() if data['bankName'] else None
        
        if 'color' in data:
            statement.color = data['color'].strip() if data['color'] else None
        
        if 'icon' in data:
            statement.icon = data['icon'].strip() if data['icon'] else None
        
        db_instance.session.commit()
        
        logger.info(f"Profile updated successfully: {statement_id} ({user_id})")
        return success_response(
            data=statement.to_dict(),
            message='Profile updated successfully'
        )
        
    except Exception as e:
        db_instance.session.rollback()
        logger.error(
            f"Update profile error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"Statement: {statement_id}, User: {user_id}"
        )
        return error_response(
            'An error occurred while updating profile',
            'UPDATE_ERROR',
            500
        )


@statements_bp.route('/<statement_id>/set-default', methods=['POST'])
@jwt_required()
def set_default_profile(statement_id):
    """Set a profile as the default profile for the user"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.info(f"Set default profile request: {statement_id} ({user_id})")
        
        # Get statement
        statement = db_instance.session.get(Statement, statement_id)
        
        if not statement:
            logger.warning(f"Set default profile failed: Statement not found - {statement_id} ({user_id})")
            return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404), 404
        
        # Verify ownership
        if statement.user_id != user_id:
            logger.warning(f"Set default profile failed: Access denied - {statement_id} ({user_id})")
            return error_response(
                'You do not have permission to set this profile as default',
                'FORBIDDEN',
                403
            ), 403
        
        # Set all user's profiles to is_default=False
        query = select(Statement).filter_by(user_id=user_id)
        all_statements = db_instance.session.scalars(query).all()
        for stmt in all_statements:
            stmt.is_default = False
        
        # Set this profile as default
        statement.is_default = True
        
        db_instance.session.commit()
        
        logger.info(f"Default profile set successfully: {statement_id} ({user_id})")
        return success_response(
            data=statement.to_dict(),
            message='Default profile set successfully'
        )
        
    except Exception as e:
        db_instance.session.rollback()
        logger.error(
            f"Set default profile error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"Statement: {statement_id}, User: {user_id}"
        )
        return error_response(
            'An error occurred while setting default profile',
            'SET_DEFAULT_ERROR',
            500
        )
