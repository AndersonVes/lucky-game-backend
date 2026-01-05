from os import name
from sqlalchemy import Column, Float, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Villages(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False, unique=True)
    
    building_cost_modifier = Column(Float, nullable=False, default=1.0)
    
    #reward on completion of all buildings
    coins = Column(Integer, nullable=False, default=0)
    gems = Column(Integer, nullable=False, default=0)
    xp = Column(Integer, nullable=False, default=0)
    energy = Column(Integer, nullable=False, default=0)
    item_slug = Column(String, nullable=True)

    
    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    buildings = relationship(
        "Buildings",
        back_populates="village"
    )
