from sqlalchemy import (Boolean, CheckConstraint, Column, DateTime, Enum,
                        Float, Integer, String)
from sqlalchemy.orm import relationship

from app.db.models.base import Base
from app.helpers.time_helper import utcnow


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)

    slug = Column(String, nullable=False, unique=True)
    image_url = Column(String, nullable=False)
    model_url = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    rarity = Column(Float, nullable=False)
    type = Column(Enum("hat", "outfit", name="item_type"), nullable=False)

    drawn_available = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=utcnow)

    user_item = relationship("UserItem", back_populates="item")
    

    __table_args__ = (CheckConstraint("rarity > 0", name="ck_cards_rarity_positive"),)
