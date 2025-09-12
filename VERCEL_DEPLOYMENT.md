# Деплой на Vercel

## Подготовка к деплою

Проект уже загружен на GitHub: https://github.com/semegn89/webappozon.git

## Шаги для деплоя на Vercel

### 1. Подключение репозитория к Vercel

1. Зайдите на [vercel.com](https://vercel.com)
2. Войдите в аккаунт или зарегистрируйтесь
3. Нажмите "New Project"
4. Выберите "Import Git Repository"
5. Найдите и выберите репозиторий `semegn89/webappozon`
6. Нажмите "Import"

### 2. Настройка проекта

**Root Directory:** `frontend`

**Build Command:** `npm run build`

**Output Directory:** `dist`

**Install Command:** `npm install`

### 3. Переменные окружения

В настройках проекта добавьте следующие переменные окружения:

```
VITE_API_URL=https://your-backend-api-url.vercel.app/api/v1
VITE_TELEGRAM_WEBAPP_URL=https://your-frontend-url.vercel.app
VITE_ENVIRONMENT=production
```

### 4. Деплой бэкенда (отдельно)

Для бэкенда нужно создать отдельный проект на Vercel:

1. Создайте новый проект
2. Выберите тот же репозиторий
3. **Root Directory:** `backend`
4. **Build Command:** `pip install -r requirements.txt`
5. **Output Directory:** `.` (точка)
6. **Install Command:** `pip install -r requirements.txt`

### 5. Переменные окружения для бэкенда

```
DATABASE_URL=postgresql://user:password@host:port/database
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_BOT_USERNAME=your_bot_username
TELEGRAM_WEBAPP_URL=https://your-frontend-url.vercel.app
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
ADMIN_USER_IDS=123456789,987654321
S3_ENDPOINT_URL=https://your-s3-endpoint.com
S3_ACCESS_KEY_ID=your_access_key
S3_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=your-bucket-name
DEBUG=false
ENVIRONMENT=production
```

### 6. Настройка базы данных

Рекомендуется использовать:
- **Vercel Postgres** (для простоты)
- **PlanetScale** (MySQL)
- **Supabase** (PostgreSQL)
- **Railway** (PostgreSQL)

### 7. Настройка Telegram Bot

После деплоя обновите настройки бота:

1. Установите webhook URL: `https://your-backend-url.vercel.app/webhook`
2. Обновите команды бота через @BotFather
3. Настройте WebApp URL в боте

### 8. Файловое хранилище

Для продакшена рекомендуется:
- **Vercel Blob** (простое решение)
- **AWS S3**
- **Cloudinary**
- **Uploadcare**

## Структура деплоя

```
Frontend (Vercel) → Backend (Vercel) → Database (Vercel Postgres/Supabase)
     ↓
Telegram Bot (отдельный сервер или Vercel Functions)
```

## Полезные команды

```bash
# Установка Vercel CLI
npm i -g vercel

# Деплой из локальной папки
vercel

# Деплой продакшен версии
vercel --prod

# Просмотр логов
vercel logs
```

## Мониторинг

После деплоя проверьте:
- ✅ Frontend доступен по HTTPS
- ✅ Backend API отвечает
- ✅ База данных подключена
- ✅ Telegram Bot работает
- ✅ WebApp открывается в Telegram

## Обновление

Для обновления просто сделайте push в main ветку:

```bash
git add .
git commit -m "Update"
git push origin main
```

Vercel автоматически пересоберет и задеплоит проект.

## Troubleshooting

### Проблемы с CORS
Добавьте в настройки Vercel:
```
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

### Проблемы с Telegram WebApp
Убедитесь что:
- URL использует HTTPS
- Домен добавлен в настройки бота
- initData корректно передается

### Проблемы с базой данных
- Проверьте строку подключения
- Убедитесь что БД доступна из Vercel
- Проверьте миграции
