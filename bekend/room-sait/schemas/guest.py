from datetime import date
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator, model_validator

Password = Annotated[str, StringConstraints(strip_whitespace=False)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Credentials(StrictModel):
    email: EmailStr
    password: Password = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return value.lower()

    @field_validator("password")
    @classmethod
    def password_bytes(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Пароль должен занимать не более 72 байт UTF-8")
        return value


class Registration(Credentials):
    password: Password = Field(min_length=12, max_length=72)
    name: str = Field(min_length=2, max_length=100)


class EmailInput(StrictModel):
    email: EmailStr


class TokenInput(StrictModel):
    token: str = Field(min_length=30, max_length=150)


class ResetInput(TokenInput):
    password: Password = Field(min_length=12, max_length=72)

    @field_validator("password")
    @classmethod
    def password_bytes(cls, value):
        return Credentials.password_bytes(value)


class ProfileInput(StrictModel):
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(pattern=r"^\+?[0-9 ()-]{7,25}$")


class QuoteInput(StrictModel):
    room_id: int = Field(gt=0)
    check_in_date: date
    check_out_date: date
    guests: int = Field(ge=1, le=100)

    @model_validator(mode="after")
    def valid_period(self):
        if not 3 <= (self.check_out_date - self.check_in_date).days <= 90:
            raise ValueError("Выберите период от 3 до 90 ночей")
        return self


class ReservationInput(QuoteInput):
    guest_name: str = Field(min_length=2, max_length=100)
    guest_phone: str = Field(pattern=r"^\+?[0-9 ()-]{7,25}$")
    request_key: str = Field(pattern=r"^[a-zA-Z0-9-]{16,64}$")
    accepted_terms: Literal[True]
    terms_version: str = Field(max_length=50)
    quoted_total_kopeks: int = Field(gt=0)
    quoted_deposit_kopeks: int = Field(gt=0)


class MessageInput(StrictModel):
    body: str = Field(min_length=1, max_length=4000)
    request_key: str = Field(pattern=r"^[a-zA-Z0-9-]{16,64}$")


class PaymentSettingsInput(StrictModel):
    enabled: bool
    deposit_mode: Literal["first_night", "percent"]
    deposit_percent: int = Field(ge=1, le=100)
    hold_minutes: int = Field(ge=10, le=60)
    terms_url: str = Field(max_length=500)
    privacy_url: str = Field(max_length=500)
    terms_version: str = Field(min_length=1, max_length=50)

    @field_validator("terms_url", "privacy_url")
    @classmethod
    def safe_url(cls, value):
        from urllib.parse import urlsplit
        if value and not (value.startswith("/") and not value.startswith("//")):
            url = urlsplit(value)
            if url.scheme != "https" or not url.hostname or url.username or url.password:
                raise ValueError("Укажите HTTPS-ссылку или путь вида /terms")
        if any(char in value for char in ("\\", "\r", "\n")):
            raise ValueError("Некорректная ссылка")
        return value


class RefundInput(StrictModel):
    reference: str = Field(min_length=5, max_length=200)
