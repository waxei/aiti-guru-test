FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=2.2.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Добавляем Poetry в PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Устанавливаем системные зависимости
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && poetry --version

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости
RUN poetry install --no-root --only main

# Копируем код приложения
COPY api/ ./api/

# Создаем непривилегированного пользователя
RUN adduser -D -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

