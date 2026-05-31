from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from models.room import Booking, CalendarSyncEvent, Room
from utils.ical_sync import is_blocking_calendar_period


def is_room_available_for_period(
    db: Session,
    room: Room,
    check_in_date: date,
    check_out_date: date,
    exclude_booking_id: Optional[int] = None,
) -> bool:
    units_count = max(room.number_of_rooms or 1, 1)
    current = check_in_date

    while current < check_out_date:
        next_day = current + timedelta(days=1)

        booking_query = db.query(Booking).filter(
            Booking.room_id == room.id,
            Booking.check_in_date < next_day,
            Booking.check_out_date > current,
        )
        if exclude_booking_id is not None:
            booking_query = booking_query.filter(Booking.id != exclude_booking_id)

        internal_count = booking_query.count()
        external_events = db.query(CalendarSyncEvent).filter(
            CalendarSyncEvent.room_id == room.id,
            CalendarSyncEvent.start_date < next_day,
            CalendarSyncEvent.end_date > current,
        ).all()

        has_external_block = any(
            is_blocking_calendar_period(event.summary or "", event.start_date, event.end_date)
            for event in external_events
        )

        if has_external_block or internal_count >= units_count:
            return False

        current = next_day

    return True
