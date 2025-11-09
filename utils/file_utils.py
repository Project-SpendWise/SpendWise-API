import os
import hashlib
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.pdf', '.xlsx', '.xls', '.csv', '.docx'}

# MIME type mapping
MIME_TYPES = {
    '.pdf': 'application/pdf',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xls': 'application/vnd.ms-excel',
    '.csv': 'text/csv',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

def validate_file_type(filename):
    """
    Validate if file extension is allowed
    Returns: (is_valid, error_message, file_type)
    """
    if not filename:
        return False, 'Filename is required', None
    
    # Get file extension
    ext = os.path.splitext(filename)[1].lower()
    
    if not ext:
        return False, 'File must have an extension', None
    
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ', '.join(ALLOWED_EXTENSIONS)
        return False, f'File type not allowed. Allowed types: {allowed}', None
    
    # Return file type without the dot
    file_type = ext[1:] if ext.startswith('.') else ext
    return True, None, file_type

def validate_file_size(file_size, max_size=None):
    """
    Validate file size
    max_size in bytes, defaults to config MAX_CONTENT_LENGTH
    Returns: (is_valid, error_message)
    """
    if max_size is None:
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024)
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return False, f'File size exceeds maximum allowed size of {max_size_mb:.1f}MB'
    
    if file_size == 0:
        return False, 'File is empty'
    
    return True, None

def generate_file_hash(file_content):
    """
    Generate SHA-256 hash of file content
    """
    return hashlib.sha256(file_content).hexdigest()

def generate_stored_filename(original_filename, user_id=None):
    """
    Generate a unique stored filename
    Format: {uuid}_{sanitized_original_filename}
    """
    # Get extension
    ext = os.path.splitext(original_filename)[1].lower()
    
    # Generate unique ID
    unique_id = str(uuid.uuid4())[:8]
    
    # Sanitize original filename (remove extension for sanitization)
    base_name = os.path.splitext(original_filename)[0]
    sanitized_base = secure_filename(base_name)
    
    # Limit base name length to avoid very long filenames
    if len(sanitized_base) > 50:
        sanitized_base = sanitized_base[:50]
    
    # Combine: unique_id_sanitized_base.ext
    stored_filename = f"{unique_id}_{sanitized_base}{ext}"
    
    return stored_filename

def get_file_storage_path(user_id, base_upload_folder=None):
    """
    Generate file storage path: uploads/YYYY-MM-DD/user_id/
    Returns: (full_path, relative_path)
    """
    if base_upload_folder is None:
        base_upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    # Get current date
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    
    # Build path: uploads/YYYY-MM-DD/user_id/
    relative_path = os.path.join(base_upload_folder, date_str, user_id)
    full_path = os.path.join(os.getcwd(), relative_path)
    
    return full_path, relative_path

def ensure_directory_exists(directory_path):
    """
    Ensure directory exists, create if it doesn't
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)

def save_file(file_content, file_path, filename):
    """
    Save file to disk
    Returns: (success, error_message, full_path)
    """
    try:
        # Ensure directory exists
        ensure_directory_exists(file_path)
        
        # Full path to file
        full_path = os.path.join(file_path, filename)
        
        # Save file
        with open(full_path, 'wb') as f:
            f.write(file_content)
        
        return True, None, full_path
    except Exception as e:
        return False, str(e), None

def delete_file_from_disk(file_path):
    """
    Delete file from disk
    Returns: (success, error_message)
    """
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            return True, None
        else:
            return False, 'File does not exist'
    except Exception as e:
        return False, str(e)

def get_file_mime_type(filename):
    """
    Get MIME type from filename extension
    """
    ext = os.path.splitext(filename)[1].lower()
    return MIME_TYPES.get(ext, 'application/octet-stream')

def sanitize_filename(filename):
    """
    Sanitize filename to prevent path traversal
    """
    return secure_filename(filename)

def get_file_extension(filename):
    """
    Get file extension (without dot)
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext[1:] if ext.startswith('.') else ext

