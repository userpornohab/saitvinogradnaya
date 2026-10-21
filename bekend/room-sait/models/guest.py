from datetime import datetime
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from database.database import Base


class GuestProfile(Base):
    __tablename__ = "guest_profiles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    phone = Column(String(25), nullable=False, default="")
    email_verified = Column(Boolean, nullable=False, default=False)


class GuestSession(Base):
    __tablename__ = "guest_sessions"
    token_hash = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)


class GuestToken(Base):
    __tablename__ = "guest_tokens"
    token_hash = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    purpose = Column(String(16), nullable=False)
    expires_at = Column(DateTime, nullable=False)


class RequestLimit(Base):
    __tablename__ = "guest_request_limits"
    key = Column(String(64), primary_key=True)
    count = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)


class PaymentSettings(Base):
    __tablename__ = "payment_settings"
    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean, nullable=False, default=False)
    deposit_mode = Column(String(16), nullable=False, default="first_night")
    deposit_percent = Column(Integer, nullable=False, default=30)
    hold_minutes = Column(Integer, nullable=False, default=20)
    terms_url = Column(String(500), nullable=False, default="")
    privacy_url = Column(String(500), nullable=False, default="")
    terms_version = Column(String(50), nullable=False, default="1")


class GuestReservation(Base):
    __tablename__ = "guest_reservations"
    __table_args__ = (UniqueConstraint("user_id", "request_key"),
                     Index("ix_guest_reservation_capacity", "room_id", "status", "expires_at"),
                     {"sqlite_autoincrement": True})
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True, unique=True)
    room_title = Column(String(100), nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    guests = Column(Integer, nullable=False)
    guest_name = Column(String(100), nullable=False)
    guest_phone = Column(String(25), nullable=False)
    email = Column(String(255), nullable=False)
    total_kopeks = Column(Integer, nullable=False)
    deposit_kopeks = Column(Integer, nullable=False)
    deposit_rule = Column(String(40), nullable=False)
    paid_kopeks = Column(Integer, nullable=False, default=0)
    status = Column(String(24), nullable=False, default="awaiting_payment")
    is_test = Column(Boolean, nullable=False)
    request_key = Column(String(64), nullable=False)
    terms_version = Column(String(50), nullable=False)
    terms_url = Column(String(500), nullable=False)
    receipt_json = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    refund_reference = Column(String(200), nullable=True)
    refund_admin_id = Column(Integer, nullable=True)
    refunded_at = Column(DateTime, nullable=True)


class GuestMessage(Base):
    __tablename__ = "guest_messages"
    __table_args__ = (UniqueConstraint("reservation_id", "sender_id", "request_key"),)
    id = Column(Integer, primary_key=True)
    reservation_id = Column(Integer, ForeignKey("guest_reservations.id"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    from_admin = Column(Boolean, nullable=False)
    body = Column(Text, nullable=False)
    request_key = Column(String(64), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
