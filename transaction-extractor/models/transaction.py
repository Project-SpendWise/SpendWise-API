"""
Standard Transaction Schema
Defines the unified transaction model for all bank statements
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal, Dict, Any
from enum import Enum


class TransactionType(str, Enum):
    """Transaction type enumeration"""
    DEBIT = "debit"
    CREDIT = "credit"


class TransactionChannel(str, Enum):
    """Transaction channel enumeration"""
    ATM = "ATM"
    POS = "POS"
    TRANSFER = "Transfer"
    ONLINE = "Online"
    BRANCH = "Branch"
    MOBILE = "Mobile"
    CHECK = "Check"
    OTHER = "Other"


class Currency(str, Enum):
    """Currency enumeration"""
    TRY = "TRY"  # Turkish Lira
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    OTHER = "OTHER"


class Transaction(BaseModel):
    """
    Standard transaction model
    All bank transactions are normalized to this format
    """
    transaction_id: str = Field(
        description="Unique identifier for the transaction"
    )
    date: datetime = Field(
        description="Transaction date and time"
    )
    description: str = Field(
        description="Transaction description or memo"
    )
    amount: float = Field(
        description="Transaction amount (positive for credit, negative for debit or absolute value)"
    )
    currency: Currency = Field(
        default=Currency.TRY,
        description="Transaction currency"
    )
    transaction_type: TransactionType = Field(
        description="Type of transaction (debit or credit)"
    )
    balance_after: Optional[float] = Field(
        default=None,
        description="Account balance after transaction"
    )
    reference_number: Optional[str] = Field(
        default=None,
        description="Bank reference or transaction number"
    )
    channel: Optional[TransactionChannel] = Field(
        default=None,
        description="Transaction channel (ATM, POS, etc.)"
    )
    bank_name: Optional[str] = Field(
        default=None,
        description="Name of the bank"
    )
    account_number: Optional[str] = Field(
        default=None,
        description="Masked account number"
    )
    raw_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Original raw data from extraction"
    )
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount is a valid number"""
        if v == 0:
            raise ValueError("Amount cannot be zero")
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Ensure description is not empty"""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BankStatement(BaseModel):
    """
    Bank statement container with metadata
    """
    bank_name: str = Field(
        description="Name of the bank"
    )
    account_number: Optional[str] = Field(
        default=None,
        description="Account number (masked)"
    )
    statement_period_start: Optional[datetime] = Field(
        default=None,
        description="Statement period start date"
    )
    statement_period_end: Optional[datetime] = Field(
        default=None,
        description="Statement period end date"
    )
    opening_balance: Optional[float] = Field(
        default=None,
        description="Opening balance for the period"
    )
    closing_balance: Optional[float] = Field(
        default=None,
        description="Closing balance for the period"
    )
    currency: Currency = Field(
        default=Currency.TRY,
        description="Currency of the statement"
    )
    transactions: list[Transaction] = Field(
        default_factory=list,
        description="List of transactions"
    )
    extraction_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadata about the extraction process"
    )
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_transaction(self, transaction: Transaction):
        """Add a transaction to the statement"""
        self.transactions.append(transaction)
    
    def get_total_credits(self) -> float:
        """Calculate total credits"""
        return sum(t.amount for t in self.transactions if t.transaction_type == TransactionType.CREDIT)
    
    def get_total_debits(self) -> float:
        """Calculate total debits"""
        return sum(abs(t.amount) for t in self.transactions if t.transaction_type == TransactionType.DEBIT)
    
    def to_json(self) -> str:
        """Export to JSON string"""
        return self.model_dump_json(indent=2)

