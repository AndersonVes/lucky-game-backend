from collections import defaultdict

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.models.user import User
from app.helpers.time_helper import utcnow
from app.db.models import Event, UserEvent


def event_is_active(
    db: Session,
    user: User,
    event_or_slug: Event | str,
) -> bool:

    now = utcnow()

    if isinstance(event_or_slug, str):
        event = db.query(Event).filter(Event.slug == event_or_slug).first()

    else:
        event = event_or_slug

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.type == "seasonal":

        if not (event.start_at <= now <= event.end_at):
            return False

        user_event = (
            db.query(UserEvent)
            .filter(
                UserEvent.user_id == user.id,
                UserEvent.event_id == event.id,
            )
            .first()
        )

        if user_event and user_event.finished_at is not None:
            return False

        return True

    if event.type == "progression":

        line_events = (
            db.query(Event)
            .filter(Event.progression_line_id == event.progression_line_id)
            .order_by(Event.order_in_line.asc())
            .all()
        )

        event_ids = [e.id for e in line_events]

        user_events = (
            db.query(UserEvent)
            .filter(
                UserEvent.user_id == user.id,
                UserEvent.event_id.in_(event_ids),
            )
            .all()
        )

        finished_map = {ue.event_id: ue.finished_at for ue in user_events}

        for e in line_events:
            finished_at = finished_map.get(e.id)

            if finished_at is None:
                return e.id == event.id

        return False

    return False


def get_active_events(db: Session, user: User) -> list[Event]:
    now = utcnow()

    seasonal_events = (
        db.query(Event)
        .filter(
            Event.type == "seasonal",
            Event.start_at <= now,
            Event.end_at >= now,
        )
        .all()
    )

    progression_events = (
        db.query(Event)
        .filter(Event.type == "progression")
        .order_by(Event.progression_line_id, Event.order_in_line)
        .all()
    )

    user_events = (
        db.query(UserEvent)
        .filter(UserEvent.user_id == user.id)
        .all()
    )

    user_event_map = {ue.event_id: ue for ue in user_events}
    active_events = []

    
    
    

    for event in seasonal_events:
        ue = user_event_map.get(event.id)

        if ue and ue.finished_at is not None:
            continue

        active_events.append(event)

        if ue is None:
            new_ue = UserEvent(
                user_id=user.id,
                event_id=event.id,
            )
            db.add(new_ue)

            
            user_event_map[event.id] = new_ue

    
    
    

    progression_by_line = defaultdict(list)

    for event in progression_events:
        progression_by_line[event.progression_line_id].append(event)

    for line_id, events in progression_by_line.items():

        for event in events:
            ue = user_event_map.get(event.id)

            if ue is None or ue.finished_at is None:
                active_events.append(event)

                if ue is None:
                    new_ue = UserEvent(
                        user_id=user.id,
                        event_id=event.id,
                    )
                    db.add(new_ue)
                    user_event_map[event.id] = new_ue

                break

    db.flush()  

    return active_events

