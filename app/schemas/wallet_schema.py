from pydantic import BaseModel, NonNegativeInt

class WalletOut(BaseModel):
    coins: NonNegativeInt
    gems: NonNegativeInt
    energy: NonNegativeInt

    class Config:
        from_attributes = True