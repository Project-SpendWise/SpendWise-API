from app import db
from datetime import datetime
import uuid

class Statement(db.Model):
    """Statement model for storing bank statement uploads and processing status"""
    __tablename__ = 'statements'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    statement_period_start = db.Column(db.DateTime, nullable=True)
    statement_period_end = db.Column(db.DateTime, nullable=True)
    transaction_count = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(20), default='processing', nullable=False)  # processing, processed, failed
    error_message = db.Column(db.Text, nullable=True)
    
    # Profile metadata fields
    profile_name = db.Column(db.String(255), nullable=True)
    profile_description = db.Column(db.Text, nullable=True)
    account_type = db.Column(db.String(100), nullable=True)  # Checking, Savings, Credit Card, Business, etc.
    bank_name = db.Column(db.String(255), nullable=True)
    color = db.Column(db.String(7), nullable=True)  # Hex color code (e.g., "#FF5733")
    icon = db.Column(db.String(50), nullable=True)  # Icon identifier (e.g., "wallet", "credit-card")
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    transactions = db.relationship(
        'Transaction',
        backref='statement',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='Transaction.statement_id'
    )
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_statements_user_id', 'user_id'),
        db.Index('idx_statements_status', 'status'),
        db.Index('idx_statements_upload_date', 'upload_date'),
    )
    
    def __init__(self, user_id, file_name, file_path, status='processing', 
                 profile_name=None, profile_description=None, account_type=None,
                 bank_name=None, color=None, icon=None, is_default=False):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.file_name = file_name
        self.file_path = file_path
        self.status = status
        self.transaction_count = 0
        self.profile_name = profile_name
        self.profile_description = profile_description
        self.account_type = account_type
        self.bank_name = bank_name
        self.color = color
        self.icon = icon
        self.is_default = is_default
    
    def to_dict(self):
        """Convert statement to dictionary matching API response format"""
        return {
            'id': self.id,
            'fileName': self.file_name,
            'uploadDate': self.upload_date.isoformat() + 'Z' if self.upload_date else None,
            'status': self.status,
            'transactionCount': self.transaction_count,
            'statementPeriodStart': self.statement_period_start.isoformat() + 'Z' if self.statement_period_start else None,
            'statementPeriodEnd': self.statement_period_end.isoformat() + 'Z' if self.statement_period_end else None,
            'isProcessed': self.status == 'processed',
            # Profile metadata
            'profileName': self.profile_name,
            'profileDescription': self.profile_description,
            'accountType': self.account_type,
            'bankName': self.bank_name,
            'color': self.color,
            'icon': self.icon,
            'isDefault': self.is_default
        }
    
    def update_status(self, status, error_message=None):
        """Update statement status"""
        valid_statuses = ['processing', 'processed', 'failed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        self.status = status
        if error_message:
            self.error_message = error_message
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Statement {self.file_name} (user: {self.user_id}, status: {self.status})>'

