from flask import Blueprint, request, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select, desc, func
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import RequestEntityTooLarge
import os
import logging
import traceback

from app import db
from models.file import File
from models.user import User
from utils.responses import success_response, error_response
from utils.file_utils import (
    validate_file_type,
    validate_file_size,
    generate_file_hash,
    generate_stored_filename,
    get_file_storage_path,
    save_file,
    delete_file_from_disk,
    get_file_mime_type,
    sanitize_filename
)

files_bp = Blueprint('files', __name__)
logger = logging.getLogger(__name__)

def get_db():
    """Get db instance from current app"""
    return current_app.extensions['sqlalchemy']

@files_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload a file"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.info(f"File upload request: {user_id}")
        
        # Verify user exists
        user = db_instance.session.get(User, user_id)
        if not user:
            logger.warning(f"File upload failed: User not found - {user_id}")
            return error_response('User not found', 'USER_NOT_FOUND', 404)
        
        # Check if file is in request
        if 'file' not in request.files:
            logger.warning(f"File upload failed: No file provided - {user_id}")
            return error_response('No file provided', 'NO_FILE', 400)
        
        file = request.files['file']
        
        # Check if file was actually selected
        if file.filename == '':
            logger.warning(f"File upload failed: No file selected - {user_id}")
            return error_response('No file selected', 'NO_FILE_SELECTED', 400)
        
        logger.debug(f"File upload attempt: {file.filename} ({user_id})")
        
        # Get optional description
        description = request.form.get('description', '').strip() or None
        
        # Validate file type
        is_valid, error_msg, file_type = validate_file_type(file.filename)
        if not is_valid:
            logger.warning(f"File upload failed: Invalid file type - {file.filename} ({user_id})")
            return error_response(error_msg, 'INVALID_FILE_TYPE', 400)
        
        # Read file content
        file_content = file.read()
        file_size = len(file_content)
        
        logger.debug(f"File size: {file_size} bytes ({user_id})")
        
        # Validate file size
        is_valid, error_msg = validate_file_size(file_size)
        if not is_valid:
            logger.warning(f"File upload failed: File too large - {file_size} bytes ({user_id})")
            return error_response(error_msg, 'FILE_TOO_LARGE', 400)
        
        # Generate file hash
        file_hash = generate_file_hash(file_content)
        logger.debug(f"File hash generated: {file_hash[:16]}... ({user_id})")
        
        # Check for duplicate files (same hash and user)
        existing_file = db_instance.session.scalar(
            select(File).filter_by(user_id=user_id, file_hash=file_hash)
        )
        if existing_file:
            logger.warning(f"File upload failed: Duplicate file - {file.filename} ({user_id})")
            return error_response(
                'File with same content already exists',
                'DUPLICATE_FILE',
                409
            )
        
        # Generate stored filename
        stored_filename = generate_stored_filename(file.filename, user_id)
        
        # Get storage path
        storage_path, relative_path = get_file_storage_path(user_id)
        
        # Save file to disk
        success, error_msg, full_file_path = save_file(
            file_content,
            storage_path,
            stored_filename
        )
        
        if not success:
            logger.error(f"File upload failed: Save error - {error_msg} ({user_id})")
            return error_response(
                f'Failed to save file: {error_msg}',
                'SAVE_ERROR',
                500
            )
        
        # Get MIME type
        mime_type = get_file_mime_type(file.filename)
        
        # Create file record in database
        file_record = File(
            user_id=user_id,
            original_filename=sanitize_filename(file.filename),
            stored_filename=stored_filename,
            file_path=storage_path,
            file_type=file_type,
            mime_type=mime_type,
            file_size=file_size,
            file_hash=file_hash,
            description=description
        )
        
        db_instance.session.add(file_record)
        db_instance.session.commit()
        
        logger.info(f"File uploaded successfully: {file_record.id} ({file.filename}, {user_id})")
        return success_response(
            data={'file': file_record.to_dict()},
            message='File uploaded successfully',
            status_code=201
        )
        
    except RequestEntityTooLarge:
        logger.warning(f"File upload failed: File too large ({user_id})")
        return error_response(
            'File size exceeds maximum allowed size',
            'FILE_TOO_LARGE',
            413
        )
    except IntegrityError as e:
        db_instance.session.rollback()
        logger.error(f"File upload failed: Database integrity error - {str(e)} ({user_id})")
        return error_response(
            'File record creation failed',
            'DATABASE_ERROR',
            500
        )
    except Exception as e:
        db_instance.session.rollback()
        logger.error(
            f"File upload error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"User: {user_id}"
        )
        return error_response(
            f'An error occurred during upload: {str(e)}',
            'UPLOAD_ERROR',
            500
        )

