"""Isolated payment/account regression tests. No SMTP, Robokassa or live DB calls."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.parse import quote
from uuid import uuid4

os.environ.setdefault("SECRET_KEY", "test-only-not-production-1234567890")
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from config import settings
from database.database import Base, get_db
from auth.core import get_password_hash, create_access_token
from models.user import User
from models.room import Room, PricePeriod, Booking
from models.guest import GuestProfile, GuestReservation, GuestToken, GuestSession, PaymentSettings
from utils.guest_security import COOKIE, digest
from utils.robokassa import payment_parameters, receipt_for

PASSWORD = "a-strong-test-password-123"
PASSWORD_HASH = get_password_hash(PASSWORD)
ORIGIN = "http://testserver"


class GuestPaymentTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.engine = create_engine("sqlite:///" + (Path(self.directory.name) / "test.db").as_posix(),
                                    connect_args={"check_same_thread": False, "timeout": 15})
        Base.metadata.create_all(self.engine)
        self.factory = sessionmaker(bind=self.engine, autoflush=False)
        self.db = self.factory()
        self.override = patch.multiple(settings, GUEST_COOKIE_SECURE=False, GUEST_ALLOWED_ORIGINS=ORIGIN,
            PUBLIC_SITE_URL="https://vinegrape.ru", SMTP_HOST="smtp.example.test", SMTP_FROM="test@example.test",
            ROBOKASSA_IS_TEST=False, ROBOKASSA_MERCHANT_LOGIN="test-merchant", ROBOKASSA_HASH="sha256",
            ROBOKASSA_PASSWORD1="live-one", ROBOKASSA_PASSWORD2="live-two",
            ROBOKASSA_TEST_PASSWORD1="test-one", ROBOKASSA_TEST_PASSWORD2="test-two",
            ROBOKASSA_RECEIPT_ENABLED=True, ROBOKASSA_TAX="none", ROBOKASSA_SNO="")
        self.override.start()
        # Live configuration validation normally requires secure cookies. Tests override only readiness.
        self.ready = patch("routers.guest_bookings.readiness", return_value=[])
        self.ready.start()
        self.mail = patch("utils.guest_security.send_account_email").start()
        self.db.add_all([User(id=1, email="guest@example.com", name="Гость", hashed_password=PASSWORD_HASH, is_superuser=False),
                         User(id=2, email="other@example.com", name="Другой гость", hashed_password=PASSWORD_HASH, is_superuser=False),
                         User(id=3, email="admin@example.com", name="Админ", hashed_password=PASSWORD_HASH, is_superuser=True)])
        self.db.add_all([GuestProfile(user_id=1, phone="+79990000001", email_verified=True), GuestProfile(user_id=2, phone="", email_verified=True)])
        self.db.add(Room(id=1, title="Семейный номер", description="", number_of_rooms=1, max_guests=4))
        self.db.add(PricePeriod(room_id=1, start_date=date(2030, 6, 1), end_date=date(2030, 8, 31), price=3000, number_of_guests=4))
        self.db.add(PaymentSettings(id=1, enabled=True, deposit_mode="first_night", deposit_percent=30, hold_minutes=20,
                                    terms_url="/terms", privacy_url="/privacy", terms_version="1"))
        self.db.commit()
        def session():
            with self.factory() as db:
                yield db
        app.dependency_overrides[get_db] = session
        self.client = TestClient(app)
        self.headers = {"Origin": ORIGIN}
        self.login()
        self.admin = {"Authorization": "Bearer " + create_access_token({"sub": "admin@example.com"})}
        self.period = {"room_id": 1, "check_in_date": "2030-06-10", "check_out_date": "2030-06-13", "guests": 2}

    def tearDown(self):
        self.client.close()
        self.db.close()
        app.dependency_overrides.clear()
        self.engine.dispose()
        patch.stopall()
        self.directory.cleanup()

    def login(self, email="guest@example.com", password=PASSWORD):
        response = self.client.post("/guest/auth/login", json={"email": email, "password": password}, headers={"Origin": ORIGIN})
        self.assertEqual(response.status_code, 200, response.text)
        self.headers = {"Origin": ORIGIN, "X-CSRF-Token": response.json()["csrf"]}
        return response

    def reserve(self, **updates):
        request = {**self.period, "guest_name": "Гость", "guest_phone": "+79990000001", "request_key": uuid4().hex,
                   "accepted_terms": True, "terms_version": "1", "quoted_total_kopeks": 900000, "quoted_deposit_kopeks": 300000}
        request.update(updates)
        return self.client.post("/guest/reservations", json=request, headers=self.headers)

    def pay(self, invoice, amount="3000.000000", test=False, **extra):
        raw = f"{amount}:{invoice}:{'test-two' if test else 'live-two'}"
        fields = {"OutSum": amount, "InvId": str(invoice), "SignatureValue": hashlib.sha256(raw.encode()).hexdigest(), **extra}
        return self.client.post("/payments/robokassa/result" + ("/test" if test else ""), data=fields)

    def test_registration_verification_is_single_use_and_cannot_set_admin(self):
        response = self.client.post("/guest/auth/register", headers=self.headers,
            json={"email": "new@example.com", "name": "Новый гость", "password": PASSWORD, "is_superuser": True})
        self.assertEqual(response.status_code, 422)
        response = self.client.post("/guest/auth/register", headers=self.headers,
            json={"email": "new@example.com", "name": "Новый гость", "password": PASSWORD})
        self.assertEqual(response.status_code, 200, response.text)
        token = self.mail.call_args.args[1]
        self.assertNotIn(token, response.text)
        self.login("new@example.com")
        self.assertEqual(self.reserve().status_code, 403)
        verified = self.client.post("/guest/auth/verify", json={"token": token}, headers=self.headers)
        self.assertEqual(verified.status_code, 200, verified.text)
        self.assertEqual(self.client.post("/guest/auth/verify", json={"token": token}, headers=self.headers).status_code, 400)
        self.assertEqual(self.reserve().status_code, 200)
        self.assertFalse(self.db.query(User).filter_by(email="new@example.com").one().is_superuser)

    def test_cookie_csrf_and_admin_boundaries(self):
        response = self.login()
        self.assertIn("HttpOnly", response.headers["set-cookie"])
        self.assertIn("SameSite=lax", response.headers["set-cookie"])
        self.assertNotIn("access_token", response.text)
        self.assertEqual(self.client.post("/guest/quote", json=self.period).status_code, 403)
        self.assertEqual(self.client.post("/guest/quote", json=self.period, headers={**self.headers, "Origin": "https://evil.test"}).status_code, 403)
        self.assertEqual(self.client.get("/guest-admin/reservations").status_code, 401)
        self.assertEqual(self.client.get("/guest/auth/session").headers["cache-control"], "no-store")
        self.client.post("/guest/auth/logout", headers=self.headers)
        self.assertEqual(self.client.get("/guest/auth/session").status_code, 401)

    def test_reset_revokes_sessions_and_token(self):
        self.client.post("/guest/auth/forgot", json={"email": "guest@example.com"}, headers=self.headers)
        token = self.mail.call_args.args[1]
        response = self.client.post("/guest/auth/reset", json={"token": token, "password": PASSWORD + "new"}, headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.client.get("/guest/auth/session").status_code, 401)
        self.assertEqual(self.client.post("/guest/auth/reset", json={"token": token, "password": PASSWORD}, headers=self.headers).status_code, 400)
        self.login(password=PASSWORD + "new")

    def test_quote_percent_and_first_night(self):
        response = self.client.post("/guest/quote", json=self.period, headers=self.headers)
        self.assertEqual(response.json()["deposit_kopeks"], 300000)
        policy = self.db.get(PaymentSettings, 1)
        policy.deposit_mode = "percent"; policy.deposit_percent = 25
        self.db.commit()
        response = self.client.post("/guest/quote", json=self.period, headers=self.headers)
        self.assertEqual(response.json()["deposit_kopeks"], 225000)
        self.assertEqual(self.reserve().status_code, 409)

    def test_duplicate_unverified_registration_requires_new_password(self):
        payload = {"email": "new@example.com", "name": "New guest", "password": PASSWORD}
        self.assertEqual(self.client.post("/guest/auth/register", json=payload, headers=self.headers).status_code, 200)
        old_verification = self.mail.call_args.args[1]
        self.login("new@example.com")
        replacement = "  different-strong-password  "
        self.assertEqual(self.client.post("/guest/auth/register", json={**payload, "password": replacement}, headers=self.headers).status_code, 200)
        token = self.mail.call_args.args[1]
        self.assertEqual(self.mail.call_args.args[2], "reset")
        response = self.client.post("/guest/auth/reset", json={"token": token, "password": replacement}, headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.client.get("/guest/auth/session").status_code, 401)
        self.assertEqual(self.client.post("/guest/auth/verify", json={"token": old_verification}, headers=self.headers).status_code, 400)
        self.assertEqual(self.client.post("/guest/auth/login", json={"email": payload["email"], "password": PASSWORD}, headers=self.headers).status_code, 401)
        self.assertEqual(self.client.post("/guest/auth/login", json={"email": payload["email"], "password": replacement.strip()}, headers=self.headers).status_code, 401)
        self.assertTrue(self.login(payload["email"], replacement).json()["user"]["email_verified"])

    def test_reservation_idempotency_frozen_prices_and_hold(self):
        key = uuid4().hex
        response = self.reserve(request_key=key)
        self.assertEqual(response.status_code, 200, response.text)
        row = response.json()
        self.assertEqual(self.reserve(request_key=key).json()["id"], row["id"])
        self.assertEqual(self.reserve().status_code, 409)
        self.assertEqual(self.db.query(GuestReservation).count(), 1)
        self.assertEqual(self.db.query(Booking).count(), 0)
        policy = self.db.get(PaymentSettings, 1); policy.deposit_mode = "percent"; policy.deposit_percent = 50; self.db.commit()
        response = self.client.post(f"/guest/reservations/{row['id']}/payment", headers=self.headers)
        self.assertEqual(response.json()["params"]["OutSum"], "3000.00")
        self.assertNotIn("live-one", response.text)
        self.assertNotIn("live-two", response.text)
        busy = self.client.get("/bookings/rooms/1").json()
        self.assertEqual(len(busy), 1)
        self.assertNotIn("guest_name", busy[0])

    def test_valid_callback_is_idempotent_and_enables_private_chat(self):
        invoice = self.reserve().json()["id"]
        self.assertEqual(self.client.get(f"/guest/reservations/{invoice}/messages").status_code, 403)
        response = self.pay(invoice)
        self.assertEqual(response.text, f"OK{invoice}")
        self.assertEqual(self.pay(invoice).text, f"OK{invoice}")
        self.assertEqual(self.db.query(Booking).count(), 1)
        row = self.client.get(f"/guest/reservations/{invoice}").json()
        self.assertEqual(row["status"], "confirmed")
        self.assertEqual(row["remaining_kopeks"], 600000)
        key = uuid4().hex
        payload = {"body": "<script>alert('x')</script>", "request_key": key}
        for _ in range(2):
            self.assertEqual(self.client.post(f"/guest/reservations/{invoice}/messages", json=payload, headers=self.headers).status_code, 200)
        self.assertEqual(len(self.client.get(f"/guest/reservations/{invoice}/messages").json()), 1)
        self.assertEqual(self.client.post(f"/guest-admin/reservations/{invoice}/messages", json={"body": "Ждём вас!", "request_key": uuid4().hex}, headers=self.admin).status_code, 200)
        self.login("other@example.com")
        for path in (f"/guest/reservations/{invoice}", f"/guest/reservations/{invoice}/messages"):
            self.assertEqual(self.client.get(path).status_code, 404)
        self.assertEqual(self.client.post(f"/guest/reservations/{invoice}/payment", headers=self.headers).status_code, 404)

    def test_bad_signatures_amounts_environment_and_duplicates_do_not_confirm(self):
        invoice = self.reserve().json()["id"]
        self.assertEqual(self.pay(invoice, SignatureValue="0" * 64).status_code, 403)
        self.assertEqual(self.pay(invoice, amount="1.00").status_code, 400)
        self.assertEqual(self.pay(invoice, test=True).status_code, 400)
        self.assertEqual(self.pay(invoice, Shp_user="fake").status_code, 400)
        self.assertEqual(self.client.post("/payments/robokassa/result", content="OutSum=3000&OutSum=1&InvId=1", headers={"Content-Type": "application/x-www-form-urlencoded"}).status_code, 400)
        self.assertEqual(self.db.query(Booking).count(), 0)
        self.assertEqual(self.client.get(f"/guest/reservations/{invoice}").json()["status"], "awaiting_payment")

    def test_late_payment_does_not_overbook(self):
        invoice = self.reserve().json()["id"]
        row = self.db.get(GuestReservation, invoice); row.expires_at = datetime.utcnow() - timedelta(minutes=1); self.db.commit()
        manual = self.client.post("/bookings/", json={"room_id": 1, "check_in_date": "2030-06-10", "check_out_date": "2030-06-13", "number_of_guests": 2}, headers=self.admin)
        self.assertEqual(manual.status_code, 200, manual.text)
        self.assertEqual(self.pay(invoice).status_code, 200)
        self.assertEqual(self.client.get(f"/guest/reservations/{invoice}").json()["status"], "payment_review")
        self.assertEqual(self.db.query(Booking).count(), 1)

    def test_shared_callback_passwords_and_non_hex_signature_are_rejected(self):
        invoice = self.reserve().json()["id"]
        self.assertEqual(self.pay(invoice, SignatureValue="неподписано").status_code, 403)
        with patch.object(settings, "ROBOKASSA_TEST_PASSWORD2", "live-two"):
            self.assertEqual(self.pay(invoice).status_code, 503)
        self.assertEqual(self.db.query(Booking).count(), 0)

    def test_late_payment_can_confirm_if_still_free(self):
        invoice = self.reserve().json()["id"]
        row = self.db.get(GuestReservation, invoice); row.expires_at = datetime.utcnow() - timedelta(minutes=1); self.db.commit()
        self.assertEqual(self.pay(invoice).status_code, 200)
        self.assertEqual(self.client.get(f"/guest/reservations/{invoice}").json()["status"], "confirmed")

    def test_cancelled_invoice_late_payment_requires_review(self):
        invoice = self.reserve().json()["id"]
        self.client.post(f"/guest/reservations/{invoice}/cancel", headers=self.headers)
        self.pay(invoice)
        self.assertEqual(self.client.get(f"/guest/reservations/{invoice}").json()["status"], "payment_review")
        self.assertEqual(self.db.query(Booking).count(), 0)

    def test_test_payment_never_creates_live_booking(self):
        with patch.object(settings, "ROBOKASSA_IS_TEST", True):
            invoice = self.reserve().json()["id"]
        self.assertEqual(self.client.get("/bookings/rooms/1").json(), [])
        self.assertEqual(self.pay(invoice).status_code, 400)
        self.assertEqual(self.pay(invoice, test=True).status_code, 200)
        self.assertEqual(self.client.get(f"/guest/reservations/{invoice}").json()["status"], "test_paid")
        self.assertEqual(self.db.query(Booking).count(), 0)

    def test_paid_booking_cannot_be_deleted_or_repriced_through_legacy_api(self):
        invoice = self.reserve().json()["id"]; self.pay(invoice)
        booking = self.db.query(Booking).one()
        self.assertEqual(self.client.delete(f"/bookings/{booking.id}", headers=self.admin).status_code, 409)
        self.assertEqual(self.client.delete("/rooms/1", headers=self.admin).status_code, 409)
        manual = self.client.post("/bookings/", json={"room_id": 1, "check_in_date": "2030-06-10", "check_out_date": "2030-06-13", "number_of_guests": 2}, headers=self.admin)
        self.assertEqual(manual.status_code, 400)

    def test_cancellation_and_manual_refund_record_keep_payment_history(self):
        invoice = self.reserve().json()["id"]; self.pay(invoice)
        response = self.client.post(f"/guest/reservations/{invoice}/cancel", headers=self.headers)
        self.assertEqual(response.json()["status"], "cancel_requested")
        self.assertEqual(self.db.query(Booking).count(), 1)
        response = self.client.post(f"/guest-admin/reservations/{invoice}/refund-record", json={"reference": "provider-refund-123"}, headers=self.admin)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["status"], "refunded")
        self.assertEqual(self.db.query(Booking).count(), 0)
        self.assertEqual(self.pay(invoice).text, f"OK{invoice}")
        self.assertEqual(self.db.query(Booking).count(), 0)

    def test_receipt_encoded_once_before_signing_and_contains_prepayment(self):
        invoice = self.reserve().json()["id"]
        row = self.db.get(GuestReservation, invoice)
        params = payment_parameters(row)["params"]
        encoded = quote(row.receipt_json, safe="")
        self.assertEqual(params["Receipt"], encoded)
        expected = hashlib.sha256(f"test-merchant:3000.00:{invoice}:{encoded}:live-one".encode()).hexdigest()
        self.assertEqual(params["SignatureValue"], expected)
        self.assertEqual(json.loads(row.receipt_json)["items"][0]["payment_method"], "prepayment")

    def test_concurrent_guests_cannot_hold_last_room_twice(self):
        cookie = self.client.cookies.get(COOKIE)
        headers = dict(self.headers)
        def create(index):
            with TestClient(app) as client:
                client.cookies.set(COOKIE, cookie, path="/guest")
                body = {**self.period, "guest_name": "Гость", "guest_phone": "+79990000001", "request_key": uuid4().hex,
                    "accepted_terms": True, "terms_version": "1", "quoted_total_kopeks": 900000, "quoted_deposit_kopeks": 300000}
                return client.post("/guest/reservations", json=body, headers=headers).status_code
        # Do not enter TestClient lifespan: it would target the application's configured DB.
        with patch("main.upgrade_database"):
            with ThreadPoolExecutor(max_workers=2) as pool:
                statuses = list(pool.map(create, [1, 2]))
        self.assertEqual(sorted(statuses), [200, 409])
        self.assertEqual(self.db.query(GuestReservation).count(), 1)


if __name__ == "__main__":
    unittest.main()
