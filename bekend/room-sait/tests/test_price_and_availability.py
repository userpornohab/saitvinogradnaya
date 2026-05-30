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
from models.room import Booking, PricePeriod, Room
from routers.rooms import filter_rooms
from schemas.room import RoomFilter
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


if __name__ == "__main__":
    unittest.main()
