from datetime import datetime
from pydantic import BaseModel, NonNegativeInt, PositiveInt

class UserBuildingOut(BaseModel):
    id: PositiveInt
    current_stage: NonNegativeInt
    created_at: datetime
    updated_at: datetime | None

class NextStageOut(BaseModel):
    max: bool
    cost: PositiveInt | None 

class BuildingOut(BaseModel):
    id: PositiveInt
    name: str
    building_stages: PositiveInt
    created_at: datetime
    updated_at: datetime | None
    user_building: UserBuildingOut
    next_stage: NextStageOut

    class Config:
        from_attributes = True