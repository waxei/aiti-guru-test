from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.v1 import orders_router

# Создаем приложение FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    REST API для управления заказами и товарами.
    
    Основной функционал:
    - Добавление товаров в заказ
    - Автоматическое увеличение количества для существующих позиций
    - Контроль остатков на складе
    - Иерархия категорий товаров
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(orders_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["health"])
async def root():
    """Проверка работоспособности API"""
    return {
        "status": "ok",
        "message": "AITI Guru Test API is running",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

