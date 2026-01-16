from sqlalchemy import Column, String, BigInteger, Numeric, Text, DateTime, Enum, JSON
from sqlalchemy.sql import func
from app.database import Base
import enum

class TransactionType(str, enum.Enum):
    debit = "debit"
    credit = "credit"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String(36), primary_key=True)
    amount = Column(BigInteger, nullable=False)
    currency = Column(String(10), nullable=False)
    human_readable_amount = Column(Numeric(15, 2), nullable=False)
    charge = Column(BigInteger, nullable=False)
    human_readable_charge = Column(Numeric(15, 2), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    decline_reason = Column(Text, nullable=True)
    mode = Column(String(50), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    description = Column(Text, nullable=True)
    external_id = Column(String(255), nullable=True)
    from_wallet = Column(String(10), nullable=True)
    to_wallet = Column(String(10), nullable=True)
    debit_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(6), nullable=False, server_default=func.now())
    recipient = Column(JSON, nullable=True)
