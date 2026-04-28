# sait-frontend - Фронтенд гостевого дома "Виноградная Лоза"

## Обзор проекта

Это клиентское веб-приложение (Vue.js 3) для гостевого дома "Виноградная Лоза", расположенного на Южном берегу Крыма (Алушта, с. Рыбачье). Приложение предоставляет интерфейс для:

- Просмотра номеров и их деталей с фото-галереей
- Бронирования номеров с выбором дат и количества гостей
- Управления сайтом через админ-панель (требует superuser)
- Просмотра статистики бронирований
- Аутентификации и регистрации пользователей

## Технологии и зависимости

### Основные зависимости
- **Vue.js 3.2.13** - UI фреймворк (Composition API + Options API)
- **Vue Router 4.5.0** - маршрутизация с guards для защиты маршрутов
- **Axios 1.7.9** - HTTP клиент с JWT interceptor
- **ApexCharts 5.10.6** + **vue3-apexcharts** - графики и диаграммы для статистики
- **Core.js 3.8.3** - полифиллы

### Dev-зависимости
- **Vue CLI 5.0** - сборка и инструменты разработки
- **ESLint 7.32** + **eslint-plugin-vue** - линтинг кода
- **Babel 7.12** - транспиляция JavaScript

## Структура проекта

```
sait-frontend/
├── public/
│   ├── index.html              # HTML шаблон
│   └── favicon.ico
├── src/
│   ├── main.js                 # Точка входа (Vue app, router, axios interceptor)
│   ├── App.vue                 # Корневой компонент (навигация, футер, уведомления)
│   ├── router.js               # Маршруты Vue Router с auth guards
│   └── components/
│       ├── MainStr.vue         # Главная страница (Hero, О нас, Преимущества, Номера, FAQ, Отзывы)
│       ├── RoomDetail.vue      # Детальная страница номера с бронированием
│       ├── RoomComponent.vue   # Карточка номера
│       ├── AdminRooms.vue      # Админ-панель управления номерами
│       ├── AdminSitePanel.vue  # Админ-панель управления сайтом
│       ├── StatisticksBooking.vue # Статистика бронирований
│       ├── BookingForm.vue     # Форма бронирования
│       ├── DateRangePicker.vue # Выбор диапазона дат
│       ├── SearchForm.vue      # Форма поиска
│       ├── PhotoLightbox.vue   # Лайтбокс для фото
│       ├── PhotoModal.vue      # Модальное окно фото
│       ├── CalendarStatus.vue  # Статусы календаря
│       ├── GuestsInput.vue     # Ввод количества гостей
│       ├── Admin/              # Компоненты админ-панели
│       │   ├── AdminHeader.vue
│       │   ├── AdminPanel.vue
│       │   ├── AmenityManager.vue      # Управление удобствами
│       │   ├── BedOptionManager.vue    # Управление вариантами кроватей
│       │   ├── BookingManager.vue      # Управление бронированиями
│       │   ├── NotifivationMesage.vue  # Уведомления
│       │   ├── PhotoManager.vue        # Управление фото
│       │   ├── PriceManager.vue        # Управление ценами
│       │   ├── RoomForm.vue            # Форма номера
│       │   ├── RoomList.vue            # Список номеров
│       │   └── SyncDateRangePicker.vue
│       └── Auth/
│           ├── UserLogin.vue   # Страница входа
│           └── SignUp.vue      # Страница регистрации
│   └── assets/
│       ├── main.css            # Дизайн-система (CSS variables, компоненты, утилиты)
│       ├── admin-site-panel.css
│       ├── logo.png
│       ├── rybache1.jpg
│       └── icons/
├── package.json
├── vue.config.js
├── babel.config.js
└── jsconfig.json
```

## Маршруты приложения

- `/` - главная страница (MainStr)
- `/room/:id` - детальная информация о номере
- `/login` - вход в систему
- `/signup` - регистрация
- `/admin/site` - управление сайтом (требует superuser)
- `/admin/rooms` - управление номерами (требует superuser)
- `/admin/stats` - статистика бронирований (требует superuser)

## Архитектурные особенности

### Аутентификация
- JWT токены хранятся в `localStorage` (`access_token`)
- Axios interceptor автоматически добавляет `Authorization: Bearer <token>` ко всем запросам
- Vue Router guards проверяют `is_superuser` для админ-маршрутов
- Автоматический logout при истечении сессии

### Дизайн-система
- CSS Custom Properties в `main.css` определяют всю дизайн-систему
- Цветовая палитра: теплый коралловый (#FF5A5F) как основной цвет
- Вдохновление: Sutochno.ru, Airbnb
- Адаптивный дизайн (mobile-first)
- Компоненты: кнопки, карточки, формы, бейджи, сетки
- Анимации: fadeIn, slideUp, slideDown

### API
- Backend API на `http://localhost:8000`
- CORS настроен на `http://localhost:8080` (Vue dev server)

### Компоненты
- Vue 3 Composition API и Options API используются совместно
- Реактивность через `v-model`, `computed`, `watch`
- Передача данных через props и emits
- Vue transitions для анимаций (fade, slide-down)

## Сборка и запуск

### Установка зависимостей
```bash
npm install
```

### Запуск dev-сервера (с hot-reload)
```bash
npm run serve
```
Сервер запустится на `http://localhost:8080`

### Продакшен сборка
```bash
npm run build
```
Собранные файлы будут в `dist/` директории

### Линтинг и исправление
```bash
npm run lint
```

## Конфигурация

### vue.config.js
```javascript
const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})
```

### Babel (babel.config.js)
Стандартная конфигурация Vue CLI с `core-js` для полифиллов

### ESLint
- Конфигурация: `plugin:vue/vue3-essential` + `eslint:recommended`
- Парсер: `@babel/eslint-parser`
- Поддержка Node.js окружения

## Backend интеграция

Фронтенд работает с backend API (FastAPI), расположенным в `../../bekend/room-sait/`.

### Основные endpoints
- `GET/POST /rooms/` - номера
- `GET /rooms/{id}/` - детали номера
- `POST /bookings/` - создание бронирования
- `POST /token/` - получение JWT токена
- `GET /users/me/` - информация о пользователе
- `POST /upload-icon` - загрузка иконок
- И другие (см. backend routers)

## Примечания по разработке

- Навигация скрывается на страницах входа/регистрации
- Админ-панель доступна только пользователям с `is_superuser=True`
- Фото номеров загружаются с backend (`http://localhost:8000/static/uploads/`)
- Иконки загружаются с backend (`http://localhost:8000/static/icons/`)
- Форма бронирования включает календарь с заблокированными датами
- Главная страница подгружает данные о сайте (описание, FAQ, отзывы) с backend

## Связанные проекты

- **Backend**: `../../bekend/room-sait/` (FastAPI + SQLAlchemy + SQLite)
- Полная документация backend доступна в `../../QWEN.md`
