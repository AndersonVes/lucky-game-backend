from datetime import datetime
from typing import Optional

from pydantic import BaseModel, NonNegativeInt, PositiveInt

from app.schemas.building_schema import BuildingOut


class CompletionRewardOut(BaseModel):
    coins: int
    gems: int
    energy: int
    item_slug: Optional[str]


class VillageOut(BaseModel):
    id: int
    name: str
    reset_available: bool
    completion_reward: CompletionRewardOut
    buildings: list[BuildingOut]
    utcnow: Optional[datetime] = None

    class Config:
        from_attributes = True


class UpdateBuildingIn(BaseModel):
    building_id: NonNegativeInt


class UpdateBuildingOut(BaseModel):
    message: str
    cost: NonNegativeInt
    upgraded_village: bool
    utcnow: Optional[datetime] = None


# RESET

class ResetAvailableOut(BaseModel):
    reset_available: bool

class Reset(BaseModel):
    message: str
    reset: bool
