from datetime import timedelta
from re import L
from typing import Literal

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.config.game_consts import (BUILDING_MAX_STAGE,
                                    TICKETS_BUILDING_REWARD_STAGE)
from app.db.models import user_village
from app.db.models.building import Building
from app.db.models.building_upgrade_history import BuildingUpgradeHistory
from app.db.models.user import User
from app.db.models.user_building import UserBuilding
from app.db.models.user_village import UserVillage
from app.db.models.villages import Villages
from app.helpers.calc_helper import get_building_cost_modifier
from app.helpers.time_helper import utcnow
from app.services.xp_service import calculate_building_stage_xp


def get_building_stage_cost(db: Session, village: Villages, building: Building, stage: int) -> int:

    if not building:
        raise HTTPException(status_code=404, detail="Building not found in the specified village")

    if stage < 1:
        raise HTTPException(status_code=400, detail="Invalid building stage")
    if stage > building.building_stages:
        return None
    building_cost_modifier = get_building_cost_modifier(village.id)
    if building.cost_curve == "exponential":
        cost = round(
            building.base_cost * building_cost_modifier * (building.cost_multiplier ** (stage - 1))
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported cost curve")

    return cost


def get_next_stage_info(
    db: Session,
    village: Villages,
    building: Building,
    current_stage: int,
):

    cost = get_building_stage_cost(db, village, building, current_stage + 1)

    return {"max": False if cost else True, "cost": cost}


def get_building_stage_cost_by_cost_rank(
    db: Session,
    user: User,
    position_by_cost_asc: int = 1,
    return_type: Literal["cost", "user_building", "both"] = "cost",
) -> int | UserBuilding | tuple[int, UserBuilding] | None:
    candidates = (
        db.query(UserBuilding)
        .join(Building)
        .join(Villages)
        .filter(
            UserBuilding.user_id == user.id,
            Villages.id == user.actual_village,
            UserBuilding.current_stage < Building.building_stages,
        )
        .all()
    )

    if not candidates:
        return None

    candidates_with_cost = [
        (
            ub,
            get_building_stage_cost(
                db,
                ub.building.village,
                ub.building,
                ub.current_stage + 1,
            ),
        )
        for ub in candidates
    ]

    candidates_with_cost.sort(key=lambda x: x[1])
    user_building = None
    if position_by_cost_asc <= 1:
        user_building, building_stage_cost = candidates_with_cost[0]
    else:
        user_building, building_stage_cost = candidates_with_cost[
            min(position_by_cost_asc - 1, len(candidates_with_cost) - 1)
        ]

    if return_type == "cost":
        return building_stage_cost
    elif return_type == "user_building":
        return user_building
    elif return_type == "both":
        return (building_stage_cost, user_building)


def upgrade_building(db: Session, user: User, building_id: int):  # -> UpdateBuildingOut:
    from app.services.village_service import (check_village_completion,
                                              next_village)
    from app.services.wallet_service import add_currency, deduce_currency

    ub = (
        db.query(UserBuilding)
        .filter(UserBuilding.user_id == user.id, UserBuilding.building_id == building_id)
        .first()
    )

    if not ub:
        raise HTTPException(status_code=404, detail="User building not found")

    building = db.query(Building).filter(Building.id == building_id).first()
    village = db.query(Villages).filter(Villages.id == ub.building.village_id).first()

    stage_cost = get_building_stage_cost(db, village, building, ub.current_stage + 1)
    if not stage_cost:
        raise HTTPException(status_code=400, detail="Building already at max stage")

    if user.wallet.coins < stage_cost:
        raise HTTPException(status_code=400, detail="Not enough coins to upgrade building")

    if ub.current_stage < building.building_stages:
        ub.current_stage += 1

    if ub.ticket_stage_reward:
        user_village = (
            db.query(UserVillage)
            .filter(
                UserVillage.user_id == user.id,
                UserVillage.village_id == village.id,
            )
            .first()
        )
        user_village.last_ticket_reward_won_at = utcnow()

        add_currency(db, user, "tickets", amount=ub.ticket_stage_reward)
        ub.ticket_stage_reward = None

    deduce_currency(db, user, "coins", stage_cost)

    xp_to_add = calculate_building_stage_xp(building.base_completion_reward_xp, ub.current_stage)
    add_currency(db, user, "xp", amount=xp_to_add)

    upgraded_village = False
    need_reset = False

    if check_village_completion(db, user):
        _next_village = next_village(db, user, village)
        need_reset = _next_village["need_reset"] | False
        if not need_reset:
            upgraded_village = True

    building_upgrade_history = BuildingUpgradeHistory(
        user_id=user.id,
        village_id=village.id,
        building_id=building.id,
        new_building_stage=ub.current_stage,
    )

    db.add(building_upgrade_history)

    return {
        "message": "Building upgraded successfully",
        "cost": stage_cost,
        "xp_earned": xp_to_add,
        "building_current_stage": ub.current_stage,
        "upgraded_village": upgraded_village,
        "need_reset": need_reset,
        "utcnow": utcnow(),
    }


def add_ticket_reward_building(
    db: Session,
    user: User,
    user_buildings: list[UserBuilding],
):
    user_village = (
        db.query(UserVillage)
        .filter(
            UserVillage.village_id == user.actual_village,
            UserVillage.user_id == user.id,
        )
        .first()
    )

    if not user_village:
        raise Exception("User village not found")

    now = utcnow()

    last_won = user_village.last_ticket_reward_won_at
    last_set = user_village.last_ticket_reward_set_at

    # 15 minute cooldown control
    if last_won and now < last_won + timedelta(minutes=15):
        return None

    # 24h cooldown after finishing full cycle
    if user_village.ticket_reward_index >= BUILDING_MAX_STAGE:
        if not last_set or now < last_set + timedelta(hours=24):
            return None

        user_village.ticket_reward_index = 0

    # Get reward for current index
    reward = next(
        (
            item
            for item in TICKETS_BUILDING_REWARD_STAGE
            if item["index"] == user_village.ticket_reward_index
        ),
        None,
    )

    if not reward:
        return None

    tickets = reward["tickets"]

    # ---- NEW LOGIC STARTS HERE ----

    village = db.query(Villages).filter(Villages.id == user.actual_village).first()

    # Build list with cost reference
    building_cost_pairs = []

    for ub in user_buildings:
        next_stage = get_next_stage_info(
            db,
            village,
            ub.building,
            ub.current_stage,
        )

        if not next_stage["max"]:
            building_cost_pairs.append((ub, next_stage["cost"]))

    # Sort by next stage cost ascending
    building_cost_pairs.sort(key=lambda x: x[1])

    if not building_cost_pairs:
        return None

    # Select building based on reward index
    target_position = user_village.ticket_reward_index

    if target_position >= len(building_cost_pairs):
        return None

    target_ub = building_cost_pairs[target_position][0]

    target_ub.ticket_stage_reward = tickets

    # ---- NEW LOGIC ENDS HERE ----

    user_village.last_ticket_reward_won_at = now

    if user_village.ticket_reward_index + 1 >= BUILDING_MAX_STAGE:
        user_village.last_ticket_reward_set_at = now

    user_village.ticket_reward_index += 1

    return tickets
