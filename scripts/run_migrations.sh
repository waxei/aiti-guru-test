#!/bin/bash
set -e

# --- ЛОВУШКА НА SIGTERM / SIGINT ---
# При получении сигнала docker stop → завершаемся корректно
trap 'echo "[MIGRATIONS] Received stop signal. Exiting cleanly..."; exit 0' TERM INT

echo "[MIGRATIONS] Starting migration service..."

# Проверяем режим работы
INTERACTIVE_MODE=${MIGRATIONS_INTERACTIVE:-"false"}
echo "[MIGRATIONS] Interactive mode: $INTERACTIVE_MODE"

# Ждем готовности PostgreSQL
echo "[MIGRATIONS] Waiting for PostgreSQL..."
until pg_isready -h ${POSTGRES_HOST:-postgres} -U ${POSTGRES_USER:-aiti_user} > /dev/null 2>&1; do
  echo "[MIGRATIONS] PostgreSQL not ready, waiting..."
  sleep 2
done
echo "[MIGRATIONS] PostgreSQL is ready!"

# Проверка подключения к БД
echo "[MIGRATIONS] Testing DB connection..."
python3 -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test():
    engine = create_async_engine('${POSTGRES_DSN}')
    async with engine.begin() as conn:
        await conn.execute(text('SELECT 1'))
    await engine.dispose()

asyncio.run(test())
"

if [ $? -eq 0 ]; then
    echo "[MIGRATIONS] DB connection OK"
else
    echo "[MIGRATIONS] DB connection failed!"
    exit 1
fi

# Если интерактивный режим, не завершаем контейнер
if [ "$INTERACTIVE_MODE" = "true" ]; then
    echo "[MIGRATIONS] Starting interactive mode..."
    echo "[MIGRATIONS] Available commands:"
    echo "  alembic revision --autogenerate -m 'description'  # Создать миграцию"
    echo "  alembic upgrade head                              # Применить миграции"
    echo "  alembic current                                   # Текущая версия"
    echo "  alembic history                                   # История миграций"
    echo "  alembic downgrade -1                              # Откатить последнюю миграцию"
    echo "  exit                                              # Выход (контейнер останется жить)"
    echo ""
    echo "[MIGRATIONS] Container will stay alive until stopped manually."
    echo "[MIGRATIONS] You can attach to it using:"
    echo "  docker exec -it aiti_migrations sh"
    echo ""
    tail -f /dev/null &
    wait $!
fi

# Выполнение миграций
echo "[MIGRATIONS] Running alembic upgrade head..."
cd /app/api
python -m alembic upgrade head

if [ $? -eq 0 ]; then
    echo "[MIGRATIONS] Schema migrations completed successfully ✓"
else
    echo "[MIGRATIONS] Schema migrations failed!"
    exit 1
fi

echo "[MIGRATIONS] All migrations completed successfully ✓"
exit 0

