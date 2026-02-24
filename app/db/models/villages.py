from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.models.base import Base
from app.helpers.time_helper import utcnow


class Villages(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    # building_cost_modifier = Column(Float, nullable=False, default=1.0)

    # reward on completion of all buildings

    starting_reward_coins = Column(Integer, nullable=False, default=0)
    starting_reward_gems = Column(Integer, nullable=False, default=0)
    starting_reward_xp = Column(Integer, nullable=False, default=0)
    starting_reward_energy = Column(Integer, nullable=False, default=0)
    starting_reward_item_slug = Column(String, ForeignKey("items.slug"), nullable=True)

    # timestamps
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=utcnow)

    building = relationship("Building", back_populates="village")
    building_upgrade_history = relationship("BuildingUpgradeHistory", back_populates="village")
    user_village = relationship(
        "UserVillage",
        back_populates="village",
        cascade="all, delete-orphan",
    )
