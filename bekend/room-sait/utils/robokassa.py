"""Robokassa signatures are calculated only on the server; amounts are stored in kopeks."""
from datetime import timedelta
from decimal import Decimal, InvalidOperation
import hashlib
import hmac
import json
import re
from urllib.parse import quote

from fastapi import HTTPException
from config import settings

PAYMENT_URL = "https://auth.robokassa.ru/Merchant/Index.aspx"
TAXES = {"none", "vat0", "vat10", "vat110", "vat20", "vat22", "vat120", "vat122", "vat5", "vat7", "vat105", "vat107"}


def credentials(test):
    if test:
        return settings.ROBOKASSA_TEST_PASSWORD1, settings.ROBOKASSA_TEST_PASSWORD2
    return settings.ROBOKASSA_PASSWORD1, settings.ROBOKASSA_PASSWORD2


def configuration_errors():
    errors = []
    if not settings.ROBOKASSA_MERCHANT_LOGIN or not all(credentials(settings.ROBOKASSA_IS_TEST)):
        errors.append("Не заданы логин магазина и соответствующая пара паролей Робокассы")
    if settings.ROBOKASSA_HASH.lower() not in {"sha256", "sha512", "md5"}:
        errors.append("Алгоритм подписи должен быть sha256, sha512 или md5")
    if settings.ROBOKASSA_RECEIPT_ENABLED and settings.ROBOKASSA_TAX not in TAXES:
        errors.append("Укажите налоговую ставку ROBOKASSA_TAX")
    if settings.ROBOKASSA_PASSWORD2 and settings.ROBOKASSA_PASSWORD2 == settings.ROBOKASSA_TEST_PASSWORD2:
        errors.append("Боевой и тестовый Пароль №2 должны различаться")
    if not settings.ROBOKASSA_IS_TEST:
        if not settings.PUBLIC_SITE_URL.startswith("https://") or not settings.GUEST_COOKIE_SECURE:
            errors.append("Для настоящих платежей нужны HTTPS и Secure cookie")
        if not settings.ROBOKASSA_RECEIPT_ENABLED:
            errors.append("Для настоящих платежей включите передачу чека")
    return errors


def signature(value):
    algorithm = settings.ROBOKASSA_HASH.lower()
    if algorithm not in {"sha256", "sha512", "md5"}:
        raise HTTPException(503, "Не настроена подпись платёжной системы")
    return hashlib.new(algorithm, value.encode("utf-8")).hexdigest()


def rubles(kopeks):
    return f"{kopeks // 100}.{kopeks % 100:02d}"


def receipt_for(reservation):
    if not settings.ROBOKASSA_RECEIPT_ENABLED:
        return None
    receipt = {"items": [{"name": ("Предоплата проживания: " + reservation.room_title)[:128],
                         "quantity": 1, "sum": float(Decimal(reservation.deposit_kopeks) / 100),
                         "payment_method": "full_prepayment" if reservation.deposit_kopeks == reservation.total_kopeks else "prepayment",
                         "payment_object": "service", "tax": settings.ROBOKASSA_TAX}]}
    if settings.ROBOKASSA_SNO:
        receipt["sno"] = settings.ROBOKASSA_SNO
    return json.dumps(receipt, ensure_ascii=False, separators=(",", ":"))


def payment_parameters(reservation):
    password, _ = credentials(reservation.is_test)
    if not password or not settings.ROBOKASSA_MERCHANT_LOGIN:
        raise HTTPException(503, "Оплата пока не настроена")
    amount = rubles(reservation.deposit_kopeks)
    values = [settings.ROBOKASSA_MERCHANT_LOGIN, amount, str(reservation.id)]
    receipt = quote(reservation.receipt_json, safe="") if reservation.receipt_json else None
    if receipt:
        values.append(receipt)
    values.append(password)
    params = {"MerchantLogin": settings.ROBOKASSA_MERCHANT_LOGIN, "OutSum": amount,
              "InvId": reservation.id, "Description": f"Предоплата бронирования №{reservation.id}",
              "SignatureValue": signature(":".join(values)), "Email": reservation.email,
              "Culture": "ru", "Encoding": "utf-8", "IncCurrLabel": "SBP",
              "IsTest": 1 if reservation.is_test else 0,
              "ExpirationDate": (reservation.expires_at + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M")}
    if receipt:
        params["Receipt"] = receipt
    return {"action": PAYMENT_URL, "params": params}


def verify_result(fields, test):
    amount, invoice, received = fields.get("OutSum", ""), fields.get("InvId", ""), fields.get("SignatureValue", "")
    if not re.fullmatch(r"[0-9]{1,12}(?:\.[0-9]{1,6})?", amount) or not re.fullmatch(r"[1-9][0-9]{0,17}", invoice):
        raise HTTPException(400, "Invalid payment parameters")
    if any(key.lower().startswith("shp_") for key in fields):
        raise HTTPException(400, "Unexpected signed parameters")
    _, password = credentials(test)
    if not password:
        raise HTTPException(503, "Payment callback is not configured")
    if settings.ROBOKASSA_PASSWORD2 and settings.ROBOKASSA_PASSWORD2 == settings.ROBOKASSA_TEST_PASSWORD2:
        raise HTTPException(503, "Separate live and test callback passwords are required")
    expected = signature(f"{amount}:{invoice}:{password}")
    if not re.fullmatch(r"[a-fA-F0-9]+", received) or not hmac.compare_digest(expected, received.lower()):
        raise HTTPException(403, "Invalid payment signature")
    try:
        kopeks = Decimal(amount) * 100
        if kopeks != kopeks.to_integral_value() or kopeks <= 0:
            raise InvalidOperation
    except InvalidOperation:
        raise HTTPException(400, "Invalid payment amount")
    return int(invoice), int(kopeks)
