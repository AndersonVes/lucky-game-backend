from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.models.base import Base
from app.helpers.time_helper import utcnow


class UserVillage(Base):
    __tablename__ = "user_villages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    village_id = Column(Integer, ForeignKey("villages.id", ondelete="CASCADE"))

    # ticket reward
    last_ticket_reward_set_at = Column(DateTime(timezone=True), nullable=True)
    ticket_reward_index = Column(Integer, nullable=False, default=0)
    last_ticket_reward_won_at = Column(DateTime(timezone=True), nullable=True)

    # timestamps
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=utcnow)

    user = relationship("User", back_populates="user_village")
    village = relationship("Villages", back_populates="user_village")
