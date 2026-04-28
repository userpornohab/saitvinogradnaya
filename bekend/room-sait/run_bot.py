"""Entrypoint для запуска Telegram-бота в отдельном процессе.

Использование (из папки bekend/room-sait):
    python run_bot.py
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

# Подхватываем .env, который уже используется приложением (рядом с main.py)
load_dotenv(Path(__file__).parent / ".env")

from bot.telegram_bot import main  # noqa: E402  (после load_dotenv)


if __name__ == "__main__":
    main()






