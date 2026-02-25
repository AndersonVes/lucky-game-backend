from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.models.base import Base
from app.helpers.time_helper import utcnow


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

    # progression
    rank = Column(Integer, nullable=False, default=1)
    actual_village = Column(Integer, nullable=False, default=1)
    resets = Column(Integer, nullable=False, default=0)

    # daily reward
    last_daily_reward_won_at = Column(DateTime(timezone=True), nullable=True)
    consecutive_days_logged_in = Column(Integer, nullable=False, default=0)

    # cards
    last_jackpot_at = Column(DateTime(timezone=True), nullable=True)

    # timestamps
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=utcnow)

    user_building = relationship(
        "UserBuilding",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    user_village = relationship(
        "UserVillage",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    user_item = relationship(
        "UserItem",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    user_boost = relationship(
        "UserBoost",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    card_hash = relationship(
        "CardHash",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    wallet_transactions = relationship(
        "WalletTransaction",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    wallet = relationship(
        "Wallet",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
        lazy="joined",
    )

    building_upgrade_history = relationship(
        "BuildingUpgradeHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    user_event = relationship(
        "UserEvent",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    __table_args__ = (
        # garante unicidade por provider
        {"sqlite_autoincrement": True},
    )
