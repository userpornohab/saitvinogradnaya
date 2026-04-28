# QWEN.md - Проект: Система управления бронированием номеров

## Обзор проекта

Это полнофункциональное веб-приложение для управления бронированием номеров (room booking system) с админ-панелью. Состоит из:

- **Backend**: FastAPI (Python) - REST API с аутентификацией JWT
- **Frontend**: Vue.js 3 (JavaScript) - клиентское приложение с Vue Router

Приложение позволяет:
- Просматривать номера и их детали
- Создавать бронирования
- Управлять номерами, удобствами, тарифами через админ-панель
- Загружать фотографии и иконки
- Просматривать статистику бронирований

## Структура проекта

```
proekt2/
├── bekend/                      # Backend (FastAPI)
│   ├── room-sait/
│   │   ├── main.py              # Точка входа FastAPI
│   │   ├── config.py            # Настройки (JWT, DB)
│   │   ├── create_superuser.py  # Скрипт создания админа
│   │   ├── alembic.ini          # Конфигурация миграций
│   │   ├── auth/                # Аутентификация (JWT, пароли)
│   │   ├── database/            # Подключение к БД
│   │   ├── models/              # SQLAlchemy модели
│   │   ├── routers/             # API эндпоинты
│   │   ├── schemas/             # Pydantic схемы валидации
│   │   ├── utils/               # Утилиты
│   │   ├── migrations/          # Миграции Alembic
│   │   └── static/              # Статические файлы (фото, иконки)
│   ├── requirements.txt         # Python зависимости
│   └── myvenv/                  # Виртуальное окружение
└── frontend/
    └── sait-frontend/           # Frontend (Vue.js 3)
        ├── src/
        │   ├── main.js          # Точка входа Vue
        │   ├── router.js        # Маршруты Vue Router
        │   ├── App.vue          # Корневой компонент
        │   └── components/      # Vue компоненты
        ├── package.json         # Node зависимости
        └── vue.config.js        # Конфигурация Vue CLI
```

## Ключевые модели данных

### Backend модели (`bekend/room-sait/models/`)

- **User** - пользователи системы (email, name, is_superuser)
- **Room** - номера (title, description, max_guests, floor, number_of_rooms)
- **Booking** - бронирования (room_id, check_in/out dates, guests, price, guest details)
- **Amenity** - удобства (name, icon)
- **BedOption** - варианты кроватей (name, icon)
- **PricePeriod** - ценовые периоды (start_date, end_date, price)
- **RoomPhoto** - фотографии номеров
- **SiteInfo** - информация о сайте (main_photo, main_description)
- **Testimonial** - отзывы
- **FAQ** - часто задаваемые вопросы

## API Endpoints (Backend)

### Аутентификация (`routers/auth.py`)
- `POST /register/` - регистрация пользователя
- `POST /token/` - получение JWT токена (login)
- `GET /users/me/` - информация о текущем пользователе
- `PUT /users/{user_id}/` - обновление пользователя

### Основные эндпоинты
- **Rooms** (`routers/rooms.py`) - CRUD номеров
- **Bookings** (`routers/bookings.py`) - управление бронированиями
- **Amenities** (`routers/amenities.py`) - управление удобствами
- **Bed Options** (`routers/bed_options.py`) - варианты кроватей
- **Price Periods** (`routers/price_periods.py`) - ценовые периоды
- **Site** (`routers/site.py`) - информация о сайте
- `POST /upload-icon` - загрузка иконок

## Frontend маршруты

- `/` - главная страница
- `/room/:id` - детальная информация о номере
- `/login` - вход
- `/signup` - регистрация
- `/admin/site` - управление сайтом (требует superuser)
- `/admin/rooms` - управление номерами (требует superuser)
- `/admin/stats` - статистика бронирований (требует superuser)

## Запуск и разработка

### Backend

1. **Активировать виртуальное окружение:**
   ```bash
   cd bekend
   myvenv\Scripts\activate  # Windows
   ```

