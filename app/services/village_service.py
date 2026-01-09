from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.building import Building
from app.models.user import User
from app.models.user_building import UserBuilding
from app.models.villages import Villages


def get_building_stage_cost(db: Session, village: Villages, building: Building, stage: int) -> int:

    if not building:
        raise HTTPException(status_code=404, detail="Building not found in the specified village")

    if stage < 1 or stage > building.building_stages:
        raise HTTPException(status_code=400, detail="Invalid building stage")

    if building.cost_curve == "exponential":
        cost = round(
            building.base_cost
            * village.building_cost_modifier
            * (building.cost_multiplier ** (stage - 1))
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported cost curve")

    return cost


def get_actual_village(db: Session, user: User) -> dict:
    village = (
        db.query(
            Villages.id,
            Villages.name,
            Villages.building_cost_modifier,
            Villages.completion_reward_coins,
            Villages.completion_reward_gems,
            Villages.completion_reward_xp,
            Villages.completion_reward_energy,
            Villages.completion_reward_item_id,
        )
        .filter(Villages.id == user.actual_village)
        .first()
    )

    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    rows = (
        db.query(
            Building.id,
            Building.name,
            Building.building_stages,
            Building.cost_curve,
            Building.base_cost,
            Building.cost_multiplier,
            Building.created_at,
            Building.updated_at,
            UserBuilding.id.label("user_building_id"),
            UserBuilding.current_stage.label("user_building_current_stage"),
            UserBuilding.created_at.label("user_building_created_at"),
            UserBuilding.updated_at.label("user_building_updated_at"),
        )
        .join(Building)
        .filter(Building.village_id == village.id, UserBuilding.user_id == user.id)
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail="No buildings found for the user's village")

    buildings = []
    for row in rows:
        (
            building_id,
            name,
            building_stages,
            cost_curve,
            base_base_cost,
            cost_multiplier,
            created_at,
            updated_at,
            user_building_id,
            user_building_current_stage,
            user_building_created_at,
            user_building_updated_at,
        ) = row
        building_dict = {
            "id": building_id,
            "name": name,
            "building_stages": building_stages,
            "created_at": created_at,
            "updated_at": updated_at,
            "next_stage": {
                "max": user_building_current_stage >= building_stages,
                "cost": (
                    get_building_stage_cost(db, village, row, user_building_current_stage + 1)
                    if user_building_current_stage < building_stages
                    else None
                ),
                # "stage": user_building_current_stage + 1 if user_building_current_stage < building_stages else None,
            },
            "user_building": {
                "id": user_building_id,
                "current_stage": user_building_current_stage,
                "created_at": user_building_created_at,
                "updated_at": user_building_updated_at,
            },
        }
        buildings.append(building_dict)

    return {
        "id": village.id,
        "name": village.name,
        "completion_reward": {
            "coins": village.completion_reward_coins,
            "gems": village.completion_reward_gems,
            "energy": village.completion_reward_energy,
            "item_id": village.completion_reward_item_id,
        },
        "buildings": buildings,
    }


def next_village(db: Session, village_id: int, user_id: int):
    buildings = db.query(Building).filter(Building.village_id == village_id).all()

    for building in buildings:
        db.add(UserBuilding(user_id=user_id, building_id=building.id))

    db.flush()
