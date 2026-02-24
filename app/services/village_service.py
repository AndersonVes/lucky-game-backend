from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.models import user
from app.db.models.building import Building
from app.db.models.user import User
from app.db.models.user_building import UserBuilding
from app.db.models.user_village import UserVillage
from app.db.models.villages import Villages
from app.helpers.time_helper import utcnow
from app.schemas.village_schema import BuildingOut, VillageOut
from app.services.building_service import (add_ticket_reward_building,
                                           get_next_stage_info)
from app.services.items_service import add_item


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
    #
    has_ticket_reward = any(ub.ticket_stage_reward is not None for ub in user_buildings)

    if not has_ticket_reward:
        add_ticket_reward_building(db, user, user_buildings)
        db.flush()

    buildings_out = []

    for ub in user_buildings:
        building = ub.building

        next_stage = get_next_stage_info(
            db,
            village,
            building,
            ub.current_stage,
        )

        next_stage["tickets_reward"] = ub.ticket_stage_reward

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
    village_id = None
    if current_village is None:
        village_id = 1
    else:
        village_id = current_village.id + 1

    return db.query(Villages).filter(Villages.id == village_id).first()


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

    user_village = UserVillage(
        user_id=user.id,
        village_id=next_village.id,
    )
    db.add(user_village)

    buildings = db.query(Building).filter(Building.village_id == next_village.id).all()

    for building in buildings:
        db.add(UserBuilding(user_id=user.id, building_id=building.id))

    next_village = get_next_village(db, current_village)

    user.actual_village = next_village.id

    db.flush()

    return {"need_reset": need_reset}


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
