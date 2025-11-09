from app import db
from datetime import datetime
import uuid
import os

class File(db.Model):
    """File model for storing user uploaded files"""
    __tablename__ = 'files'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, xlsx, xls, csv, docx
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    file_hash = db.Column(db.String(64), nullable=False)  # SHA-256 hash
    processing_status = db.Column(db.String(20), default='pending', nullable=False)  # pending, processing, completed, failed
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_files_user_id', 'user_id'),
        db.Index('idx_files_created_at', 'created_at'),
    )
    
    def __init__(self, user_id, original_filename, stored_filename, file_path, 
                 file_type, mime_type, file_size, file_hash, description=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.original_filename = original_filename
        self.stored_filename = stored_filename
        self.file_path = file_path
        self.file_type = file_type.lower()
        self.mime_type = mime_type
        self.file_size = file_size
        self.file_hash = file_hash
        self.processing_status = 'pending'
        self.description = description
    
    def to_dict(self, include_user=False):
        """Convert file to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'processing_status': self.processing_status,
            'description': self.description,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None
        }
        
        if include_user and self.user:
            data['user'] = self.user.to_dict()
        
        return data
    
    def to_dict_with_user(self):
        """Convert file to dictionary including user information"""
        return self.to_dict(include_user=True)
    
    def update_processing_status(self, status):
        """Update processing status"""
        from flask import current_app
        valid_statuses = ['pending', 'processing', 'completed', 'failed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        self.processing_status = status
        self.updated_at = datetime.utcnow()
        db_instance = current_app.extensions['sqlalchemy']
        db_instance.session.commit()
    
    def get_full_path(self):
        """Get full filesystem path to the file"""
        # file_path already contains the full directory path
        return os.path.join(self.file_path, self.stored_filename)
    
    def exists_on_disk(self):
        """Check if file exists on disk"""
        full_path = self.get_full_path()
        return os.path.exists(full_path) and os.path.isfile(full_path)
    
    def __repr__(self):
        return f'<File {self.original_filename} (user: {self.user_id})>'

