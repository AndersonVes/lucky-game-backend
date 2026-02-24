from pydantic import BaseModel


class UserHasItemOut(BaseModel):
    hasItem: bool