2. **Установить зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настроить переменные окружения:**
   Создать файл `.env` в `bekend/room-sait/`:
   ```
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///./database.db
   ```

4. **Запустить сервер:**
   ```bash
   cd bekend/room-sait
   uvicorn main:app --reload
   ```
   Сервер запустится на `http://localhost:8000`

5. **Создать суперпользователя:**
   ```bash
   python create_superuser.py admin@example.com password123
   ```

### Frontend

1. **Установить зависимости:**
   ```bash
   cd frontend/sait-frontend
   npm install
   ```

2. **Запустить dev-сервер:**
   ```bash
   npm run serve
   ```
   Сервер запустится на `http://localhost:8080`

3. **Сборка для продакшена:**
   ```bash
   npm run build
   ```

4. **Линтинг:**
   ```bash
   npm run lint
   ```

## Технологии и зависимости

### Backend
- **FastAPI** 0.115.3 - веб-фреймворк
- **SQLAlchemy** 2.0.40 - ORM
- **Pydantic** 2.11.3 - валидация данных
- **python-jose** - JWT токены
- **bcrypt** + **passlib** - хеширование паролей
- **uvicorn** - ASGI сервер
- **Alembic** - миграции БД
- **SQLite** - база данных (по умолчанию)

### Frontend
- **Vue.js 3** - UI фреймворк (Composition API)
- **Vue Router 4** - маршрутизация
- **Axios** - HTTP клиент
- **Vue CLI 5** - сборка и инструменты
- **ESLint** - линтинг
- **Babel** - транспиляция JS

## Архитектурные особенности

### Аутентификация
- JWT токены с expiration (30 минут по умолчанию)
- Axios interceptor автоматически добавляет `Authorization: Bearer <token>` к запросам
- Guard'ы в Vue Router защищают админ-маршруты (проверка `is_superuser`)

### CORS
- Backend настроен на `http://localhost:8080`
- Если фронтенд будет на другом порту/домене - обновить `allow_origins` в `main.py`

### Файлы
- Загруженные файлы сохраняются в `static/uploads/` и `static/icons/`
- Каскадное удаление файлов при удалении записей через SQLAlchemy events

### База данных
- По умолчанию используется SQLite
- Для production рекомендуется PostgreSQL/MySQL
- Alembic настроен для миграций

## Соглашения по разработке

### Backend
- Роутеры разделены по доменам (auth, rooms, bookings, и т.д.)
- SQLAlchemy модели в `models/`
- Pydantic схемы в `schemas/`
- Бизнес-логика в `utils/`
- Аутентификация в `auth/` (core.py, dependencies.py)

### Frontend
- Компоненты организованы по папкам: `Admin/`, `Auth/`
- Vue Router с `beforeEnter` guards для защищенных маршрутов
- Axios для всех HTTP запросов
- Компоненты используют Vue 3 Composition API или Options API

## Полезные команды

### Backend
```bash
# Запуск с автоперезагрузкой
uvicorn main:app --reload

# Запуск на определенном порту
uvicorn main:app --reload --port 8001

# Проверка миграций Alembic
alembic check

# Создание миграции
alembic revision --autogenerate -m "description"

# Применение миграций
alembic upgrade head
```

### Frontend
```bash
# Development сервер
npm run serve

# Продакшен сборка
npm run build

# Проверка кода
npm run lint
```

## Конфигурация

### Backend (.env файл)
```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./database.db
# Для PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Изменение CORS
В `main.py` обновить `allow_origins` если фронтенд на другом домене:
```python
allow_origins=["http://localhost:8080", "https://yourdomain.com"],
```

## Примечания

- Проект использует SQLite по умолчанию, что подходит для разработки
- Для production рекомендуется настроить PostgreSQL и proper secret management
- JWT токены хранятся в `localStorage` на фронтенде
- Админ-панель доступна только для пользователей с `is_superuser=True`
