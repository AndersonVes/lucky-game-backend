import math

from sqlalchemy.orm import Session

from app.config.game_consts import (XP_BASE, XP_BUILDINGS_STAGE_GROWTH,
                                    XP_GROWTH)
from app.db.models.user import User


def _xp_required_for_level(level: int) -> int:
    if level <= 1:
        return 0

    xp = 0
    for lvl in range(1, level):
        xp += math.floor(XP_BASE * (XP_GROWTH ** (lvl - 1)))

    return xp


def _level_from_xp(total_xp: int) -> int:
    level = 1
    xp_accumulated = 0

    while True:
        xp_for_next = math.floor(XP_BASE * (XP_GROWTH ** (level - 1)))

        if total_xp < xp_accumulated + xp_for_next:
            return level

        xp_accumulated += xp_for_next
        level += 1


def _xp_to_next_level(total_xp: int) -> int:
    level = _level_from_xp(total_xp)

    xp_next_level_start = _xp_required_for_level(level + 1)

    return xp_next_level_start


def get_xp_data(db: Session, user: User):
    xp = user.wallet.xp
    current_level = _level_from_xp(xp)
    return {
        "user_level": current_level,
        "current_xp": xp,
        "xp_to_current_level": _xp_required_for_level(current_level),
        "xp_to_next_level": _xp_to_next_level(xp),
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
