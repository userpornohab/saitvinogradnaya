"""Telegram-бот на aiogram 3.x.

Запуск отдельно от FastAPI (polling), например:
    python run_bot.py

Требует переменных окружения (.env рядом с main.py):
    TELEGRAM_BOT_TOKEN        — токен от @BotFather
    TELEGRAM_MANAGER_CHAT_ID  — chat_id менеджера (int). Опционально.
    TELEGRAM_BOT_USERNAME     — username бота без '@' (для логов/проверок)
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import date
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message

from .payload import BookingPayload, decode_payload

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Форматирование сообщений
# --------------------------------------------------------------------------- #

def _fmt_date(d: Optional[date]) -> str:
    return d.strftime("%d.%m.%Y") if d else "—"


def _fmt_money(v: Optional[int]) -> str:
    if v is None:
        return "—"
    return f"{int(v):,} ₽".replace(",", " ")


def build_client_message(payload: BookingPayload) -> str:
    """Сообщение, которое получит клиент в боте."""
    return (
        "<b>Здравствуйте!</b>\n"
        "Ваше бронирование принято в обработку:\n\n"
        f"📅 <b>Дата заезда:</b> {_fmt_date(payload.checkin)}\n"
        f"📅 <b>Дата выезда:</b> {_fmt_date(payload.checkout)}\n"
        f"👥 <b>Гостей:</b> {payload.guests or '—'}\n"
        f"💰 <b>Цена:</b> {_fmt_money(payload.price)}\n"
        f"🔐 <b>Предоплата:</b> {_fmt_money(payload.prepay)}\n\n"
        "Менеджер скоро свяжется с вами для подтверждения."
    )


def build_manager_message(payload: BookingPayload, user: Message) -> str:
    """Сообщение для менеджера о новой заявке."""
    from_user = user.from_user
    username = f"@{from_user.username}" if from_user and from_user.username else "—"
    full_name = from_user.full_name if from_user else "—"
    tg_id = from_user.id if from_user else "—"

    return (
        "<b>🆕 Новая заявка на бронирование</b>\n\n"
        f"👤 <b>Клиент:</b> {full_name}\n"
        f"🔗 <b>Telegram:</b> {username} (id: <code>{tg_id}</code>)\n\n"
        f"📅 Заезд: <b>{_fmt_date(payload.checkin)}</b>\n"
        f"📅 Выезд: <b>{_fmt_date(payload.checkout)}</b>\n"
        f"👥 Гостей: <b>{payload.guests or '—'}</b>\n"
        f"💰 Цена: <b>{_fmt_money(payload.price)}</b>\n"
        f"🔐 Предоплата: <b>{_fmt_money(payload.prepay)}</b>\n"
        f"🏠 Номер: <code>{payload.room or '—'}</code>"
    )


# --------------------------------------------------------------------------- #
# Хэндлеры
# --------------------------------------------------------------------------- #

def create_dispatcher(manager_chat_id: Optional[int]) -> Dispatcher:
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def on_start(message: Message, command: CommandObject):
        token = (command.args or "").strip()

        logger.info(
            "/start from user_id=%s username=%s token_len=%d token=%r",
            message.from_user.id,
            message.from_user.username,
            len(token),
            token,
        )

        # /start без payload — пользователь пришёл напрямую
        if not token:
            await message.answer(
                "Здравствуйте! Чтобы забронировать номер, воспользуйтесь кнопкой "
                "«Забронировать» на нашем сайте — мы покажем здесь детали заявки."
            )
            return

        payload = decode_payload(token)
        logger.info("Decoded payload: %s", payload)

        # Если не удалось распарсить ни одного поля — сообщим об этом, но не молчим
        if not any([
            payload.checkin, payload.checkout, payload.guests,
            payload.price, payload.prepay, payload.room,
        ]):
            await message.answer(
                "Ссылка получена, но данные бронирования не удалось распознать. "
                "Попробуйте ещё раз нажать «Забронировать» на сайте."
            )
            return

        # 1) Клиенту — подтверждение
        await message.answer(build_client_message(payload))

        # 2) Менеджеру — уведомление (если настроен chat_id)
        if manager_chat_id:
            try:
                await message.bot.send_message(
                    manager_chat_id,
                    build_manager_message(payload, message),
                )
            except Exception as exc:  # pragma: no cover
                logger.exception("Не удалось отправить уведомление менеджеру: %s", exc)

    @dp.message(F.text)
    async def on_any_text(message: Message):
        await message.answer(
            "Спасибо за сообщение! Менеджер ответит в ближайшее время."
        )
        if manager_chat_id and message.from_user.id != manager_chat_id:
            try:
                await message.bot.send_message(
                    manager_chat_id,
                    f"💬 Сообщение от @{message.from_user.username or '—'} "
                    f"(id {message.from_user.id}):\n\n{message.text}",
                )
            except Exception:  # pragma: no cover
                logger.exception("Не удалось переслать сообщение менеджеру")

    return dp


# --------------------------------------------------------------------------- #
# Точка входа
# --------------------------------------------------------------------------- #

async def run_bot() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN не задан. Добавьте его в .env рядом с main.py"
        )

    manager_chat_id_env = os.getenv("TELEGRAM_MANAGER_CHAT_ID")
    try:
        manager_chat_id = int(manager_chat_id_env) if manager_chat_id_env else None
    except ValueError:
        logger.warning(
            "TELEGRAM_MANAGER_CHAT_ID=%r не число, уведомления менеджеру отключены",
            manager_chat_id_env,
        )
        manager_chat_id = None

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = create_dispatcher(manager_chat_id)

    me = await bot.get_me()
    logger.info("Бот запущен: @%s (id=%s)", me.username, me.id)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s :: %(message)s",
    )
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
