from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from database.database import get_db
from models.user import User
from schemas.auth import Token, UserResponse, UserCreate, UserUpdate
from auth.core import create_access_token
from auth.dependencies import get_current_user, check_superuser
from config import settings
from passlib.context import CryptContext
from utils.guest_security import limit

router = APIRouter(tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/register/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    raise HTTPException(410, "Используйте регистрацию гостя /guest/auth/register с подтверждением почты")

@router.post("/token/", response_model=Token)
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    limit(db, "admin-login-ip", request.client.host, 60)
    limit(db, "admin-login-email", form_data.username.lower(), 10)
    if len(form_data.password.encode("utf-8")) > 72:
        raise HTTPException(401, "Incorrect email or password")
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.is_active or not user.is_superuser or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    # Если имя не установлено, возвращаем пустую строку вместо null
    if current_user.name is None:
        current_user.name = ""
    return current_user


@router.put("/users/{user_id}/", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,  # Use a separate UserUpdate schema
    db: Session = Depends(get_db),
    current_user: User = Depends(check_superuser)
):
    # Check permissions
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    # Get the user to update
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check email uniqueness if email is being updated
    if user_update.email and user_update.email != db_user.email:
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already in use by another user"
            )
        db_user.email = user_update.email
    
    # Update password if provided
    if user_update.password:
        db_user.hashed_password = pwd_context.hash(user_update.password)
    
    # Update other fields
    if user_update.name is not None:
        db_user.name = user_update.name
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Database integrity error - possibly duplicate email"
        )
