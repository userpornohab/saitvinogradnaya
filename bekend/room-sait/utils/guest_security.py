from datetime import datetime, timedelta
from email.message import EmailMessage
import hashlib
import hmac
import secrets
import smtplib
import ssl
from urllib.parse import urlencode

from fastapi import Depends, HTTPException, Request
from sqlalchemy import case
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from config import settings
from database.database import get_db
from models.guest import GuestProfile, GuestSession, GuestToken, RequestLimit
from models.user import User

COOKIE = "vinegrape_guest"


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def check_origin(request: Request):
    allowed = {origin.strip().rstrip("/") for origin in settings.GUEST_ALLOWED_ORIGINS.split(",")}
    if request.headers.get("origin") not in allowed:
        raise HTTPException(403, "Недопустимый источник запроса")


def csrf_value(token):
    return hmac.new(settings.SECRET_KEY.encode(), ("guest-csrf:" + token).encode(), hashlib.sha256).hexdigest()


def current_guest(request: Request, db: Session = Depends(get_db)):
    raw = request.cookies.get(COOKIE, "")
    session = db.get(GuestSession, digest(raw)) if raw else None
    user = db.get(User, session.user_id) if session and session.expires_at > datetime.utcnow() else None
    if user is None or not user.is_active or user.is_superuser:
        raise HTTPException(401, "Войдите в личный кабинет гостя")
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        check_origin(request)
        if not hmac.compare_digest(request.headers.get("x-csrf-token", "").encode(), csrf_value(raw).encode()):
            raise HTTPException(403, "Обновите страницу и повторите действие")
    return user


def verified_guest(user=Depends(current_guest), db: Session = Depends(get_db)):
    profile = db.get(GuestProfile, user.id)
    if not profile or not profile.email_verified:
        raise HTTPException(403, "Подтвердите адрес электронной почты")
    return user


def limit(db, scope, key, maximum=10, seconds=900):
    now = datetime.utcnow()
    hashed = digest(scope + ":" + str(key))
    expired = RequestLimit.expires_at <= now
    statement = insert(RequestLimit).values(key=hashed, count=1, expires_at=now + timedelta(seconds=seconds))
    statement = statement.on_conflict_do_update(index_elements=[RequestLimit.key], set_={
        "count": case((expired, 1), else_=RequestLimit.count + 1),
        "expires_at": case((expired, now + timedelta(seconds=seconds)), else_=RequestLimit.expires_at)})
    db.execute(statement)
    db.query(RequestLimit).filter(RequestLimit.expires_at < now - timedelta(days=1)).delete()
    db.commit()
    if db.get(RequestLimit, hashed).count > maximum:
        raise HTTPException(429, "Слишком много запросов. Попробуйте позже.", headers={"Retry-After": str(seconds)})


def mail_ready():
    return bool(settings.SMTP_HOST and settings.SMTP_FROM)


def send_account_email(email, token, purpose):
    if not mail_ready():
        raise HTTPException(503, "Почтовый сервис пока не настроен")
    action = "Подтверждение почты" if purpose == "verify" else "Восстановление пароля"
    # Fragment keeps the one-use secret out of HTTP access logs and Referer headers.
    link = settings.PUBLIC_SITE_URL.rstrip("/") + "/account#" + urlencode({"action": purpose, "token": token})
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM
    message["To"] = email
    message["Subject"] = action + " | Виноградная Лоза"
    message.set_content(f"{action}\n\n{link}\n\nСсылка действует 30 минут и используется один раз.\nЕсли вы не запрашивали это действие, проигнорируйте письмо.")
    connection = smtplib.SMTP_SSL if settings.SMTP_SSL else smtplib.SMTP
    options = {"context": ssl.create_default_context()} if settings.SMTP_SSL else {}
    try:
        with connection(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10, **options) as smtp:
            if settings.SMTP_STARTTLS and not settings.SMTP_SSL:
                smtp.starttls(context=ssl.create_default_context())
            if settings.SMTP_USER:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        raise HTTPException(503, "Не удалось отправить письмо. Попробуйте позже.")


def issue_email_token(db, user, purpose):
    token = secrets.token_urlsafe(32)
    db.query(GuestToken).filter(GuestToken.user_id == user.id, GuestToken.purpose == purpose).delete()
    db.add(GuestToken(token_hash=digest(token), user_id=user.id, purpose=purpose,
                      expires_at=datetime.utcnow() + timedelta(minutes=30)))
    db.commit()
    send_account_email(user.email, token, purpose)


def open_session(db, user, response):
    token = secrets.token_urlsafe(32)
    now = datetime.utcnow()
    db.query(GuestSession).filter(GuestSession.expires_at < now).delete()
    db.add(GuestSession(token_hash=digest(token), user_id=user.id, expires_at=now + timedelta(days=7)))
    db.commit()
    response.set_cookie(COOKIE, token, max_age=7 * 86400, httponly=True,
                        secure=settings.GUEST_COOKIE_SECURE, samesite="lax", path="/guest")
    return csrf_value(token)
