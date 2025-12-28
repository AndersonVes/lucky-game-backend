from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    store = Column(String)  # google | apple
    product_id = Column(String)
    receipt_id = Column(String, unique=True)
    amount = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
