from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.concurrency import run_in_threadpool

from auth.dependencies import check_superuser
from config import settings
from database.database import get_db
from models.room import Booking, Room
from models.guest import GuestMessage, GuestReservation, PaymentSettings
from schemas.guest import QuoteInput, ReservationInput, MessageInput, PaymentSettingsInput, RefundInput
from utils.availability import available_room_ids
from utils.guest_security import current_guest, verified_guest, limit, mail_ready
from utils.inventory_lock import lock_inventory
from utils.price_calculator import calculate_booking_price
from utils.robokassa import configuration_errors, payment_parameters, receipt_for, verify_result

router = APIRouter(tags=["guest reservations and payments"])
CHAT_STATES = {"confirmed", "cancel_requested", "test_paid"}


def payment_settings(db):
    return db.get(PaymentSettings, 1) or PaymentSettings(id=1, enabled=False, deposit_mode="first_night",
        deposit_percent=30, hold_minutes=20, terms_url="", privacy_url="", terms_version="1")


def readiness(policy):
    errors = configuration_errors()
    if not mail_ready():
        errors.append("Не настроена отправка писем")
    if not policy.terms_url or not policy.privacy_url:
        errors.append("Укажите ссылки на условия бронирования и политику конфиденциальности")
    return errors


def policy_data(policy):
    return {key: getattr(policy, key) for key in PaymentSettingsInput.model_fields}


@router.get("/guest/booking-policy")
def public_policy(db: Session = Depends(get_db)):
    policy = payment_settings(db)
    return {**policy_data(policy), "available": policy.enabled and not readiness(policy), "is_test": settings.ROBOKASSA_IS_TEST}


@router.get("/guest-admin/payment-settings", dependencies=[Depends(check_superuser)])
def get_settings(db: Session = Depends(get_db)):
    policy = payment_settings(db)
    return {**policy_data(policy), "is_test": settings.ROBOKASSA_IS_TEST, "configuration_errors": readiness(policy)}


@router.put("/guest-admin/payment-settings", dependencies=[Depends(check_superuser)])
def set_settings(data: PaymentSettingsInput, db: Session = Depends(get_db)):
    policy = PaymentSettings(id=1, **data.model_dump())
    if policy.enabled and readiness(policy):
        raise HTTPException(400, "; ".join(readiness(policy)))
    db.merge(policy)
    db.commit()
    return get_settings(db)


