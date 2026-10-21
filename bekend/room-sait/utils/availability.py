from collections import defaultdict
from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from models.room import Booking, CalendarSyncEvent, Room
from models.guest import GuestReservation
from utils.ical_sync import is_blocking_calendar_period


def active_holds(db):
    return db.query(GuestReservation).filter(GuestReservation.status == "awaiting_payment",
        GuestReservation.is_test.is_(False), GuestReservation.expires_at > datetime.utcnow())


def available_room_ids(db, rooms, check_in_date, check_out_date, exclude_booking_id=None, exclude_reservation_id=None):
    """Check [arrival, departure) in batches, including unexpired payment holds."""
    if check_out_date <= check_in_date or not rooms:
        return set()
    ids = [room.id for room in rooms]
    query = db.query(Booking.room_id, Booking.check_in_date, Booking.check_out_date).filter(
        Booking.room_id.in_(ids),
        Booking.check_in_date < check_out_date,
        Booking.check_out_date > check_in_date,
    )
    if exclude_booking_id is not None:
        query = query.filter(Booking.id != exclude_booking_id)

    changes = defaultdict(lambda: defaultdict(int))
    for room_id, start, end in query.all():
        changes[room_id][max(start, check_in_date)] += 1
        changes[room_id][min(end, check_out_date)] -= 1

    holds = active_holds(db).filter(GuestReservation.room_id.in_(ids),
        GuestReservation.check_in_date < check_out_date, GuestReservation.check_out_date > check_in_date)
    if exclude_reservation_id is not None:
        holds = holds.filter(GuestReservation.id != exclude_reservation_id)
    for hold in holds:
        changes[hold.room_id][max(hold.check_in_date, check_in_date)] += 1
        changes[hold.room_id][min(hold.check_out_date, check_out_date)] -= 1

    events = db.query(CalendarSyncEvent).filter(
        CalendarSyncEvent.room_id.in_(ids),
        CalendarSyncEvent.start_date < check_out_date,
        CalendarSyncEvent.end_date > check_in_date,
    ).all()
    blocked = {
        event.room_id for event in events
        if is_blocking_calendar_period(event.summary or "", event.start_date, event.end_date)
    }
    available = set()
    for room in rooms:
        if room.id in blocked:
            continue
        occupied = 0
        for day, delta in sorted(changes[room.id].items()):
            occupied += delta
            if day < check_out_date and occupied >= max(room.number_of_rooms or 1, 1):
                break
        else:
            available.add(room.id)
    return available


def is_room_available_for_period(
    db: Session,
    room: Room,
    check_in_date: date,
    check_out_date: date,
    exclude_booking_id: Optional[int] = None,
) -> bool:
    return room.id in available_room_ids(
        db, [room], check_in_date, check_out_date, exclude_booking_id
    )
