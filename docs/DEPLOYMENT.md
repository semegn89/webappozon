# Руководство по развертыванию

## Требования

- Docker и Docker Compose
- PostgreSQL 15+
- Redis (опционально)
- Домен с SSL сертификатом
- Telegram Bot Token

## Быстрый старт

### 1. Клонирование и настройка

```bash
git clone <repository-url>
cd telegram-mini-app-catalog
```

### 2. Настройка переменных окружения

```bash
# Скопируйте пример конфигурации
cp env.example .env

# Отредактируйте .env файл
nano .env
```

Обязательные переменные:
- `TELEGRAM_BOT_TOKEN` - токен вашего бота
- `TELEGRAM_BOT_USERNAME` - username бота
- `TELEGRAM_WEBAPP_URL` - URL вашего веб-приложения
- `SECRET_KEY` - секретный ключ для подписи
- `JWT_SECRET_KEY` - ключ для JWT токенов
- `ADMIN_USER_IDS` - ID админов через запятую

### 3. Запуск через Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### 4. Инициализация базы данных

```bash
# Применение миграций (если используется Alembic)
docker-compose exec backend alembic upgrade head

# Или создание таблиц автоматически
docker-compose exec backend python -c "from app.core.database import engine, Base; import asyncio; asyncio.run(engine.run_sync(Base.metadata.create_all))"
```

## Ручная установка

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

### Bot

```bash
cd bot
pip install -r requirements.txt
python main.py
```

## Настройка Telegram Bot

### 1. Создание бота

1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Сохраните полученный токен

### 2. Настройка WebApp

1. Отправьте `/setmenubutton` боту @BotFather
2. Выберите вашего бота
3. Укажите URL вашего веб-приложения
4. Укажите текст кнопки (например, "Открыть приложение")

### 3. Настройка команд

Отправьте @BotFather:
```
/setcommands
@your_bot_username
start - Главное меню
models - Каталог моделей
my_tickets - Мои тикеты
admin - Админ-панель
help - Справка
```

## Настройка веб-сервера (Nginx)

### Конфигурация Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Webhook для бота
    location /webhook {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Мониторинг и логирование

### Логи

```bash
# Просмотр логов всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f bot
```

### Мониторинг

- Backend API: http://yourdomain.com/docs (Swagger UI)
- Health check: http://yourdomain.com/health
- Метрики: можно добавить Prometheus/Grafana

## Резервное копирование

### База данных

```bash
# Создание бэкапа
docker-compose exec postgres pg_dump -U user telegram_mini_app > backup.sql

# Восстановление
docker-compose exec -T postgres psql -U user telegram_mini_app < backup.sql
```

### Файлы

```bash
# Копирование загруженных файлов
tar -czf uploads_backup.tar.gz uploads/

# Восстановление
tar -xzf uploads_backup.tar.gz
```

## Обновление

```bash
# Остановка сервисов
docker-compose down

# Обновление кода
git pull

# Пересборка и запуск
docker-compose up -d --build

# Применение миграций (если есть)
docker-compose exec backend alembic upgrade head
```

## Безопасность

### Рекомендации

1. Используйте сильные пароли для БД
2. Настройте файрвол
3. Регулярно обновляйте зависимости
4. Используйте HTTPS
5. Настройте rate limiting
6. Регулярно делайте бэкапы

### Переменные окружения для продакшена

```bash
# Безопасность
SECRET_KEY=your-very-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# База данных
DATABASE_URL=postgresql://user:strong_password@localhost:5432/telegram_mini_app

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/webhook
TELEGRAM_WEBAPP_URL=https://yourdomain.com

# Файловое хранилище (рекомендуется S3)
S3_ENDPOINT_URL=https://your-s3-endpoint.com
S3_ACCESS_KEY_ID=your_access_key
S3_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=your-bucket-name

# Админы
ADMIN_USER_IDS=123456789,987654321

# Продакшен настройки
DEBUG=false
ENVIRONMENT=production
```

## Устранение неполадок

### Частые проблемы

1. **Бот не отвечает**
   - Проверьте токен бота
   - Убедитесь что webhook настроен правильно
   - Проверьте логи бота

2. **Ошибки аутентификации**
   - Проверьте SECRET_KEY
   - Убедитесь что initData от Telegram корректный
   - Проверьте время на сервере

3. **Проблемы с файлами**
   - Проверьте права доступа к директории uploads
   - Убедитесь что S3 настроен правильно (если используется)
   - Проверьте размер файлов

4. **Ошибки базы данных**
   - Проверьте подключение к PostgreSQL
   - Убедитесь что таблицы созданы
   - Проверьте логи БД

### Полезные команды

```bash
# Проверка статуса сервисов
docker-compose ps

# Перезапуск сервиса
docker-compose restart backend

# Подключение к БД
docker-compose exec postgres psql -U user telegram_mini_app

# Очистка логов
docker-compose logs --tail=0 -f
```
