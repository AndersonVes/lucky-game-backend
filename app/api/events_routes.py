from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.deps import get_db
from app.db.models.user import User
from app.schemas.event_schema import ActiveEventsOut
from app.services.events_service import event_is_active, get_active_events

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=ActiveEventsOut)
def active_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        active_events = get_active_events(db, current_user)
        db.commit()

        return {"active_events": active_events}
    except HTTPException:
        db.rollback()
        raise


@router.get("/is-active/{event_slug}")
def is_event_active(
    event_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        is_active = event_is_active(db, current_user, event_slug)
        return {"is_event_active": is_active}
    except HTTPException as e:
        raise
