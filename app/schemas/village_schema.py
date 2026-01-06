from pydantic import BaseModel, PositiveInt

from app.schemas.building_schema import BuildingOut


class CompletionRewardOut(BaseModel):
    coins: int
    gems: int
    energy: int
    item_id: int


class VillageOut(BaseModel):
    id: PositiveInt
    name: str
    completion_reward: CompletionRewardOut
    buildings: list[BuildingOut]
