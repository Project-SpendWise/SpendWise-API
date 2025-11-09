from app import db
from datetime import datetime
import bcrypt
import uuid

class User(db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationship to files
    files = db.relationship(
        'File',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='File.user_id'
    )
    
    def __init__(self, email, password, username=None, first_name=None, last_name=None):
        self.id = str(uuid.uuid4())
        self.email = email.lower().strip()
        self.username = username.strip() if username else None
        self.first_name = first_name.strip() if first_name else None
        self.last_name = last_name.strip() if last_name else None
        self.set_password(password)
        self.is_active = True
    
    def set_password(self, password):
        """Hash and set the password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'is_active': self.is_active
        }
        
        if include_sensitive:
            data['last_login'] = self.last_login.isoformat() + 'Z' if self.last_login else None
        
        return data
    
    def get_files_count(self):
        """Get count of user's files"""
        from sqlalchemy import func, select
        from models.file import File
        from flask import current_app
        db_instance = current_app.extensions['sqlalchemy']
        result = db_instance.session.scalar(
            select(func.count(File.id)).filter_by(user_id=self.id)
        )
        return result or 0
    
    def get_files_by_type(self, file_type):
        """Get user's files filtered by type"""
        from sqlalchemy import select
        from models.file import File
        from flask import current_app
        db_instance = current_app.extensions['sqlalchemy']
        return db_instance.session.scalars(
            select(File).filter_by(user_id=self.id, file_type=file_type.lower())
        ).all()
    
    def __repr__(self):
        return f'<User {self.email}>'

