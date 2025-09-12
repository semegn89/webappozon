# Telegram Mini App - Каталог моделей, инструкции и поддержка

Telegram Mini App для просмотра каталога моделей, скачивания инструкций и создания тикетов поддержки.

## Архитектура

- **Frontend**: React + TypeScript + Vite + Telegram Web Apps API
- **Backend**: FastAPI + PostgreSQL + SQLAlchemy
- **File Storage**: S3-совместимое хранилище с подписанными URL
- **Bot**: Python + python-telegram-bot

## Структура проекта

```
├── frontend/          # React приложение
├── backend/           # FastAPI сервер
├── bot/              # Telegram бот
├── database/         # SQL схемы и миграции
├── docker/           # Docker конфигурации
└── docs/             # Документация
```

## Быстрый старт

1. Установите зависимости:
```bash
npm run install:all
```

2. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл
```

3. Запустите базу данных:
```bash
docker-compose up -d postgres
```

4. Примените миграции:
```bash
cd backend && alembic upgrade head
```

5. Запустите приложение:
```bash
npm run dev
```

## Переменные окружения

См. `.env.example` для полного списка необходимых переменных.

## API Документация

После запуска бэкенда доступна по адресу: http://localhost:8000/docs

## Роли пользователей

- **user**: просмотр каталога, создание тикетов, просмотр своих тикетов
- **admin**: полный доступ к админ-панели, управление моделями и тикетами

## Команды Telegram бота

- `/start` - приветствие и открытие Mini App
- `/models` - открытие каталога моделей
- `/my_tickets` - просмотр своих тикетов
- `/admin` - админ-панель (только для админов)
