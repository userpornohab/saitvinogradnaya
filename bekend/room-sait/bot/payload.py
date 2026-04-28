"""Кодирование/декодирование payload бронирования для Telegram deep-link.

Telegram /start принимает параметр длиной до 64 символов из алфавита
[A-Za-z0-9_-], поэтому используется URL-safe base64 без padding.

Формат исходной строки (до base64):
    checkin=YYYY-MM-DD&checkout=YYYY-MM-DD&guests=N&price=XXX&prepay=YYY&room=ID
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from urllib.parse import parse_qs, urlencode


@dataclass
class BookingPayload:
    checkin: Optional[date] = None
    checkout: Optional[date] = None
    guests: Optional[int] = None
    price: Optional[int] = None
    prepay: Optional[int] = None
    room: Optional[str] = None  # id номера, если пришёл


# --------------------------------------------------------------------------- #
# base64 helpers (URL-safe, без padding)
# --------------------------------------------------------------------------- #

def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(s: str) -> bytes:
    # Восстанавливаем padding, если был удалён
    pad = (-len(s)) % 4
    return base64.urlsafe_b64decode(s + ("=" * pad))


# --------------------------------------------------------------------------- #
# encode / decode
# --------------------------------------------------------------------------- #

def encode_payload(payload: BookingPayload) -> str:
    """Сериализует объект в URL-safe base64 строку (совместимую с фронтом).

    Используются короткие ключи и компактные даты (YYYYMMDD),
    чтобы уложиться в 64-символьный лимит Telegram /start.
    """
    data: dict[str, str] = {}
    if payload.checkin:
        data["c"] = payload.checkin.strftime("%Y%m%d")
    if payload.checkout:
        data["o"] = payload.checkout.strftime("%Y%m%d")
    if payload.guests is not None:
        data["g"] = str(payload.guests)
    if payload.price is not None:
        data["p"] = str(payload.price)
    if payload.prepay is not None:
        data["d"] = str(payload.prepay)
    if payload.room:
        data["r"] = str(payload.room)
    raw = urlencode(data)
    return _b64encode(raw.encode("utf-8"))


def decode_payload(token: str) -> BookingPayload:
    """Декодирует URL-safe base64 строку обратно в BookingPayload.

    В случае некорректного формата возвращает пустой BookingPayload —
    это безопаснее, чем бросать исключение в хэндлере бота.
    """
    payload = BookingPayload()
    if not token:
        return payload
    try:
        raw = _b64decode(token).decode("utf-8", errors="replace")
    except (ValueError, UnicodeDecodeError):
        return payload

    parsed = parse_qs(raw, keep_blank_values=False)

    def _first(key: str) -> Optional[str]:
        vals = parsed.get(key)
        return vals[0] if vals else None

    # Короткие ключи (c/o/g/p/d/r) — основной формат, совместимый с 64-символьным
    # лимитом Telegram. Длинные ключи — для обратной совместимости.
    if (v := _first("c") or _first("checkin")):
        payload.checkin = _safe_date(v)
    if (v := _first("o") or _first("checkout")):
        payload.checkout = _safe_date(v)
    if (v := _first("g") or _first("guests")):
        payload.guests = _safe_int(v)
    if (v := _first("p") or _first("price")):
        payload.price = _safe_int(v)
    if (v := _first("d") or _first("prepay")):
        payload.prepay = _safe_int(v)
    if (v := _first("r") or _first("room")):
        payload.room = v
    return payload


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def _safe_date(value: str) -> Optional[date]:
    for fmt in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def _safe_int(value: str) -> Optional[int]:
    try:
        # поддерживаем и '15000', и '15000.0'
        return int(float(value))
    except (ValueError, TypeError):
        return None
