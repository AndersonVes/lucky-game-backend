from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Auth
    auth_provider = Column(String, nullable=False, index=True)  
    provider_user_id = Column(String, nullable=False, index=True)

    # Profile
    email = Column(String, nullable=True, index=True)
    full_name = Column(String, nullable=False)
    locale = Column(String, nullable=True)
    picture_url = Column(String, nullable=True)

    #progression
    rank = Column(Integer, nullable=False, default=1)
    actual_village = Column(Integer, nullable=False, default=1)

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    user_buildings = relationship(
        "UserBuilding",
        back_populates="user"
    )

    wallet = relationship("Wallet", back_populates="user", uselist=False, lazy="joined")

    __table_args__ = (
        # garante unicidade por provider
        {"sqlite_autoincrement": True},
    )

