import sys
import unittest
from datetime import date
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from database.database import Base
from models.room import Booking, CalendarSyncEvent, CalendarSyncSource, PricePeriod, Room
from routers.rooms import filter_rooms
from schemas.room import RoomFilter
from utils.availability import is_room_available_for_period
from utils.ical_sync import build_ical, collapse_busy_days, is_blocking_calendar_period, parse_ical_events
from utils.price_calculator import calculate_booking_price


class BookingRulesTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=engine)
        self.Session = sessionmaker(bind=engine)
        self.db = self.Session()

        self.room = Room(
            title="Семейный номер",
            description="Тестовый номер",
            max_guests=4,
            number_of_rooms=1,
            title_dop="",
            floor=1,
            area=25,
        )
        self.db.add(self.room)
        self.db.commit()
        self.db.refresh(self.room)

    def tearDown(self):
        self.db.close()

    def add_price(self, start, end, guests, price):
        self.db.add(PricePeriod(
            room_id=self.room.id,
            start_date=start,
            end_date=end,
            number_of_guests=guests,
            price=price,
        ))
        self.db.commit()

    def test_calculates_price_by_nights_and_guest_count(self):
        self.add_price(date(2026, 6, 1), date(2026, 6, 10), 2, 3000)

        price = calculate_booking_price(
            room_id=self.room.id,
            check_in=date(2026, 6, 1),
            check_out=date(2026, 6, 4),
            number_of_guests=2,
            db=self.db,
        )

        self.assertEqual(price, 9000)

    def test_uses_nearest_higher_guest_price_when_exact_missing(self):
        self.add_price(date(2026, 6, 1), date(2026, 6, 10), 4, 4500)

        price = calculate_booking_price(
            room_id=self.room.id,
            check_in=date(2026, 6, 2),
            check_out=date(2026, 6, 4),
            number_of_guests=3,
            db=self.db,
        )

        self.assertEqual(price, 9000)

    def test_filter_excludes_room_when_all_units_are_booked(self):
        self.add_price(date(2026, 6, 1), date(2026, 6, 10), 2, 3000)
        self.db.add(Booking(
            room_id=self.room.id,
            check_in_date=date(2026, 6, 3),
            check_out_date=date(2026, 6, 5),
            number_of_guests=2,
            price=6000,
        ))
        self.db.commit()

        rooms = filter_rooms(
            RoomFilter(
                guests=2,
                check_in_date=date(2026, 6, 4),
                check_out_date=date(2026, 6, 6),
            ),
            db=self.db,
        )

        self.assertEqual(rooms, [])

    def test_filter_allows_room_when_dates_do_not_overlap(self):
        self.add_price(date(2026, 6, 1), date(2026, 6, 10), 2, 3000)
        self.db.add(Booking(
            room_id=self.room.id,
            check_in_date=date(2026, 6, 1),
            check_out_date=date(2026, 6, 3),
            number_of_guests=2,
            price=6000,
        ))
        self.db.commit()

        rooms = filter_rooms(
            RoomFilter(
                guests=2,
                check_in_date=date(2026, 6, 3),
                check_out_date=date(2026, 6, 5),
            ),
            db=self.db,
        )

        self.assertEqual([room.id for room in rooms], [self.room.id])

    def test_filter_excludes_room_when_external_calendar_blocks_dates(self):
        self.add_price(date(2026, 6, 1), date(2026, 6, 10), 2, 3000)
        source = CalendarSyncSource(
            room_id=self.room.id,
            name="Суточно",
            url="https://example.com/calendar.ics",
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        self.db.add(CalendarSyncEvent(
            source_id=source.id,
            room_id=self.room.id,
            uid="external-1",
            summary="Забронировано",
            start_date=date(2026, 6, 3),
            end_date=date(2026, 6, 5),
        ))
        self.db.commit()

        rooms = filter_rooms(
            RoomFilter(
                guests=2,
                check_in_date=date(2026, 6, 4),
                check_out_date=date(2026, 6, 6),
            ),
            db=self.db,
        )

        self.assertEqual(rooms, [])

    def test_external_calendar_event_blocks_whole_multi_unit_category(self):
        self.room.number_of_rooms = 2
        self.add_price(date(2026, 6, 1), date(2026, 6, 10), 2, 3000)
        source = CalendarSyncSource(
            room_id=self.room.id,
            name="Суточно",
            url="https://example.com/calendar.ics",
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        self.db.add(CalendarSyncEvent(
            source_id=source.id,
            room_id=self.room.id,
            uid="external-1",
            summary="Забронировано",
            start_date=date(2026, 6, 3),
            end_date=date(2026, 6, 5),
        ))
        self.db.commit()

        self.assertFalse(is_room_available_for_period(
            self.db,
            self.room,
            date(2026, 6, 4),
            date(2026, 6, 6),
        ))

    def test_external_calendar_placeholder_does_not_block_dates(self):
        self.room.number_of_rooms = 2
        source = CalendarSyncSource(
            room_id=self.room.id,
            name="Суточно",
            url="https://example.com/calendar.ics",
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        self.db.add(CalendarSyncEvent(
            source_id=source.id,
            room_id=self.room.id,
            uid="external-placeholder",
            summary="Недоступно",
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 10),
        ))
        self.db.commit()

        self.assertTrue(is_room_available_for_period(
            self.db,
            self.room,
            date(2026, 10, 2),
            date(2026, 10, 4),
        ))

    def test_long_external_calendar_event_does_not_block_dates(self):
        self.assertFalse(is_blocking_calendar_period(
            "Забронировано",
            date(2026, 10, 1),
            date(2026, 12, 15),
        ))

    def test_availability_uses_per_day_capacity_for_multi_unit_rooms(self):
        self.room.number_of_rooms = 2
        self.db.add(self.room)
        self.db.add(Booking(
            room_id=self.room.id,
            check_in_date=date(2026, 6, 1),
            check_out_date=date(2026, 6, 3),
            number_of_guests=2,
            price=6000,
        ))
        self.db.add(Booking(
            room_id=self.room.id,
            check_in_date=date(2026, 6, 3),
            check_out_date=date(2026, 6, 5),
            number_of_guests=2,
            price=6000,
        ))
        self.db.commit()

        self.assertTrue(is_room_available_for_period(
            self.db,
            self.room,
            date(2026, 6, 1),
            date(2026, 6, 5),
        ))

    def test_ical_parser_reads_sutochno_style_events(self):
        raw_calendar = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:test-1
DTSTART:20260801T140000
DTEND:20260918T120000
SUMMARY:Забронировано
END:VEVENT
END:VCALENDAR
"""

        events = parse_ical_events(raw_calendar)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].uid, "test-1")
        self.assertEqual(events[0].start_date, date(2026, 8, 1))
        self.assertEqual(events[0].end_date, date(2026, 9, 18))

    def test_ical_export_marks_only_fully_busy_days_for_multi_unit_room(self):
        events = [
            CalendarSyncEvent(
                source_id=1,
                room_id=self.room.id,
                uid="external-1",
                summary="Забронировано",
                start_date=date(2026, 6, 1),
                end_date=date(2026, 6, 4),
            ),
            CalendarSyncEvent(
                source_id=1,
                room_id=self.room.id,
                uid="external-2",
                summary="Забронировано",
                start_date=date(2026, 6, 2),
                end_date=date(2026, 6, 3),
            ),
        ]

        collapsed = collapse_busy_days(events, units_count=2)
        calendar = build_ical(collapsed)

        self.assertEqual(len(collapsed), 1)
        self.assertEqual(collapsed[0].start_date, date(2026, 6, 2))
        self.assertEqual(collapsed[0].end_date, date(2026, 6, 3))
        self.assertIn("DTSTART;VALUE=DATE:20260602", calendar)
        self.assertIn("DTEND;VALUE=DATE:20260603", calendar)


if __name__ == "__main__":
    unittest.main()
