import asyncio
from datetime import date
from io import BytesIO
import os
from pathlib import Path
import random
import sqlite3
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("SECRET_KEY", "test-only-not-a-production-secret-123456")

from fastapi import HTTPException, UploadFile
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.datastructures import Headers

from main import app
from database.database import Base, get_db
from database.migrate import upgrade_database, HEAD
from auth.core import create_access_token
from models.user import User
from models.room import Room, Booking, PricePeriod
from routers.public_pages import room_path
from utils.availability import available_room_ids
from utils.backup import create_backup, verify_archive, restore_backup
from contextlib import closing
from utils.image_upload import read_limited_upload, save_raw_upload, save_svg_image


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add_all([User(email="admin@example.test", hashed_password="unused", is_superuser=True),
                         User(email="guest@example.test", hashed_password="unused", is_superuser=False)])
        self.room = Room(title="Семейный номер", description="Отдых у моря", max_guests=4,
                         number_of_rooms=1, title_dop="", floor=1, area=25)
        self.db.add(self.room)
        self.db.flush()
        self.db.add(PricePeriod(room_id=self.room.id, start_date=date(2030, 6, 1), end_date=date(2030, 7, 31),
                                number_of_guests=2, price=3000))
        self.db.commit()

        def session():
            yield self.db
        app.dependency_overrides[get_db] = session
        # No lifespan: these API tests use an isolated in-memory DB, never the local DB.
        self.client = TestClient(app)
        self.admin = {"Authorization": "Bearer " + create_access_token({"sub": "admin@example.test"})}
        self.guest = {"Authorization": "Bearer " + create_access_token({"sub": "guest@example.test"})}

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()
        self.engine.dispose()

    def test_admin_apis_reject_anonymous_and_non_admin(self):
        for headers, status in (({}, 401), (self.guest, 403), ({"Authorization": "Bearer invalid"}, 401)):
            for url in ("/bookings/booking-stats", "/bookings/booking-detailed-stats", "/rooms/admin/", "/bookings/admin", "/analytics/stats"):
                with self.subTest(url=url, status=status):
                    response = self.client.get(url, params={"start_date": "2030-06-01", "end_date": "2030-06-30"}, headers=headers)
                    self.assertEqual(response.status_code, status, response.text)
            self.assertEqual(self.client.post("/upload-icon", headers=headers,
                files={"file": ("icon.svg", b'<svg xmlns="http://www.w3.org/2000/svg"/>', "image/svg+xml")}).status_code, status)

    def test_admin_can_read_statistics(self):
        for url in ("/bookings/booking-stats", "/bookings/booking-detailed-stats", "/rooms/admin/"):
            response = self.client.get(url, params={"start_date": "2030-06-01", "end_date": "2030-06-30"}, headers=self.admin)
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.headers['cache-control'], 'no-store')

    def test_room_redirects_preserve_booking_dates(self):
        query = '?start=2030-06-10&end=2030-06-13&guests=2'
        for path in (f'/public-pages/room={self.room.id}', f'/public-pages/rooms/{self.room.id}-old-title'):
            response = self.client.get(path + query, follow_redirects=False)
            self.assertEqual(response.status_code, 301)
            self.assertTrue(response.headers['location'].endswith(room_path(self.room) + query))

    def test_search_detail_booking_flow_and_checkout_boundary(self):
        period = {"guests": 2, "check_in_date": "2030-06-10", "check_out_date": "2030-06-13"}
        response = self.client.post("/rooms/filter", json=period)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual([room["id"] for room in response.json()], [self.room.id])
        self.assertEqual(self.client.get(f"/rooms/{self.room.id}").status_code, 200)
        booking = {"room_id": self.room.id, "number_of_guests": 2,
                   "check_in_date": period["check_in_date"], "check_out_date": period["check_out_date"]}
        response = self.client.post("/bookings/", json=booking, headers=self.admin)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["price"], 9000)
        self.assertEqual(self.client.post("/bookings/", json=booking, headers=self.admin).status_code, 400)
        self.assertEqual(self.client.post("/rooms/filter", json=period).json(), [])
        period.update(check_in_date="2030-06-13", check_out_date="2030-06-15")
        self.assertEqual(len(self.client.post("/rooms/filter", json=period).json()), 1)

    def test_invalid_search_periods(self):
        for end, guests in (("2030-06-10", 1), ("2030-06-09", 1), ("2035-01-01", 1), ("2030-06-11", 0)):
            response = self.client.post("/rooms/filter", json={"guests": guests, "check_in_date": "2030-06-10", "check_out_date": end})
            self.assertEqual(response.status_code, 422)

    def test_search_has_fixed_query_budget(self):
        for index in range(20):
            room = Room(title=f"Room {index}", description="", max_guests=4, number_of_rooms=2)
            self.db.add(room)
            self.db.flush()
            self.db.add(PricePeriod(room_id=room.id, start_date=date(2030, 1, 1), end_date=date(2030, 12, 31), number_of_guests=2, price=2000))
        self.db.commit()
        statements = []
        def count(conn, cursor, statement, parameters, context, executemany):
            if statement.lstrip().upper().startswith("SELECT"):
                statements.append(statement)
        event.listen(self.engine, "before_cursor_execute", count)
        try:
            response = self.client.post("/rooms/filter", json={"guests": 2, "check_in_date": "2030-06-01", "check_out_date": "2030-06-30"})
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(len(response.json()), 21)
            self.assertLessEqual(len(statements), 8)
        finally:
            event.remove(self.engine, "before_cursor_execute", count)

    def test_sweep_matches_daily_count_for_random_bookings(self):
        rng = random.Random(12)
        for capacity in (1, 2, 3):
            self.room.number_of_rooms = capacity
            for _ in range(20):
                self.db.query(Booking).delete()
                intervals = []
                for _ in range(8):
                    start = rng.randint(1, 27)
                    end = rng.randint(start + 1, 30)
                    intervals.append((start, end))
                    self.db.add(Booking(room_id=self.room.id, check_in_date=date(2030, 6, start), check_out_date=date(2030, 6, end), price=1))
                self.db.flush()
                expected = all(sum(start <= day < end for start, end in intervals) < capacity for day in range(10, 20))
                self.assertEqual(bool(available_room_ids(self.db, [self.room], date(2030, 6, 10), date(2030, 6, 20))), expected)

    def test_server_metadata_and_sitemap_escape_content(self):
        self.room.title = '<script>alert("x")</script>'
        self.db.commit()
        template = '<!DOCTYPE html><html><head><title>Old</title><meta name="description" content="Old"><link rel="canonical" href="/"></head><body><div id="app"></div><script src="/js/app.js"></script></body></html>'
        with patch("routers.public_pages.load_template", return_value=template):
            response = self.client.get("/public-pages" + room_path(self.room))
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.text.count("<title>"), 1)
            self.assertNotIn('<script>alert("x")</script>', response.text)
            self.assertIn('src="/js/app.js"', response.text)
            self.assertIn('property="og:image"', response.text)
            missing = self.client.get("/public-pages/rooms/999-missing")
            self.assertEqual(missing.status_code, 404)
            self.assertIn("noindex", missing.text)
        sitemap = self.client.get("/public-pages/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertNotIn("/admin", sitemap.text)


class UploadTests(unittest.TestCase):
    def test_rejects_active_svg_and_external_references(self):
        with TemporaryDirectory() as directory:
            for svg in ('<svg onmouseover="alert(1)"/>', '<svg><script/></svg>',
                        '<svg><foreignObject/></svg>', '<svg><use href="https://evil.test/x"/></svg>',
                        '<!DOCTYPE svg [<!ENTITY a "hi">]><svg/>', '<svg><path style="fill:url(https://evil.test/x)"/></svg>'):
                with self.subTest(svg=svg), self.assertRaises(HTTPException):
                    save_svg_image(svg.encode(), Path(directory), "x.svg", "test")
            self.assertEqual(list(Path(directory).iterdir()), [])
            save_svg_image(b'<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0h4" fill="#fff"/></svg>', Path(directory), "x.svg", "test")

    def test_limited_read_and_real_image_validation(self):
        upload = UploadFile(BytesIO(b"a" * 11), filename="huge.png")
        with self.assertRaises(HTTPException) as result:
            asyncio.run(read_limited_upload(upload, max_bytes=10))
        self.assertEqual(result.exception.status_code, 413)
        self.assertTrue(upload.file.closed)
        with TemporaryDirectory() as directory:
            fake = UploadFile(BytesIO(b"<html>not an image</html>"), filename="image.png", headers=Headers({"content-type": "image/png"}))
            with self.assertRaises(HTTPException):
                asyncio.run(save_raw_upload(fake, Path(directory), "icon", {"image/png"}))
            buffer = BytesIO()
            Image.new("RGB", (10, 10)).save(buffer, "PNG")
            real = UploadFile(BytesIO(buffer.getvalue()), filename="test.html", headers=Headers({"content-type": "image/png"}))
            url = asyncio.run(save_raw_upload(real, Path(directory), "icon", {"image/png"}))
            self.assertTrue(url.endswith(".webp"))


class MigrationBackupTests(unittest.TestCase):
    def test_fresh_legacy_and_repeated_migrations_preserve_data(self):
        with TemporaryDirectory() as directory:
            database = Path(directory) / "test.db"
            engine = create_engine("sqlite:///" + database.as_posix())
            upgrade_database(engine)
            with engine.begin() as connection:
                connection.execute(text("INSERT INTO rooms (id, title) VALUES (1, 'keep me')"))
                connection.execute(text("DROP TABLE deployment_schema_version"))
                for table in ("guest_messages", "guest_reservations", "payment_settings", "guest_request_limits", "guest_tokens", "guest_sessions", "guest_profiles"):
                    connection.execute(text(f"DROP TABLE {table}"))
                connection.execute(text("ALTER TABLE room_photos DROP COLUMN sort_order"))
            upgrade_database(engine)
            upgrade_database(engine)
            with engine.connect() as connection:
                self.assertEqual(connection.execute(text("SELECT title FROM rooms WHERE id=1")).scalar(), "keep me")
                self.assertEqual(connection.execute(text("SELECT version_num FROM deployment_schema_version")).scalar(), HEAD)
            engine.dispose()
            static = Path(directory) / "static"
            static.mkdir()
            (static / "photo.txt").write_text("photo fixture")
            archive = create_backup(database, static, Path(directory) / "backups")
            verify_archive(archive)
            restored = Path(directory) / "restored"
            restore_backup(archive, restored)
            with closing(sqlite3.connect(restored / "data/database.db")) as db:
                self.assertEqual(db.execute("SELECT title FROM rooms WHERE id=1").fetchone()[0], "keep me")
            self.assertEqual((restored / "static/photo.txt").read_text(), "photo fixture")
            with self.assertRaises(ValueError):
                restore_backup(archive, restored)
            self.assertTrue(list((Path(directory) / "migration-backups").glob("*.db")))


if __name__ == "__main__":
    unittest.main()
