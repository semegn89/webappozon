# 🚀 Production Setup Guide

## 1. Домены и URL

### Фронтенд
- **URL**: `https://gakshop.com`
- **Vercel Project**: Frontend project
- **Root Directory**: `frontend`

### Бэкенд  
- **URL**: `https://api.gakshop.com` (или `https://gakshop.com/api`)
- **Vercel Project**: Backend project
- **Root Directory**: `backend`

## 2. База данных

### Рекомендуется: Vercel Postgres
1. Создайте Vercel Postgres в панели Vercel
2. Скопируйте `DATABASE_URL`
3. Добавьте в Environment Variables бэкенда

### Альтернативы:
- **Supabase**: `https://supabase.com` (бесплатно)
- **Railway**: `https://railway.app` (просто)
- **Neon**: `https://neon.tech` (быстро)

## 3. Telegram Bot Setup

### Создание бота:
1. Напишите @BotFather в Telegram
2. `/newbot` - создайте нового бота
3. Получите `BOT_TOKEN`
4. Настройте команды:
   ```
   /setcommands
   start - Запустить приложение
   help - Помощь
   support - Поддержка
   ```

### Webhook (опционально):
```
https://api.gakshop.com/webhook/telegram
```

## 4. Environment Variables

### Фронтенд (Vercel):
```
VITE_API_URL=https://api.gakshop.com/api/v1
VITE_TELEGRAM_WEBAPP_URL=https://gakshop.com
VITE_ENVIRONMENT=production
```

### Бэкенд (Vercel):
```
DATABASE_URL=postgresql://user:pass@host:port/db
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_USERNAME=your_bot_username
TELEGRAM_WEBAPP_URL=https://gakshop.com
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
ADMIN_USER_IDS=123456789,987654321
DEBUG=false
ENVIRONMENT=production
```

## 5. DNS Настройки

### Для gakshop.com:
```
Type: A
Name: @
Value: 76.76.19.19 (Vercel IP)

Type: CNAME  
Name: www
Value: cname.vercel-dns.com

Type: CNAME
Name: api
Value: cname.vercel-dns.com
```

## 6. Проверка работы

### Тестовые URL:
- **Фронтенд**: `https://gakshop.com`
- **API Health**: `https://api.gakshop.com/health`
- **API Test**: `https://api.gakshop.com/test`
- **API Docs**: `https://api.gakshop.com/docs`

## 7. Telegram Web App

### Настройка в @BotFather:
1. `/newapp` - создайте новое приложение
2. **URL**: `https://gakshop.com`
3. **Description**: Каталог моделей, инструкции и поддержка
4. Получите `WEBAPP_URL`

### В коде бота:
```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def start(update, context):
    keyboard = [[InlineKeyboardButton("Открыть приложение", web_app=WebAppInfo(url="https://gakshop.com"))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Добро пожаловать!", reply_markup=reply_markup)
```

## 8. Мониторинг

### Vercel Analytics:
- Включите в настройках проекта
- Отслеживайте производительность

### Логи:
- Vercel Functions logs
- Database logs
- Error tracking

## 9. Безопасность

### HTTPS:
- ✅ Автоматически через Vercel
- ✅ SSL сертификаты

### CORS:
- ✅ Настроено для gakshop.com
- ✅ Настроено для *.vercel.app

### Rate Limiting:
- ✅ Настроено в коде
- ✅ 100 запросов/час

## 10. Backup

### База данных:
- Автоматические бэкапы Vercel Postgres
- Или настройте в Supabase/Railway

### Файлы:
- S3-совместимое хранилище
- Или локальное хранилище Vercel
