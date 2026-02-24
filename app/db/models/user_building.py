from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.models.base import Base
from app.helpers.time_helper import utcnow


class UserBuilding(Base):
    __tablename__ = "user_buildings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)

    current_stage = Column(Integer, nullable=False, default=0)

    ticket_stage_reward = Column(Integer, nullable=True)

    # timestamps
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=utcnow)

    __table_args__ = (
        # garante unicidade por provider
        {"sqlite_autoincrement": True},
    )

    user = relationship("User", back_populates="user_building")

    building = relationship("Building", back_populates="user_building")
