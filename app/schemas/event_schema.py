from datetime import datetime
from typing import List

from pydantic import BaseModel


class ActiveEvent(BaseModel):
    slug: str
    name: str
    description: str | None = None
    
    type: str
    
    spin_currency: str
    cost_per_spin: int

    target_item_slug: str
    secondary_target_item_slug: str | None = None

    start_at: datetime | None = None
    end_at: datetime | None = None

    order_in_line: int | None = None
    progression_line_id: int | None = None

    model_config = {
        "from_attributes": True
    }



class ActiveEventsOut(BaseModel):
    active_events: List[ActiveEvent]

    model_config = {
        "from_attributes": True
    }