# Telegram-бот для подтверждения бронирований

Модуль добавляет сценарий «нажать «Забронировать» → открыть бота в Telegram → менеджер
получает уведомление». Существующие API бронирований и расчёта цены **не меняются**.

## Архитектура

```
┌────────────┐  click "Забронировать"  ┌──────────────────┐
│ Vue front  │ ──────────────────────▶│ TelegramBookingModal │
└────────────┘                        └──────────┬─────────┘
                                                 │ t.me/<bot>?start=<b64>
                                                 ▼
                                         ┌───────────────┐
                                         │ Telegram app  │
                                         └───────┬───────┘
                                                 │ /start <payload>
                                                 ▼
                                       ┌──────────────────┐
                                       │  aiogram 3 bot   │
                                       │  (polling)       │
                                       └──┬────────────┬──┘
                                          │            │
                                 клиенту  │            │ менеджеру
                              подтверждение            уведомление
```

Бот запускается **отдельным процессом** (`run_bot.py`) — так он переживает перезапуски
FastAPI и не блокирует обработку HTTP-запросов.

## Файлы

| Путь | Назначение |
|------|------------|
| `bot/payload.py` | URL-safe base64 encode/decode полезной нагрузки |
| `bot/telegram_bot.py` | aiogram Dispatcher + форматирование сообщений |
| `run_bot.py` | Entrypoint: `python run_bot.py` |
| `frontend/.../utils/telegramLink.js` | Генерация deep-link на фронтенде |
| `frontend/.../components/TelegramBookingModal.vue` | Модальное окно подтверждения |

## Настройка

### 1. Создайте бота у [@BotFather](https://t.me/BotFather)

Получите `TELEGRAM_BOT_TOKEN` и `bot username` (без `@`).

### 2. Узнайте `chat_id` менеджера

Напишите любое сообщение боту с аккаунта менеджера, затем обратитесь к
`https://api.telegram.org/bot<TOKEN>/getUpdates` — `chat.id` будет в ответе.

### 3. Backend `.env` (рядом с `main.py`)

```env
TELEGRAM_BOT_TOKEN=123456:AAE...
TELEGRAM_BOT_USERNAME=my_booking_bot
TELEGRAM_MANAGER_CHAT_ID=123456789
```

### 4. Frontend `.env` (рядом с `package.json`)

```env
VUE_APP_TELEGRAM_BOT=my_booking_bot
```

> Username должен совпадать с тем, что указан в BotFather. Для Vue CLI префикс
> `VUE_APP_` обязателен — иначе переменная не попадёт в бандл.

### 5. Установите зависимости

```powershell
# Backend
cd bekend
.\myvenv\Scripts\Activate.ps1
pip install -r requirements.txt   # установит aiogram 3.13.1

# Frontend (ничего нового не требуется — только перезапустить dev-сервер)
cd ..\frontend\sait-frontend
npm run serve
```

### 6. Запуск

```powershell
# Терминал 1 — API
cd bekend\room-sait
uvicorn main:app --reload

# Терминал 2 — Бот
cd bekend\room-sait
python run_bot.py
```

## Формат payload

Клиент кодирует такую строку:

```
checkin=2025-06-10&checkout=2025-06-14&guests=2&price=24000&prepay=6000&room=3
```

Затем URL-safe base64 без `=`:

```
Y2hlY2tpbj0yMDI1LTA2LTEwJmNoZWNrb3V0PTIwMjUtMDYtMTQmZ3Vlc3RzPTImcHJpY2U9MjQwMDAmcHJlcGF5PTYwMDAmcm9vbT0z
```

Итог: `https://t.me/<bot>?start=<payload>`. Telegram ограничивает `start` 64-мя
символами — для нашего набора полей влезает свободно.

## Рекомендации по безопасности

- **Payload — не доверенный источник.** Клиент может подменить цену. При реальной
  интеграции оплаты пересчитывайте стоимость на backend по `room + dates + guests`,
  используя существующий API расчёта цены.
- **Токен бота** храните только в `.env`, никогда не коммитьте. В `.gitignore`
  убедитесь, что `bekend/room-sait/.env` игнорируется (уже так).
- Если понадобится webhook вместо polling — добавьте HTTPS-эндпоинт (или через
  `ngrok` в dev) и используйте `Bot.set_webhook`. Webhook быстрее, но требует
  публичного URL.
- Rate-limit: aiogram сам ретраит при 429; для менеджера можно добавить
  де-дупликацию одинаковых заявок в короткий промежуток времени.

## UX-улучшения (предложения)

1. После `telegram-click` показывать маленький toast «Открываем Telegram…» — на случай
   блокировки popup браузером (сейчас `target="_blank"`, новая вкладка обычно
   разрешена, но не всегда).
2. Для десктопа без Telegram-клиента давать QR-код (через `qrcode.vue` / CDN),
   чтобы клиент мог отсканировать телефоном.
3. В самом боте после `/start` предлагать inline-кнопки: «Позвонить менеджеру»,
   «Спросить об уточнениях», «Отменить заявку».
4. Сохранять заявку в БД (новая таблица `booking_requests`), чтобы менеджер мог
   вернуться к ней из админки — ТЗ пока это запрещает, но архитектура к этому готова
   (добавить вызов нового API в `on_start_with_payload`).
