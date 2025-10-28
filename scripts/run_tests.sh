#!/bin/bash
set -e

echo "[TESTS] Starting test suite..."

# Ждем готовности PostgreSQL
echo "[TESTS] Waiting for PostgreSQL..."
until pg_isready -h postgres -U ${POSTGRES_USER:-aiti_user} > /dev/null 2>&1; do
  echo "[TESTS] PostgreSQL not ready, waiting..."
  sleep 2
done
echo "[TESTS] PostgreSQL is ready!"

# Применяем миграции если нужно
echo "[TESTS] Ensuring database schema is up to date..."
cd /app/api
alembic upgrade head 2>/dev/null || echo "[TESTS] Migrations already applied or not needed"

# Запускаем тесты
echo "[TESTS] Running pytest..."
cd /app
pytest tests/ -v --tb=short --disable-warnings

if [ $? -eq 0 ]; then
    echo "[TESTS] ✓ All tests passed!"
    exit 0
else
    echo "[TESTS] ✗ Some tests failed!"
    exit 1
fi

