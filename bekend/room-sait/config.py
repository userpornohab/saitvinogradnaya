from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./database.db"
    PUBLIC_SITE_URL: str = "https://vinegrape.ru"
    GUEST_COOKIE_SECURE: bool = True
    GUEST_ALLOWED_ORIGINS: str = "https://vinegrape.ru"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_SSL: bool = False
    SMTP_STARTTLS: bool = True
    ROBOKASSA_MERCHANT_LOGIN: str = ""
    ROBOKASSA_PASSWORD1: str = ""
    ROBOKASSA_PASSWORD2: str = ""
    ROBOKASSA_TEST_PASSWORD1: str = ""
    ROBOKASSA_TEST_PASSWORD2: str = ""
    ROBOKASSA_IS_TEST: bool = True
    ROBOKASSA_HASH: str = "sha256"
    ROBOKASSA_RECEIPT_ENABLED: bool = True
    ROBOKASSA_TAX: str = ""
    ROBOKASSA_SNO: str = ""

    class Config:
        env_file = ".env"
        # Разрешаем посторонние переменные в .env (TELEGRAM_*, и т.п.),
        # которые используются другими процессами (например, ботом).
        extra = "ignore"

settings = Settings()
