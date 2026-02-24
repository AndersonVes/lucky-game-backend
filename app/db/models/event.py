from sqlalchemy import (CheckConstraint, Column, DateTime, Enum, ForeignKey,
                        Integer, String, UniqueConstraint, desc)
from sqlalchemy.orm import relationship

from app.db.models.base import Base
from app.helpers.time_helper import utcnow


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    slug = Column(String, nullable=False, unique=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    type = Column(Enum("seasonal", "progression", name="event_type"), nullable=False)
    spin_currency = Column(
        Enum("tickets", "gems", "coins", "energy", name="event_spin_currency"),
        nullable=False, default="tickets"
    )
    cost_per_spin = Column(Integer, nullable=False, default=10)

    target_item_slug = Column(String, ForeignKey("items.slug"), nullable=False)
    secondary_target_item_slug = Column(String, ForeignKey("items.slug"), nullable=True)

    # progression fields
    progression_line_id = Column(Integer, nullable=True)
    order_in_line = Column(Integer, nullable=True)

    # seasonal fields
    start_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        # evita ordem repetida dentro da mesma linha
        UniqueConstraint("progression_line_id", "order_in_line", name="uq_progression_line_order"),
        # garante que order_in_line >= 1 quando existir
        CheckConstraint(
            """
            order_in_line IS NULL OR order_in_line >= 1
            """,
            name="ck_order_positive",
        ),
        # garante que end_at > start_at quando for seasonal
        CheckConstraint(
            """
            start_at IS NULL
            OR end_at IS NULL
            OR end_at > start_at
            """,
            name="ck_end_after_start",
        ),
        # regra principal: evento é OU seasonal OU progression (exclusivo e obrigatório)
        CheckConstraint(
            """
            (
                type = 'seasonal'
                AND start_at IS NOT NULL
                AND end_at IS NOT NULL
                AND progression_line_id IS NULL
                AND order_in_line IS NULL
            )
            OR
            (
                type = 'progression'
                AND start_at IS NULL
                AND end_at IS NULL
                AND progression_line_id IS NOT NULL
                AND order_in_line IS NOT NULL
            )
            """,
            name="ck_event_type_exclusive",
        ),
        {"sqlite_autoincrement": True},
    )

    # timestamps
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=utcnow)

    user_event = relationship("UserEvent", back_populates="event")
    card_hash = relationship("CardHash", back_populates="event")

    target_item = relationship("Item", foreign_keys=[target_item_slug])
    secondary_target_item = relationship("Item", foreign_keys=[secondary_target_item_slug])
