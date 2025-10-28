# AITI Guru Test - REST API для управления заказами

REST API сервис для добавления товаров в заказы с проверкой остатков на складе.

## Технологический стек

- Python 3.13 Alpine
- FastAPI
- PostgreSQL 18
- SQLAlchemy 2.0 (async)
- Alembic
- Docker & Docker Compose
- Poetry

## Структура БД

- `categories` - иерархические категории товаров
- `products` - товары с ценой и количеством на складе
- `clients` - клиенты
- `orders` - заказы клиентов
- `order_items` - позиции в заказах

## Быстрый старт

```bash
# Запуск всех сервисов (PostgreSQL + миграции + API)
docker-compose up -d

# Проверка
curl http://localhost:8000/docs
```

## API Endpoints

### POST `/api/v1/orders/add-item`
Добавление товара в заказ

**Запрос:**
```json
{
  "order_id": 1,
  "product_id": 5,
  "quantity": 2
}
```

**Ответ:**
```json
{
  "id": 10,
  "order_id": 1,
  "product_id": 5,
  "quantity": 2,
  "price": "1299.99"
}
```

**Ошибки:**
- `404` - заказ или товар не найдены
- `422` - недостаточно товара на складе

### GET `/api/v1/orders/{order_id}`
Получение информации о заказе

## Работа с миграциями

Миграции применяются автоматически при `docker-compose up`.

### Создание новых миграций (интерактивный режим)
```bash
# Запустить контейнер миграций в интерактивном режиме
MIGRATIONS_INTERACTIVE=true docker-compose up -d migrations

# Подключиться к контейнеру
docker exec -it aiti_migrations sh

# Создать новую миграцию
cd /app/api
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Тестирование

```bash
# Запустить тесты внутри API контейнера
docker exec -it aiti_api /app/scripts/run_tests.sh

# Или короче
docker exec -it aiti_api bash /app/scripts/run_tests.sh
```

## Локальная разработка

```bash
# Установить зависимости
poetry install

# Запустить API (PostgreSQL должен быть запущен)
cd api
alembic upgrade head
uvicorn api.main:app --reload

# Запустить тесты локально
pytest tests/ -v
```

## Переменные окружения

Основные переменные в `.env`:
- `POSTGRES_USER` - пользователь БД (по умолчанию: aiti_user)
- `POSTGRES_PASSWORD` - пароль БД (по умолчанию: aiti_password)
- `POSTGRES_DB` - имя БД (по умолчанию: aiti_db)
- `POSTGRES_HOST` - хост БД (по умолчанию: postgres)
- `POSTGRES_PORT` - порт БД (по умолчанию: 5432)

## Документация API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health
