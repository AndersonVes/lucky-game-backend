from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # reward | purchase | spend
    amount = Column(Integer)
    balance_after = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
