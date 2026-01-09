from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class UserBuilding(Base):
    __tablename__ = "user_buildings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)

    current_stage = Column(Integer, nullable=False, default=0)

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        # garante unicidade por provider
        {"sqlite_autoincrement": True},
    )

    user = relationship("User", back_populates="user_building")

    building = relationship("Building", back_populates="user_building")
