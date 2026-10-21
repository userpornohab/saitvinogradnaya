from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth.core import get_password_hash, pwd_context
from database.database import get_db
from models.user import User
from models.guest import GuestProfile, GuestSession, GuestToken
from schemas.guest import Credentials, Registration, EmailInput, TokenInput, ResetInput, ProfileInput
from utils.guest_security import (COOKIE, check_origin, csrf_value, current_guest, digest,
                                 issue_email_token, limit, mail_ready, open_session)
from utils.inventory_lock import lock_inventory

router = APIRouter(prefix="/guest/auth", tags=["guest accounts"])
GENERIC = {"message": "Если адрес доступен для этого действия, на него отправлено письмо."}
DUMMY_HASH = get_password_hash("not-a-real-account-password")


def find_user(db, email):
    return db.query(User).filter(func.lower(User.email) == email.lower()).first()


def user_data(user, db):
    profile = db.get(GuestProfile, user.id)
    return {"id": user.id, "email": user.email, "name": user.name,
            "phone": profile.phone if profile else "", "email_verified": bool(profile and profile.email_verified)}


@router.post("/register", dependencies=[Depends(check_origin)])
def register(data: Registration, request: Request, db: Session = Depends(get_db)):
    limit(db, "register-ip", request.client.host, 30, 3600)
    limit(db, "register-email", data.email, 3, 1800)
    if not mail_ready():
        raise HTTPException(503, "Регистрация временно недоступна: почтовый сервис не настроен")
    user = find_user(db, data.email)
    if user:
        profile = db.get(GuestProfile, user.id)
        if profile and not profile.email_verified and not user.is_superuser and user.is_active:
            # The email owner must replace a password potentially set by somebody else.
            issue_email_token(db, user, "reset")
        return GENERIC
    user = User(email=data.email, name=data.name, hashed_password=get_password_hash(data.password), is_superuser=False)
    try:
        db.add(user)
        db.flush()
        db.add(GuestProfile(user_id=user.id, phone="", email_verified=False))
        db.commit()
    except IntegrityError:
        db.rollback()
        return GENERIC
    issue_email_token(db, user, "verify")
    return GENERIC


@router.post("/login", dependencies=[Depends(check_origin)])
def login(data: Credentials, request: Request, response: Response, db: Session = Depends(get_db)):
    limit(db, "login-ip", request.client.host, 60)
    limit(db, "login-email", data.email, 10)
    user = find_user(db, data.email)
    valid = pwd_context.verify(data.password, user.hashed_password if user else DUMMY_HASH)
    if not valid or not user or not user.is_active or user.is_superuser:
        raise HTTPException(401, "Неверная почта или пароль гостевого аккаунта")
    if not db.get(GuestProfile, user.id):
        db.add(GuestProfile(user_id=user.id, phone="", email_verified=False))
        db.commit()
    old = request.cookies.get(COOKIE)
    if old:
        db.query(GuestSession).filter(GuestSession.token_hash == digest(old)).delete()
    csrf = open_session(db, user, response)
    return {"user": user_data(user, db), "csrf": csrf}


@router.get("/session")
def session(request: Request, user=Depends(current_guest), db: Session = Depends(get_db)):
    return {"user": user_data(user, db), "csrf": csrf_value(request.cookies[COOKIE])}


@router.post("/logout")
def logout(request: Request, response: Response, user=Depends(current_guest), db: Session = Depends(get_db)):
    db.query(GuestSession).filter(GuestSession.token_hash == digest(request.cookies[COOKIE])).delete()
    db.commit()
    response.delete_cookie(COOKIE, path="/guest", secure=True if request.url.scheme == "https" else False, httponly=True, samesite="lax")
    return {"ok": True}


@router.patch("/profile")
def profile(data: ProfileInput, user=Depends(current_guest), db: Session = Depends(get_db)):
    user.name = data.name
    db.get(GuestProfile, user.id).phone = data.phone
    db.commit()
    return user_data(user, db)


@router.post("/verification")
def resend(user=Depends(current_guest), db: Session = Depends(get_db)):
    limit(db, "verify", user.id, 3, 1800)
    if not db.get(GuestProfile, user.id).email_verified:
        issue_email_token(db, user, "verify")
    return GENERIC


@router.post("/forgot", dependencies=[Depends(check_origin)])
def forgot(data: EmailInput, request: Request, db: Session = Depends(get_db)):
    limit(db, "forgot-ip", request.client.host, 30, 3600)
    limit(db, "forgot-email", data.email.lower(), 3, 1800)
    user = find_user(db, data.email)
    if user and not user.is_superuser and user.is_active:
        issue_email_token(db, user, "reset")
    return GENERIC


def consume_token(db, raw, purpose):
    lock_inventory(db)
    token = db.get(GuestToken, digest(raw))
    if not token or token.purpose != purpose or token.expires_at <= datetime.utcnow():
        raise HTTPException(400, "Ссылка недействительна или уже использована")
    user = db.get(User, token.user_id)
    if not user or not user.is_active or user.is_superuser:
        raise HTTPException(400, "Ссылка недействительна")
    db.delete(token)
    return user


@router.post("/verify", dependencies=[Depends(check_origin)])
def verify(data: TokenInput, request: Request, db: Session = Depends(get_db)):
    limit(db, "token-ip", request.client.host, 30)
    user = consume_token(db, data.token, "verify")
    db.get(GuestProfile, user.id).email_verified = True
    db.commit()
    return {"message": "Почта подтверждена. Теперь можно войти и забронировать номер."}


@router.post("/reset", dependencies=[Depends(check_origin)])
def reset(data: ResetInput, request: Request, db: Session = Depends(get_db)):
    limit(db, "token-ip", request.client.host, 30)
    hashed = get_password_hash(data.password)
    user = consume_token(db, data.token, "reset")
    user.hashed_password = hashed
    profile = db.get(GuestProfile, user.id)
    if not profile:
        profile = GuestProfile(user_id=user.id, phone="")
        db.add(profile)
    profile.email_verified = True
    db.query(GuestSession).filter(GuestSession.user_id == user.id).delete()
    db.flush()
    db.query(GuestToken).filter(GuestToken.user_id == user.id).delete(synchronize_session=False)
    db.commit()
    return {"message": "Пароль изменён. Войдите с новым паролем."}
