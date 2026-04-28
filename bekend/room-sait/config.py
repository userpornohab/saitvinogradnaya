from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./database.db"

    class Config:
        env_file = ".env"
        # Разрешаем посторонние переменные в .env (TELEGRAM_*, и т.п.),
        # которые используются другими процессами (например, ботом).
        extra = "ignore"

settings = Settings()