@files_bp.route('', methods=['GET'])
@jwt_required()
def list_files():
    """List user's files"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        # Get query parameters
        file_type = request.args.get('file_type', '').strip().lower()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
        
        logger.debug(f"List files request: page={page}, per_page={per_page}, file_type={file_type} ({user_id})")
        
        # Build base query for filtering
        base_query = select(File).filter_by(user_id=user_id)
        
        # Filter by file type if provided
        if file_type:
            base_query = base_query.filter_by(file_type=file_type)
        
        # Get total count (before pagination)
        count_query = select(func.count(File.id)).filter_by(user_id=user_id)
        if file_type:
            count_query = count_query.filter_by(file_type=file_type)
        total_count = db_instance.session.scalar(count_query) or 0
        
        # Build query for data (with sorting and pagination)
        query = base_query.order_by(desc(File.created_at))
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        # Execute query
        files = db_instance.session.scalars(query).all()
        
        # Convert to dict
        files_data = [file.to_dict() for file in files]
        
        logger.debug(f"List files successful: {len(files_data)} files returned ({user_id})")
        return success_response(
            data={
                'files': files_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_count,
                    'pages': (total_count + per_page - 1) // per_page
                }
            }
        )
        
    except Exception as e:
        logger.error(
            f"List files error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"User: {user_id}"
        )
        return error_response(
            'An error occurred while listing files',
            'LIST_ERROR',
            500
        )

@files_bp.route('/<file_id>', methods=['GET'])
@jwt_required()
def get_file(file_id):
    """Get file metadata"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.debug(f"Get file request: {file_id} ({user_id})")
        
        # Get file
        file_record = db_instance.session.get(File, file_id)
        
        if not file_record:
            logger.warning(f"Get file failed: File not found - {file_id} ({user_id})")
            return error_response('File not found', 'FILE_NOT_FOUND', 404)
        
        # Verify ownership
        if file_record.user_id != user_id:
            logger.warning(f"Get file failed: Access denied - {file_id} ({user_id})")
            return error_response(
                'You do not have permission to access this file',
                'FORBIDDEN',
                403
            )
        
        logger.debug(f"Get file successful: {file_id} ({user_id})")
        return success_response(data={'file': file_record.to_dict()})
        
    except Exception as e:
        logger.error(
            f"Get file error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"File: {file_id}, User: {user_id}"
        )
        return error_response(
            'An error occurred',
            'SERVER_ERROR',
            500
        )

@files_bp.route('/<file_id>/download', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """Download a file"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.info(f"File download request: {file_id} ({user_id})")
        
        # Get file
        file_record = db_instance.session.get(File, file_id)
        
        if not file_record:
            logger.warning(f"File download failed: File not found - {file_id} ({user_id})")
            return error_response('File not found', 'FILE_NOT_FOUND', 404)
        
        # Verify ownership
        if file_record.user_id != user_id:
            logger.warning(f"File download failed: Access denied - {file_id} ({user_id})")
            return error_response(
                'You do not have permission to download this file',
                'FORBIDDEN',
                403
            )
        
        # Get full file path
        full_path = file_record.get_full_path()
        
        # Check if file exists on disk
        if not file_record.exists_on_disk():
            logger.error(f"File download failed: File missing on disk - {file_id} ({user_id})")
            return error_response(
                'File not found on disk',
                'FILE_MISSING',
                404
            )
        
        logger.info(f"File download successful: {file_id} ({file_record.original_filename}, {user_id})")
        # Send file
        return send_file(
            full_path,
            mimetype=file_record.mime_type,
            as_attachment=True,
            download_name=file_record.original_filename
        )
        
    except Exception as e:
        logger.error(
            f"File download error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"File: {file_id}, User: {user_id}"
        )
        return error_response(
            'An error occurred during download',
            'DOWNLOAD_ERROR',
            500
        )

@files_bp.route('/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """Delete a file"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.info(f"File delete request: {file_id} ({user_id})")
        
        # Get file
        file_record = db_instance.session.get(File, file_id)
        
        if not file_record:
            logger.warning(f"File delete failed: File not found - {file_id} ({user_id})")
            return error_response('File not found', 'FILE_NOT_FOUND', 404)
        
        # Verify ownership
        if file_record.user_id != user_id:
            logger.warning(f"File delete failed: Access denied - {file_id} ({user_id})")
            return error_response(
                'You do not have permission to delete this file',
                'FORBIDDEN',
                403
            )
        
        # Get full file path
        full_path = file_record.get_full_path()
        
        # Delete from database first
        db_instance.session.delete(file_record)
        db_instance.session.commit()
        
        # Delete from filesystem
        if os.path.exists(full_path):
            success, error_msg = delete_file_from_disk(full_path)
            if not success:
                # Log error but don't fail the request since DB record is deleted
                logger.warning(f"File delete warning: Failed to delete file from disk - {error_msg} ({file_id}, {user_id})")
        
        logger.info(f"File deleted successfully: {file_id} ({file_record.original_filename}, {user_id})")
        return success_response(message='File deleted successfully')
        
    except Exception as e:
        db_instance.session.rollback()
        logger.error(
            f"File delete error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"File: {file_id}, User: {user_id}"
        )
        return error_response(
            'An error occurred during deletion',
            'DELETE_ERROR',
            500
        )

