from app import db
from datetime import datetime
import uuid

class Budget(db.Model):
    """Budget model for storing user budget settings"""
    __tablename__ = 'budgets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.String(100), nullable=False)
    category_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    period = db.Column(db.String(20), nullable=False)  # monthly, yearly
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_budgets_user_category', 'user_id', 'category_id'),
        db.Index('idx_budgets_user_period', 'user_id', 'period'),
        db.Index('idx_budgets_start_date', 'start_date'),
    )
    
    def __init__(self, user_id, category_id, category_name, amount, period, start_date, end_date=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.category_id = category_id
        self.category_name = category_name
        self.amount = amount
        self.period = period
        self.start_date = start_date
        self.end_date = end_date
    
    def to_dict(self):
        """Convert budget to dictionary matching API response format"""
        return {
            'id': self.id,
            'categoryId': self.category_id,
            'categoryName': self.category_name,
            'amount': float(self.amount),
            'period': self.period,
            'startDate': self.start_date.isoformat() + 'Z' if self.start_date else None,
            'endDate': self.end_date.isoformat() + 'Z' if self.end_date else None,
            'createdAt': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() + 'Z' if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Budget {self.category_name} (amount: {self.amount}, period: {self.period})>'

