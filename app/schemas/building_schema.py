from datetime import datetime
from typing import Optional

from pydantic import BaseModel, NonNegativeInt, PositiveInt


class UserBuildingOut(BaseModel):
    id: int
    current_stage: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class NextStageOut(BaseModel):
    max: bool
    cost: Optional[int]
    tickets_reward: Optional[int] = None


class BuildingOut(BaseModel):
    id: PositiveInt
    name: str
    building_stages: PositiveInt
    user_building: UserBuildingOut
    next_stage: NextStageOut

    created_at: datetime
    updated_at: datetime | None


class UpgradeBuildingOut(BaseModel):
    message: str
    cost: NonNegativeInt
    xp_earned: NonNegativeInt
    building_current_stage: PositiveInt
    upgraded_village: bool
    need_reset: bool

    class Config:
        from_attributes = True
