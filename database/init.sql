-- Инициализация базы данных для Telegram Mini App

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создание индексов для оптимизации
-- (Таблицы будут созданы через SQLAlchemy, здесь только индексы)

-- Настройка для лучшей производительности
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET pg_stat_statements.track = 'all';
