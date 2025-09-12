# 🗄️ Настройка базы данных PostgreSQL

## 🚀 Создание Vercel Postgres

### 1. В панели Vercel:
1. Откройте **бэкенд проект**
2. Перейдите в **Storage** → **Create Database**
3. Выберите **Postgres**
4. Назовите: `sagshop-db`
5. Выберите регион (ближайший)
6. Нажмите **Create**

### 2. Получите DATABASE_URL:
После создания скопируйте `DATABASE_URL` из настроек:
```
postgresql://username:password@host:port/database
```

### 3. Добавьте в Environment Variables:
- **Key**: `DATABASE_URL`
- **Value**: ваш DATABASE_URL
- **Environment**: All Environments

## 📊 Структура базы данных

### Таблицы:
- **users** - пользователи
- **models** - модели
- **files** - файлы
- **tickets** - тикеты поддержки
- **ticket_messages** - сообщения в тикетах
- **audit_logs** - логи аудита

### Связи:
- User → Tickets (1:many)
- Model → Files (1:many)
- Model → Tickets (1:many)
- Ticket → Messages (1:many)

## 🔧 После создания базы данных:

1. **Добавьте DATABASE_URL** в Environment Variables
2. **Перезапустите деплой** бэкенда
3. **Проверьте** что API работает с базой данных
4. **Создайте тестовые данные**

## 📝 SQL для создания таблиц:

```sql
-- Создание таблиц будет выполнено автоматически через SQLAlchemy
-- При первом запуске API создаст все необходимые таблицы
```

## 🧪 Тестирование:

После настройки проверьте:
- `https://api.gakshop.com/health` - должно работать
- `https://api.gakshop.com/docs` - документация API
- `https://gakshop.com` - фронтенд должен работать

## 🚨 Важно:

- **Не публикуйте** DATABASE_URL публично
- **Регулярно делайте** бэкапы
- **Мониторьте** использование
- **Настройте** индексы для производительности
