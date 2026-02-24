from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.models.base import Base
from app.helpers.time_helper import utcnow


class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    xp = Column(Integer, default=0)
    coins = Column(Integer, default=0)
    gems = Column(Integer, default=0)
    tickets = Column(Integer, default=0)
    energy = Column(Integer, default=0)

    last_energy_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # timestamps
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=utcnow)

    user = relationship("User", back_populates="wallet")



# TODO RECOMPENSA DE AD
# o que eu recebo

# qual_item_clicou_para_ganhar
# se_assistiu_o_ad_inteiro

# O que eu retorno
# Lista_de_items_para_ganhar
