from app import db
from datetime import datetime
import uuid

class Transaction(db.Model):
    """Transaction model for storing financial transactions"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    statement_id = db.Column(db.String(36), db.ForeignKey('statements.id', ondelete='CASCADE'), nullable=False, index=True)
    date = db.Column(db.DateTime, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # income, expense
    category = db.Column(db.String(100), nullable=True, index=True)
    merchant = db.Column(db.String(255), nullable=True)
    account = db.Column(db.String(100), nullable=True)
    reference_number = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_transactions_user_date', 'user_id', 'date'),
        db.Index('idx_transactions_user_category', 'user_id', 'category'),
        db.Index('idx_transactions_statement', 'statement_id'),
        db.Index('idx_transactions_date', 'date'),
    )
    
    def __init__(self, user_id, statement_id, date, description, amount, type, 
                 category=None, merchant=None, account=None, reference_number=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.statement_id = statement_id
        self.date = date
        self.description = description
        self.amount = amount
        self.type = type
        self.category = category
        self.merchant = merchant
        self.account = account
        self.reference_number = reference_number
    
    def to_dict(self):
        """Convert transaction to dictionary matching API response format"""
        return {
            'id': self.id,
            'date': self.date.isoformat() + 'Z' if self.date else None,
            'description': self.description,
            'amount': float(self.amount),
            'type': self.type,
            'category': self.category,
            'merchant': self.merchant,
            'account': self.account,
            'referenceNumber': self.reference_number,
            'statementId': self.statement_id
        }
    
    def __repr__(self):
        return f'<Transaction {self.description[:30]}... (amount: {self.amount}, type: {self.type})>'

