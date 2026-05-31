from datetime import datetime
import secrets
from typing import List
from urllib.error import URLError
from urllib.request import Request as UrlRequest, urlopen

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from auth.dependencies import check_superuser
from database.database import get_db
from models.room import Booking, CalendarSyncEvent, CalendarSyncSource, Room
from schemas.room import (
    CalendarExportLinkResponse,
    CalendarSyncEventResponse,
    CalendarSyncResult,
    CalendarSyncSourceCreate,
    CalendarSyncSourceResponse,
    CalendarSyncSourceUpdate,
)
from utils.ical_sync import ICalEvent, build_ical, is_blocking_calendar_period, parse_ical_events

router = APIRouter(tags=["calendar-sync"])


def _get_room_or_404(db: Session, room_id: int) -> Room:
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


def _generate_room_token(db: Session) -> str:
    while True:
        token = secrets.token_urlsafe(24)
        exists = db.query(Room).filter(Room.calendar_token == token).first()
        if not exists:
            return token


def _fetch_ical(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Only http/https calendar URLs are supported")

    request = UrlRequest(url, headers={"User-Agent": "VinegrapeCalendarSync/1.0"})
    try:
        with urlopen(request, timeout=20) as response:
            content_type = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(content_type, errors="replace")
    except URLError as exc:
        raise HTTPException(status_code=502, detail=f"Calendar download failed: {exc}") from exc


def _sync_source(db: Session, source: CalendarSyncSource) -> CalendarSyncResult:
    skipped_count = 0
    try:
        raw_calendar = _fetch_ical(source.url)
        events = parse_ical_events(raw_calendar)
        blocking_events = [
            event for event in events
            if is_blocking_calendar_period(event.summary, event.start_date, event.end_date)
        ]
        skipped_count = len(events) - len(blocking_events)

        db.query(CalendarSyncEvent).filter(CalendarSyncEvent.source_id == source.id).delete()
        for event in blocking_events:
            db.add(CalendarSyncEvent(
                source_id=source.id,
                room_id=source.room_id,
                uid=event.uid,
                summary=event.summary,
                start_date=event.start_date,
                end_date=event.end_date,
                imported_at=datetime.utcnow(),
            ))

        source.last_synced_at = datetime.utcnow()
        source.last_error = None
        db.commit()

        return CalendarSyncResult(
            source_id=source.id,
            imported_count=len(blocking_events),
            skipped_count=skipped_count,
        )
    except HTTPException as exc:
        db.rollback()
        source.last_error = str(exc.detail)
        db.add(source)
        db.commit()
        return CalendarSyncResult(
            source_id=source.id,
            imported_count=0,
            skipped_count=skipped_count,
            last_error=source.last_error,
        )
    except Exception as exc:
        db.rollback()
        source.last_error = f"Calendar sync failed: {exc}"
        db.add(source)
        db.commit()
        return CalendarSyncResult(
            source_id=source.id,
            imported_count=0,
            skipped_count=skipped_count,
            last_error=source.last_error,
        )


@router.get("/calendar/ical/{token}.ics", name="export_room_ical")
def export_room_ical(token: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.calendar_token == token).first()
    if not room:
        raise HTTPException(status_code=404, detail="Calendar not found")

    events: List[ICalEvent] = []
    bookings = db.query(Booking).filter(Booking.room_id == room.id).all()
    for booking in bookings:
        events.append(ICalEvent(
            uid=f"booking-{booking.id}",
            start_date=booking.check_in_date,
            end_date=booking.check_out_date,
            summary="Забронировано",
        ))

    external_events = db.query(CalendarSyncEvent).filter(CalendarSyncEvent.room_id == room.id).all()
    for event in external_events:
        if not is_blocking_calendar_period(event.summary or "", event.start_date, event.end_date):
            continue
        events.append(ICalEvent(
            uid=f"external-{event.source_id}-{event.uid}",
            start_date=event.start_date,
            end_date=event.end_date,
            summary=event.summary or "Забронировано",
        ))

    events.sort(key=lambda event: (event.start_date, event.end_date, event.uid))
    calendar = build_ical(events, calendar_name=f"{room.title} — занятость")
    return Response(content=calendar, media_type="text/calendar; charset=utf-8")


@router.get(
    "/calendar-sync/rooms/{room_id}/export-link",
    response_model=CalendarExportLinkResponse,
    dependencies=[Depends(check_superuser)],
)
def get_export_link(room_id: int, request: Request, db: Session = Depends(get_db)):
    room = _get_room_or_404(db, room_id)
    if not room.calendar_token:
        room.calendar_token = _generate_room_token(db)
        db.commit()
        db.refresh(room)

    url = str(request.url_for("export_room_ical", token=room.calendar_token))
    return CalendarExportLinkResponse(room_id=room.id, token=room.calendar_token, url=url)


@router.post(
    "/calendar-sync/rooms/{room_id}/sources",
    response_model=CalendarSyncSourceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_superuser)],
)
def create_sync_source(
    room_id: int,
    source_data: CalendarSyncSourceCreate,
    db: Session = Depends(get_db),
):
    _get_room_or_404(db, room_id)
    source = CalendarSyncSource(
        room_id=room_id,
        name=source_data.name,
        url=source_data.url,
        is_active=source_data.is_active,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get(
    "/calendar-sync/rooms/{room_id}/sources",
    response_model=List[CalendarSyncSourceResponse],
    dependencies=[Depends(check_superuser)],
)
def list_sync_sources(room_id: int, db: Session = Depends(get_db)):
    _get_room_or_404(db, room_id)
    return db.query(CalendarSyncSource).filter(CalendarSyncSource.room_id == room_id).order_by(CalendarSyncSource.id).all()


@router.patch(
    "/calendar-sync/sources/{source_id}",
    response_model=CalendarSyncSourceResponse,
    dependencies=[Depends(check_superuser)],
)
def update_sync_source(
    source_id: int,
    source_data: CalendarSyncSourceUpdate,
    db: Session = Depends(get_db),
):
    source = db.query(CalendarSyncSource).filter(CalendarSyncSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Calendar source not found")

    update_data = source_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(source, field, value)

    db.commit()
    db.refresh(source)
    return source


@router.delete(
    "/calendar-sync/sources/{source_id}",
    response_model=CalendarSyncSourceResponse,
    dependencies=[Depends(check_superuser)],
)
def delete_sync_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(CalendarSyncSource).filter(CalendarSyncSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Calendar source not found")

    db.delete(source)
    db.commit()
    return source


@router.post(
    "/calendar-sync/sources/{source_id}/sync",
    response_model=CalendarSyncResult,
    dependencies=[Depends(check_superuser)],
)
def sync_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(CalendarSyncSource).filter(CalendarSyncSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Calendar source not found")
    return _sync_source(db, source)


@router.post(
    "/calendar-sync/rooms/{room_id}/sync-all",
    response_model=List[CalendarSyncResult],
    dependencies=[Depends(check_superuser)],
)
def sync_room_sources(room_id: int, db: Session = Depends(get_db)):
    _get_room_or_404(db, room_id)
    sources = db.query(CalendarSyncSource).filter(
        CalendarSyncSource.room_id == room_id,
        CalendarSyncSource.is_active == True,
    ).order_by(CalendarSyncSource.id).all()
    return [_sync_source(db, source) for source in sources]


@router.get(
    "/calendar-sync/rooms/{room_id}/events",
    response_model=List[CalendarSyncEventResponse],
    dependencies=[Depends(check_superuser)],
)
def list_imported_events(room_id: int, db: Session = Depends(get_db)):
    _get_room_or_404(db, room_id)
    events = db.query(CalendarSyncEvent).filter(
        CalendarSyncEvent.room_id == room_id
    ).order_by(CalendarSyncEvent.start_date, CalendarSyncEvent.id).all()
    return [
        event for event in events
        if is_blocking_calendar_period(event.summary or "", event.start_date, event.end_date)
    ]
