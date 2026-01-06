from pydantic import BaseModel, EmailStr, PositiveInt
from datetime import datetime

from app.schemas.wallet_schema import WalletOut

class UserOut(BaseModel):
    full_name: str
    email: EmailStr | None 
    locale: str | None 
    rank: PositiveInt
    created_at: datetime
    updated_at: datetime | None     
    wallet: WalletOut

    class Config:
        from_attributes = True