import math

from sqlalchemy.orm import Session

from app.config.game_consts import (XP_BASE, XP_BUILDINGS_STAGE_GROWTH,
                                    XP_GROWTH)
from app.db.models.user import User


def _xp_required_for_rank(rank: int) -> int:
    if rank <= 1:
        return 0

    xp = 0
    for lvl in range(1, rank):
        xp += math.floor(XP_BASE * (XP_GROWTH ** (lvl - 1)))

    return xp


def _rank_from_xp(total_xp: int) -> int:
    rank = 1
    xp_accumulated = 0

    while True:
        xp_for_next = math.floor(XP_BASE * (XP_GROWTH ** (rank - 1)))

        if total_xp < xp_accumulated + xp_for_next:
            return rank

        xp_accumulated += xp_for_next
        rank += 1


def _xp_to_next_rank(total_xp: int) -> int:
    rank = _rank_from_xp(total_xp)

    xp_next_rank_start = _xp_required_for_rank(rank + 1)

    return xp_next_rank_start


def get_xp_data(db: Session, user: User):
    xp = user.wallet.xp
    current_rank = _rank_from_xp(xp)
    return {
        "user_rank": current_rank,
        "current_xp": xp,
        "xp_to_current_rank": _xp_required_for_rank(current_rank),
        "xp_to_next_rank": _xp_to_next_rank(xp),
    }


def calculate_building_stage_xp(
    base_xp: int,
    stage_index: int,
    stage_growth: float = XP_BUILDINGS_STAGE_GROWTH,
) -> int:
    multiplier = 1 + ((stage_index - 1) * stage_growth)
    return int(base_xp * multiplier)


def calculate_building_stage_xp(
    base_xp: int,
    stage_index: int,
    stage_growth: float = XP_BUILDINGS_STAGE_GROWTH,
) -> int:
    multiplier = 1 + ((stage_index - 1) * stage_growth)
    return int(base_xp * multiplier)

def update_user_rank(db: Session, user: User):

    current_rank = _rank_from_xp(user.wallet.xp)

    if user.rank != current_rank:
        user.rank = current_rank
