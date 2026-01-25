from sqlalchemy import Column, String, BigInteger, Numeric, Text, DateTime, Enum, JSON, Integer, TIMESTAMP
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


class TransactionCache(Base):
    """
    Cache table for transactions from external SpennX API
    Synced periodically to maintain a local copy of global transactions
    """
    __tablename__ = "transaction_cache"
    
    id = Column(String(40), primary_key=True)  # UUID from external API
    amount = Column(Integer, nullable=False)
    human_readable_amount = Column(Numeric(10, 2), nullable=True)
    charge = Column(Integer, nullable=True)
    human_readable_charge = Column(Numeric(10, 2), nullable=True)
    status = Column(String(20), nullable=True)
    decline_reason = Column(String(255), nullable=True)
    mode = Column(String(20), nullable=True)
    type = Column(String(20), nullable=True)
    description = Column(String(255), nullable=True)
    external_id = Column(String(100), nullable=True)
    currency = Column(String(3), nullable=True)
    created_at = Column(DateTime, nullable=True)
    recipient = Column(JSON, nullable=True)
    # Wallet swap fields
    from_wallet = Column(String(10), nullable=True)
    to_wallet = Column(String(10), nullable=True)
    debit_id = Column(String(40), nullable=True)
    credit_id = Column(String(40), nullable=True)
    rate = Column(Numeric(20, 12), nullable=True)  
    cached_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(
        TIMESTAMP, 
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
