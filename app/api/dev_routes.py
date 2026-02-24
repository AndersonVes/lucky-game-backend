import os

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.config import settings
from app.helpers.time_helper import dev_add_seconds


def dev_only():
    env_mode = settings.ENV
    if env_mode != "DEV": #TODO colocar isso em login dev
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not allowed. only dev"+" "+env_mode,
        )

router = APIRouter(
    prefix="/dev",
    tags=["dev"],
    dependencies=[Depends(dev_only)]
)
@router.post("/add-seconds")
async def add_seconds(request: Request):
    body = await request.json()
    seconds = body.get("seconds")

    if seconds is None:
        raise HTTPException(status_code=400, detail="minutes is required")

    dev_add_seconds(int(seconds))

    return {"ok": True, "added_seconds": int(seconds)}
    

