from typing import Literal, Optional, Union
from uuid import UUID

from pydantic import UUID4, BaseModel, Field, NonNegativeFloat, NonNegativeInt


class NewGameIn(BaseModel):
    event_slug: Optional[str] = Field(
        default=None,
        description="Slug da carta objetivo (ex: item3). Caso não esteja presente, o jogo será de coins_jackpot.",
    )


class NewGameOut(BaseModel):
    game_uuid: UUID
    reward_focus: str
    reward_probability: Optional[float] = Field(
        ...,
        ge=0,
        le=1,
    ) 


class RevealCardIn(BaseModel):
    game_uuid: UUID4 | None = None
