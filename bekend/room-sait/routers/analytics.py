from datetime import date, datetime, time, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from auth.dependencies import check_superuser
from database.database import get_db
from models.room import Room, SiteEvent

router = APIRouter(prefix="/analytics", tags=["analytics"])

EVENT_TYPES = {"room_click", "booking_click", "phone_click"}


class EventCreate(BaseModel):
    event_type: str
    room_id: Optional[int] = None
    path: Optional[str] = None


def _date_bounds(start_date: date, end_date: date):
    start_dt = datetime.combine(start_date, time.min)
    end_dt = datetime.combine(end_date + timedelta(days=1), time.min)
    return start_dt, end_dt


@router.post("/events")
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    if event.event_type not in EVENT_TYPES:
        return {"ok": False}

    db_event = SiteEvent(
        event_type=event.event_type,
        room_id=event.room_id,
        path=(event.path or "")[:300],
    )
    db.add(db_event)
    db.commit()
    return {"ok": True}


@router.get("/stats", dependencies=[Depends(check_superuser)])
def get_analytics_stats(
    start_date: date,
    end_date: date,
    room_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    start_dt, end_dt = _date_bounds(start_date, end_date)

    query = db.query(SiteEvent).filter(
        and_(
            SiteEvent.created_at >= start_dt,
            SiteEvent.created_at < end_dt,
        )
    )
    if room_id is not None:
        query = query.filter(SiteEvent.room_id == room_id)

    events = query.all()

    totals = {
        "room_click": 0,
        "booking_click": 0,
        "phone_click": 0,
    }
    for event in events:
        if event.event_type in totals:
            totals[event.event_type] += 1

    daily_rows = db.query(
        func.date(SiteEvent.created_at).label("day"),
        SiteEvent.event_type,
        func.count(SiteEvent.id).label("count"),
    ).filter(
        and_(
            SiteEvent.created_at >= start_dt,
            SiteEvent.created_at < end_dt,
        )
    )
    if room_id is not None:
        daily_rows = daily_rows.filter(SiteEvent.room_id == room_id)
    daily_rows = daily_rows.group_by(func.date(SiteEvent.created_at), SiteEvent.event_type).all()

    daily_map = {}
    current = start_date
    while current <= end_date:
        daily_map[current.isoformat()] = {
            "date": current.isoformat(),
            "room_click": 0,
            "booking_click": 0,
            "phone_click": 0,
        }
        current += timedelta(days=1)

    for row in daily_rows:
        if row.day in daily_map and row.event_type in totals:
            daily_map[row.day][row.event_type] = row.count

    room_stats = []
    if room_id is None:
        rooms = db.query(Room).order_by(Room.id).all()
        events_by_room = {
            room.id: {
                "room_click": 0,
                "booking_click": 0,
                "phone_click": 0,
            }
            for room in rooms
        }
        for event in events:
            if event.room_id in events_by_room and event.event_type in totals:
                events_by_room[event.room_id][event.event_type] += 1

        for room in rooms:
            stats = events_by_room[room.id]
            room_stats.append({
                "room_id": room.id,
                "room_title": room.title,
                "room_clicks": stats["room_click"],
                "booking_clicks": stats["booking_click"],
                "phone_clicks": stats["phone_click"],
            })

    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "totals": {
            "room_clicks": totals["room_click"],
            "booking_clicks": totals["booking_click"],
            "phone_clicks": totals["phone_click"],
        },
        "daily": list(daily_map.values()),
        "room_statistics": room_stats if room_id is None else None,
    }
