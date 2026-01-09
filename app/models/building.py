from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False)
    name = Column(String, nullable=False)
    building_stages = Column(Integer, nullable=False, default=4)

    # cost
    cost_curve = Column(String, nullable=False, default="exponential")
    base_cost = Column(Integer, nullable=False)
    cost_multiplier = Column(Float, nullable=False, default=1.35)
    # cost(stage) =
    # round(
    #     base_cost
    #     × (cost_multiplier ^ (stage - 1))
    #     × village_cost_modifier
    # )

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    village = relationship("Villages", back_populates="building")
    user_building = relationship("UserBuilding", back_populates="building")
