from pyexpat import model
from sqlalchemy import CheckConstraint, Column, Float, Integer, ForeignKey, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)

    slug = Column(String, nullable=False, unique=True)
    image_url = Column(String, nullable=False)
    model_url = Column(
        String, nullable=False
    )  # TODO dependendo de como forem referenciados os models, pode ser que essa coluna seja desnecessaria ou int, fk
    name = Column(String, nullable=False)
    # description = Column(String, nullable=False) #TODO consultar os macacos sobre existencia desse campo e estabelecer limites (null, max chars)
    rarity = Column(Float, nullable=False)

    # TODO price  em coins/gems/userLevel/newVillage/envento

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user_item = relationship("UserItem", back_populates="item")
    card_hash = relationship("CardHash", back_populates="item")

    __table_args__ = (CheckConstraint("rarity > 0", name="ck_cards_rarity_positive"),)
