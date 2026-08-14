"""initial schema

Revision ID: cf17524ab04c
Revises: 
Create Date: 2026-08-14 18:29:45.787773

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.db.models.base import Base
from app.db.models.user import User
from app.db.models.item import Item
from app.db.models.content_patches import ContentPatch
from app.db.models.villages import Villages
from app.db.models.building import Building
from app.db.models.event import Event
from app.db.models.wallet import Wallet
from app.db.models.purchase import Purchase
from app.db.models.user_boost import UserBoost
from app.db.models.wallet_transaction import WalletTransaction
from app.db.models.user_item import UserItem
from app.db.models.user_building import UserBuilding
from app.db.models.user_village import UserVillage
from app.db.models.user_event import UserEvent
from app.db.models.building_upgrade_history import BuildingUpgradeHistory
from app.db.models.card_hash import CardHash


# revision identifiers, used by Alembic.
revision: str = 'cf17524ab04c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLES = [
    User.__table__,
    Item.__table__,
    ContentPatch.__table__,
    Villages.__table__,
    Building.__table__,
    Event.__table__,
    Wallet.__table__,
    Purchase.__table__,
    UserBoost.__table__,
    WalletTransaction.__table__,
    UserItem.__table__,
    UserBuilding.__table__,
    UserVillage.__table__,
    UserEvent.__table__,
    BuildingUpgradeHistory.__table__,
    CardHash.__table__,
]


def upgrade():
    Base.metadata.create_all(bind=op.get_bind(), tables=TABLES)


def downgrade():
    Base.metadata.drop_all(bind=op.get_bind(), tables=list(reversed(TABLES)))