def quote_booking(data, db):
    today = datetime.now(timezone(timedelta(hours=3))).date()
    if data.check_in_date < today:
        raise HTTPException(400, "Нельзя забронировать прошедшие даты")
    room = db.get(Room, data.room_id)
    if not room or (room.number_of_rooms or 0) < 1:
        raise HTTPException(404, "Номер недоступен")
    if data.guests > (room.max_guests or 0):
        raise HTTPException(400, "Превышено количество гостей")
    if room.id not in available_room_ids(db, [room], data.check_in_date, data.check_out_date):
        raise HTTPException(409, "На выбранные даты свободных номеров больше нет")
    policy = payment_settings(db)
    total = int((Decimal(str(calculate_booking_price(room.id, data.check_in_date, data.check_out_date, data.guests, db))) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if policy.deposit_mode == "percent":
        deposit = int((Decimal(total) * policy.deposit_percent / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        rule = f"{policy.deposit_percent}%"
    else:
        deposit = int(Decimal(str(calculate_booking_price(room.id, data.check_in_date, data.check_in_date + timedelta(days=1), data.guests, db))) * 100)
        rule = "first_night"
    if total <= 0 or deposit <= 0 or deposit > total:
        raise HTTPException(400, "На выбранный период не настроена корректная цена")
    return room, policy, {"total_kopeks": total, "deposit_kopeks": deposit, "deposit_rule": rule,
                          "terms_version": policy.terms_version, "room_title": room.title}


@router.post("/guest/quote")
def quote(data: QuoteInput, user=Depends(verified_guest), db: Session = Depends(get_db)):
    _, _, result = quote_booking(data, db)
    return result


def reservation_data(row):
    fields = ("id", "room_id", "room_title", "check_in_date", "check_out_date", "guests", "guest_name", "guest_phone",
              "total_kopeks", "deposit_kopeks", "deposit_rule", "paid_kopeks", "status", "is_test",
              "expires_at", "created_at", "paid_at", "terms_url", "terms_version", "refund_reference")
    result = {key: getattr(row, key) for key in fields}
    if row.status == "awaiting_payment" and row.expires_at <= datetime.utcnow():
        result["status"] = "expired"
    result["chat_available"] = row.status in CHAT_STATES
    result["remaining_kopeks"] = max(row.total_kopeks - row.paid_kopeks, 0)
    # Explicit UTC prevents countdown/timezone differences in mobile browsers.
    for key in ("expires_at", "created_at", "paid_at"):
        result[key] = result[key].isoformat() + "Z" if result[key] else None
    return result


@router.post("/guest/reservations")
def reserve(data: ReservationInput, user=Depends(verified_guest), db: Session = Depends(get_db)):
    user_id = user.id
    limit(db, "reservation", user_id, 10, 3600)
    lock_inventory(db)
    existing = db.query(GuestReservation).filter_by(user_id=user_id, request_key=data.request_key).first()
    if existing:
        if (existing.room_id, existing.check_in_date, existing.check_out_date, existing.guests) != (data.room_id, data.check_in_date, data.check_out_date, data.guests):
            raise HTTPException(409, "Ключ запроса уже использован для другого бронирования")
        return reservation_data(existing)
    if db.query(GuestReservation).filter(GuestReservation.user_id == user_id,
            GuestReservation.status == "awaiting_payment", GuestReservation.expires_at > datetime.utcnow()).count() >= 2:
        raise HTTPException(409, "Сначала оплатите или отмените предыдущие заявки")
    room, policy, price = quote_booking(data, db)
    if not policy.enabled or readiness(policy):
        raise HTTPException(503, "Онлайн-оплата временно недоступна")
    if (data.quoted_total_kopeks, data.quoted_deposit_kopeks, data.terms_version) != (price["total_kopeks"], price["deposit_kopeks"], policy.terms_version):
        raise HTTPException(409, "Стоимость или условия изменились. Обновите расчёт перед оплатой.")
    row = GuestReservation(user_id=user_id, room_id=room.id, email=user.email,
        room_title=room.title, check_in_date=data.check_in_date, check_out_date=data.check_out_date,
        guests=data.guests, guest_name=data.guest_name, guest_phone=data.guest_phone,
        total_kopeks=price["total_kopeks"], deposit_kopeks=price["deposit_kopeks"], deposit_rule=price["deposit_rule"],
        request_key=data.request_key, terms_version=policy.terms_version, terms_url=policy.terms_url,
        is_test=settings.ROBOKASSA_IS_TEST, expires_at=datetime.utcnow() + timedelta(minutes=policy.hold_minutes))
    row.receipt_json = receipt_for(row)
    db.add(row)
    db.commit()
    return reservation_data(row)


def owned_reservation(db, reservation_id, user):
    row = db.get(GuestReservation, reservation_id)
    if row is None or (not user.is_superuser and row.user_id != user.id):
        raise HTTPException(404, "Бронирование не найдено")
    return row


@router.get("/guest/reservations")
def reservations(user=Depends(current_guest), db: Session = Depends(get_db), page: int = Query(1, ge=1)):
    query = db.query(GuestReservation).filter_by(user_id=user.id)
    return {"items": [reservation_data(row) for row in query.order_by(GuestReservation.id.desc()).offset((page-1)*10).limit(10)], "total": query.count()}


@router.get("/guest/reservations/{reservation_id}")
def reservation(reservation_id: int, user=Depends(current_guest), db: Session = Depends(get_db)):
    return reservation_data(owned_reservation(db, reservation_id, user))


@router.post("/guest/reservations/{reservation_id}/payment")
def payment(reservation_id: int, user=Depends(verified_guest), db: Session = Depends(get_db)):
    row = owned_reservation(db, reservation_id, user)
    if row.status != "awaiting_payment" or row.expires_at <= datetime.utcnow():
        raise HTTPException(409, "Счёт уже оплачен, отменён или срок оплаты истёк")
    if not payment_settings(db).enabled:
        raise HTTPException(503, "Онлайн-оплата временно приостановлена")
    return payment_parameters(row)


@router.post("/guest/reservations/{reservation_id}/cancel")
def cancel(reservation_id: int, user=Depends(current_guest), db: Session = Depends(get_db)):
    lock_inventory(db)
    row = owned_reservation(db, reservation_id, user)
    if row.status == "awaiting_payment":
        row.status = "cancelled"
    elif row.status in {"confirmed", "test_paid"}:
        row.status = "cancel_requested"
    db.commit()
    return reservation_data(row)


def process_result(fields, test, db):
    invoice_id, amount = verify_result(fields, test)
    lock_inventory(db)
    row = db.get(GuestReservation, invoice_id)
    if not row or row.is_test != test or row.deposit_kopeks != amount:
        raise HTTPException(400, "Invoice, environment or amount mismatch")
    if row.paid_at:
        return f"OK{invoice_id}"
    row.paid_at = datetime.utcnow()
    row.paid_kopeks = amount
    room = db.get(Room, row.room_id)
    if test:
        row.status = "test_paid"
    elif row.status != "awaiting_payment" or not room or row.check_in_date < datetime.now(timezone(timedelta(hours=3))).date():
        row.status = "payment_review"
    elif room.id not in available_room_ids(db, [room], row.check_in_date, row.check_out_date, exclude_reservation_id=row.id):
        row.status = "payment_review"
    else:
        booking = Booking(room_id=row.room_id, check_in_date=row.check_in_date, check_out_date=row.check_out_date,
            number_of_guests=row.guests, price=row.total_kopeks / 100,
            guest_name=row.guest_name, guest_phone=row.guest_phone, guest_comment=f"Онлайн-бронирование #{row.id}")
        db.add(booking)
        db.flush()
        row.booking_id = booking.id
        row.status = "confirmed"
    db.commit()
    return f"OK{invoice_id}"


async def callback(request, test, db):
    if request.headers.get("content-type", "").split(";")[0] != "application/x-www-form-urlencoded":
        raise HTTPException(415, "Use application/x-www-form-urlencoded")
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 16384:
            raise HTTPException(413, "Callback too large")
    try:
        pairs = parse_qsl(body.decode("utf-8"), keep_blank_values=True, max_num_fields=40)
    except (UnicodeDecodeError, ValueError):
        raise HTTPException(400, "Invalid callback")
    if len(dict(pairs)) != len(pairs):
        raise HTTPException(400, "Duplicate callback parameters")
    return PlainTextResponse(await run_in_threadpool(process_result, dict(pairs), test, db))


@router.post("/payments/robokassa/result")
async def result(request: Request, db: Session = Depends(get_db)):
    return await callback(request, False, db)


@router.post("/payments/robokassa/result/test")
async def test_result(request: Request, db: Session = Depends(get_db)):
    return await callback(request, True, db)


def message_list(reservation_id, after_id, db, user):
    row = owned_reservation(db, reservation_id, user)
    if row.status not in CHAT_STATES:
        raise HTTPException(403, "Чат доступен после подтверждения бронирования")
    return [{"id": message.id, "body": message.body, "from_admin": message.from_admin,
             "created_at": message.created_at.isoformat() + "Z"} for message in
            db.query(GuestMessage).filter(GuestMessage.reservation_id == row.id, GuestMessage.id > after_id)
            .order_by(GuestMessage.id).limit(100)]


def send_message(reservation_id, data, db, user):
    limit(db, "messages", user.id, 30, 60)
    row = owned_reservation(db, reservation_id, user)
    if row.status not in CHAT_STATES:
        raise HTTPException(403, "Чат доступен после подтверждения бронирования")
    existing = db.query(GuestMessage).filter_by(reservation_id=row.id, sender_id=user.id, request_key=data.request_key).first()
    if not existing:
        db.add(GuestMessage(reservation_id=row.id, sender_id=user.id, from_admin=user.is_superuser,
                            body=data.body, request_key=data.request_key))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
    return {"ok": True}


@router.get("/guest/reservations/{reservation_id}/messages")
def messages(reservation_id: int, after_id: int = Query(0, ge=0), user=Depends(current_guest), db: Session = Depends(get_db)):
    return message_list(reservation_id, after_id, db, user)


@router.post("/guest/reservations/{reservation_id}/messages")
def new_message(reservation_id: int, data: MessageInput, user=Depends(verified_guest), db: Session = Depends(get_db)):
    return send_message(reservation_id, data, db, user)


@router.get("/guest-admin/reservations")
def admin_reservations(page: int = Query(1, ge=1), search: str = Query("", max_length=100),
                       state: str = Query("", max_length=30), user=Depends(check_superuser), db: Session = Depends(get_db)):
    query = db.query(GuestReservation)
    if search:
        query = query.filter(GuestReservation.guest_name.contains(search, autoescape=True))
    if state == "expired":
        query = query.filter(GuestReservation.status == "awaiting_payment", GuestReservation.expires_at <= datetime.utcnow())
    elif state:
        query = query.filter(GuestReservation.status == state)
        if state == "awaiting_payment":
            query = query.filter(GuestReservation.expires_at > datetime.utcnow())
    return {"total": query.count(), "items": [reservation_data(row) for row in query.order_by(GuestReservation.id.desc()).offset((page-1)*20).limit(20)]}


@router.get("/guest-admin/reservations/{reservation_id}/messages")
def admin_messages(reservation_id: int, after_id: int = Query(0, ge=0), user=Depends(check_superuser), db: Session = Depends(get_db)):
    return message_list(reservation_id, after_id, db, user)


@router.post("/guest-admin/reservations/{reservation_id}/messages")
def admin_send(reservation_id: int, data: MessageInput, user=Depends(check_superuser), db: Session = Depends(get_db)):
    return send_message(reservation_id, data, db, user)


@router.post("/guest-admin/reservations/{reservation_id}/refund-record")
def record_refund(reservation_id: int, data: RefundInput, user=Depends(check_superuser), db: Session = Depends(get_db)):
    lock_inventory(db)
    row = owned_reservation(db, reservation_id, user)
    if row.status not in {"cancel_requested", "payment_review"} or not row.paid_at:
        raise HTTPException(409, "Возврат нельзя записать для этого статуса")
    # This records an externally completed FULL refund; it never pretends to transfer money.
    if row.booking_id:
        booking = db.get(Booking, row.booking_id)
        row.booking_id = None
        if booking:
            db.delete(booking)
    row.status = "refunded"
    row.refund_reference = data.reference
    row.refund_admin_id = user.id
    row.refunded_at = datetime.utcnow()
    db.commit()
    return reservation_data(row)
