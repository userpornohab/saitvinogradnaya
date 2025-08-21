from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = Field(None)  # Разрешаем null значения

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_superuser: bool

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None
    name: str | None = None