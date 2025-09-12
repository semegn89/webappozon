# API Документация

## Аутентификация

Все API запросы требуют аутентификации через JWT токен, полученный после верификации Telegram WebApp initData.

### Получение токена

```http
POST /api/v1/auth/verify
Content-Type: application/json

{
  "init_data": "telegram_webapp_init_data_string"
}
```

**Ответ:**
```json
{
  "token": {
    "access_token": "jwt_token_here",
    "token_type": "bearer",
    "expires_at": "2024-01-01T12:00:00Z"
  },
  "user": {
    "id": 1,
    "telegram_user_id": 123456789,
    "username": "username",
    "first_name": "Имя",
    "last_name": "Фамилия",
    "language_code": "ru",
    "role": "user",
    "is_blocked": false,
    "full_name": "Имя Фамилия",
    "is_admin": false
  },
  "is_admin": false
}
```

### Использование токена

Добавьте заголовок `Authorization: Bearer <token>` ко всем запросам.

## Модели

### Получение списка моделей

```http
GET /api/v1/models?page=1&page_size=20&q=search&brand=brand&category=category
```

**Параметры:**
- `page` - номер страницы (по умолчанию 1)
- `page_size` - размер страницы (по умолчанию 20, максимум 100)
- `q` - поисковый запрос
- `brand` - фильтр по бренду
- `category` - фильтр по категории
- `year_from` - фильтр по году от
- `year_to` - фильтр по году до
- `has_files` - фильтр по наличию файлов (true/false)
- `is_active` - фильтр по активности (по умолчанию true)

**Ответ:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Название модели",
      "code": "MODEL-001",
      "brand": "Бренд",
      "category": "Категория",
      "year_from": 2020,
      "year_to": 2023,
      "description": "Описание модели",
      "image_url": "https://example.com/image.jpg",
      "is_active": true,
      "year_range": "2020-2023",
      "has_files": true,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

### Получение модели по ID

```http
GET /api/v1/models/{id}
```

### Создание модели (только админы)

```http
POST /api/v1/models
Content-Type: application/json

{
  "name": "Название модели",
  "code": "MODEL-001",
  "brand": "Бренд",
  "category": "Категория",
  "year_from": 2020,
  "year_to": 2023,
  "description": "Описание модели",
  "image_url": "https://example.com/image.jpg",
  "is_active": true
}
```

### Обновление модели (только админы)

```http
PUT /api/v1/models/{id}
Content-Type: application/json

{
  "name": "Новое название",
  "description": "Новое описание"
}
```

### Удаление модели (только админы)

```http
DELETE /api/v1/models/{id}
```

## Файлы

### Получение списка файлов

```http
GET /api/v1/files?model_id=1&page=1&page_size=20
```

### Получение информации о файле

```http
GET /api/v1/files/{id}
```

### Получение ссылки для скачивания

```http
GET /api/v1/files/{id}/download-url?expires_in_minutes=15
```

**Ответ:**
```json
{
  "download_url": "https://signed-url-here",
  "expires_at": "2024-01-01T12:15:00Z",
  "filename": "file.pdf",
  "size_bytes": 1024000
}
```

### Прямое скачивание файла

```http
GET /api/v1/files/{id}/download
```

### Загрузка файла (только админы)

```http
POST /api/v1/files/
Content-Type: multipart/form-data

file: <file>
title: "Название файла"
version: "1.0"
model_id: 1
```

### Обновление файла (только админы)

```http
PUT /api/v1/files/{id}
Content-Type: application/json

{
  "title": "Новое название",
  "is_public": true,
  "version": "1.1"
}
```

### Удаление файла (только админы)

```http
DELETE /api/v1/files/{id}
```

## Тикеты

### Получение списка тикетов

```http
GET /api/v1/tickets?status=open&priority=high&page=1&page_size=20
```

**Параметры:**
- `status` - фильтр по статусу (open, in_progress, resolved, closed)
- `priority` - фильтр по приоритету (low, normal, high)
- `assignee_id` - фильтр по назначенному (только для админов)
- `model_id` - фильтр по модели
- `user_id` - фильтр по пользователю (только для админов)

### Получение тикета по ID

```http
GET /api/v1/tickets/{id}
```

### Создание тикета

```http
POST /api/v1/tickets
Content-Type: application/json

{
  "subject": "Тема тикета",
  "description": "Описание проблемы",
  "priority": "normal",
  "model_id": 1
}
```

### Обновление тикета

```http
PUT /api/v1/tickets/{id}
Content-Type: application/json

{
  "status": "in_progress",
  "assignee_id": 2,
  "priority": "high"
}
```

### Получение сообщений тикета

```http
GET /api/v1/tickets/{id}/messages
```

### Создание сообщения в тикете

```http
POST /api/v1/tickets/{id}/messages
Content-Type: application/json

{
  "body": "Текст сообщения",
  "attachments": [],
  "is_internal_note": false
}
```

### Получение статистики тикетов (только админы)

```http
GET /api/v1/tickets/stats
```

**Ответ:**
```json
{
  "total": 100,
  "open": 20,
  "in_progress": 15,
  "resolved": 50,
  "closed": 15,
  "high_priority": 5
}
```

## Админские эндпоинты

### Получение списка пользователей (только админы)

```http
GET /api/v1/admin/users?page=1&page_size=20&role=admin&is_blocked=false
```

### Обновление пользователя (только админы)

```http
PUT /api/v1/admin/users/{id}
Content-Type: application/json

{
  "role": "admin",
  "is_blocked": false
}
```

### Получение общей статистики (только админы)

```http
GET /api/v1/admin/stats
```

**Ответ:**
```json
{
  "users": {
    "total": 100,
    "admins": 5,
    "blocked": 2
  },
  "models": {
    "total": 50,
    "active": 45
  },
  "files": {
    "total": 200
  },
  "tickets": {
    "total": 100,
    "open": 20,
    "high_priority": 5
  }
}
```

## Коды ошибок

- `400` - Неверный запрос
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Не найдено
- `422` - Ошибка валидации
- `429` - Превышен лимит запросов
- `500` - Внутренняя ошибка сервера

## Формат ошибок

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "name",
        "message": "Field is required"
      }
    ]
  }
}
```

## Rate Limiting

API имеет ограничения на количество запросов:
- 100 запросов в час на IP
- 1000 запросов в день на пользователя

При превышении лимита возвращается ошибка `429 Too Many Requests`.

## WebSocket (планируется)

В будущих версиях планируется добавление WebSocket для:
- Уведомлений о новых сообщениях в тикетах
- Обновлений статуса тикетов в реальном времени
- Уведомлений о новых тикетах для админов
