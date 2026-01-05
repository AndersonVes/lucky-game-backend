from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.villages import Villages
from app.models.buildings import Buildings
from app.models.user_building import UserBuilding


def get_building_stage_cost(
    db: Session,
    village_id: int,
    building_id: int,
    stage: int
) -> dict:

    building = (
        db.query(Buildings)
        .join(Villages)
        .filter(
            Buildings.id == building_id,
            Buildings.village_id == village_id
        )
        .first()
    )

    if not building:
        raise HTTPException(404, "Building not found")

    if stage < 1 or stage > building.building_stages:
        raise HTTPException(400, "Invalid stage")

    cost = round(
        building.base_cost
        * (building.cost_multiplier ** (stage - 1))
        * building.village.building_cost_modifier
    )

    return cost
def next_village(db: Session, village_id: int, user_id: int):
    buildings = (
        db.query(Buildings)
        .filter(Buildings.village_id == village_id)
        .all()
    )

    for building in buildings:
        db.add(UserBuilding(
            user_id=user_id,
            building_id=building.id
        ))
