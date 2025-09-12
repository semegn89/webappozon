# 📋 Импорт Environment Variables в Vercel

## 🚀 Быстрый способ - через импорт .env файла

### Для бэкенда проекта:

1. **Откройте** `backend/env.production`
2. **Скопируйте** весь содержимое файла
3. **В Vercel** → Backend Project → Settings → Environment Variables
4. **Нажмите** "Import .env"
5. **Вставьте** содержимое файла
6. **Нажмите** "Save"

### Для фронтенда проекта:

1. **Откройте** `frontend/env.production`
2. **Скопируйте** весь содержимое файла
3. **В Vercel** → Frontend Project → Settings → Environment Variables
4. **Нажмите** "Import .env"
5. **Вставьте** содержимое файла
6. **Нажмите** "Save"

## ⚠️ Важно изменить перед импортом:

### В backend/env.production:
```
# Замените на ваши реальные значения:
SECRET_KEY=your-super-secret-key-change-this-in-production-12345
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production-67890
ADMIN_USER_IDS=123456789,987654321
DATABASE_URL=postgresql://user:password@host:port/database
```

### Как получить значения:

#### SECRET_KEY и JWT_SECRET_KEY:
```bash
# Сгенерируйте случайные ключи:
openssl rand -hex 32
```

#### ADMIN_USER_IDS:
1. Напишите @userinfobot в Telegram
2. Он пришлет ваш ID
3. Добавьте ID через запятую: `123456789,987654321`

#### DATABASE_URL:
1. Создайте Vercel Postgres
2. Скопируйте URL из настроек

## 🔧 Ручной способ (если импорт не работает):

### Бэкенд Environment Variables:
```
TELEGRAM_BOT_TOKEN=7870121478:AAGtGNo-Hrx3Ox4OZsbuqZniexzeR_tl47w
TELEGRAM_BOT_USERNAME=SAGShop_bot
TELEGRAM_WEBAPP_URL=https://gakshop.com
DEBUG=false
ENVIRONMENT=production
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
ADMIN_USER_IDS=your-telegram-id-here
DATABASE_URL=your-database-url-here
```

### Фронтенд Environment Variables:
```
VITE_API_URL=https://api.gakshop.com/api/v1
VITE_TELEGRAM_WEBAPP_URL=https://gakshop.com
VITE_ENVIRONMENT=production
```

## ✅ После импорта:

1. **Перезапустите деплой** (Vercel сделает это автоматически)
2. **Проверьте логи** на наличие ошибок
3. **Протестируйте API** по адресу `https://api.gakshop.com/health`

## 🚨 Безопасность:

- **НЕ коммитьте** .env файлы в git
- **НЕ публикуйте** токены и ключи
- **Используйте** разные ключи для разных окружений
- **Регулярно меняйте** секретные ключи

## 📞 Если что-то не работает:

1. **Проверьте** правильность URL
2. **Убедитесь**, что все переменные добавлены
3. **Проверьте** логи Vercel
4. **Убедитесь**, что домены настроены
