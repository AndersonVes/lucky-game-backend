from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.models.building import Building
from app.db.models.building_upgrade_history import BuildingUpgradeHistory
from app.db.models.user import User
from app.db.models.user_building import UserBuilding
from app.db.models.villages import Villages
from app.helpers.calc_helper import get_building_cost_modifier
from app.helpers.time_helper import utcnow
from app.schemas.village_schema import BuildingOut, VillageOut
from app.services.items_service import add_item
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


def get_actual_village(db: Session, user: User) -> VillageOut:
    from app.services.reset_service import reset_available

    village = db.query(Villages).filter(Villages.id == user.actual_village).first()

    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    user_buildings = (
        db.query(UserBuilding)
        .options(joinedload(UserBuilding.building))
        .filter(UserBuilding.user_id == user.id)
        .all()
    )

    buildings_out = []

    for ub in user_buildings:
        building = ub.building

        next_stage = get_next_stage_info(db, village, building, ub.current_stage)

        buildings_out.append(
            BuildingOut.model_validate(
                {
                    **building.__dict__,
                    "next_stage": next_stage,
                    "user_building": ub,
                }
            )
        )

    buildings_out.sort(key=lambda b: b.id)

    return VillageOut(
        id=village.id,
        name=village.name,
        completion_reward={
            "coins": village.starting_reward_coins,
            "gems": village.starting_reward_gems,
            "energy": village.starting_reward_energy,
            "item_slug": village.starting_reward_item_slug,
        },
        buildings=buildings_out,
        reset_available=reset_available(db, user),
        utcnow=utcnow(),
    )


def get_next_village(db: Session, current_village: Villages | None = None) -> Villages | None:
    if current_village is None:
        return db.query(Villages).filter(Villages.id == 1).first()

    return db.query(Villages).filter(Villages.id == current_village.id + 1).first()


def next_village(
    db: Session,
    user: User,
    current_village: Villages | None = None,
):
    from app.services.wallet_service import add_currency

    need_reset = False

    next_village = get_next_village(db, current_village)

    if next_village is None:
        need_reset = True
        return {"need_reset": need_reset}

    add_currency(db, user, "coins", amount=next_village.starting_reward_coins)
    add_currency(db, user, "gems", amount=next_village.starting_reward_gems)
    add_currency(db, user, "energy", amount=next_village.starting_reward_energy)
    add_currency(db, user, "xp", amount=next_village.starting_reward_xp)

    try:
        add_item(db, user, next_village.starting_reward_item_slug)
    except Exception:
        pass

    buildings = db.query(Building).filter(Building.village_id == next_village.id).all()

    for building in buildings:
        db.add(UserBuilding(user_id=user.id, building_id=building.id))

    next_village = get_next_village(db, current_village)

    user.actual_village = next_village.id

    db.flush()

    return {"need_reset": need_reset}


def get_next_cheaper_building_stage_cost(db: Session, user: User) -> int | None:
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

    cheapest = min(
        candidates,
        key=lambda ub: get_building_stage_cost(
            db,
            ub.building.village,
            ub.building,
            ub.current_stage + 1,
        ),
    )

    cheapest_value = get_building_stage_cost(
        db,
        cheapest.building.village,
        cheapest.building,
        cheapest.current_stage + 1,
    )

    return cheapest_value


def check_village_completion(db: Session, user: User):
    user_buildings = (
        db.query(UserBuilding)
        .options(joinedload(UserBuilding.building))
        .filter(UserBuilding.user_id == user.id)
        .all()
    )

    if all(ub.current_stage >= ub.building.building_stages for ub in user_buildings):
        return True

    return False


def upgrade_building(db: Session, user: User, building_id: int):  # -> UpdateBuildingOut:
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
