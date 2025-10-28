import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from api.main import app
from api.models.base import Base
from api.models import Category, Product, Client, Order
from api.db.session import get_db

# Используем отдельную тестовую БД!
TEST_DATABASE_URL = "postgresql+asyncpg://aiti_user:aiti_password@postgres:5432/aiti_test"
# URL для подключения к postgres БД (для создания тестовой БД)
POSTGRES_URL = "postgresql+asyncpg://aiti_user:aiti_password@postgres:5432/postgres"


@pytest_asyncio.fixture(scope="session")
async def create_test_database():
    """Создаем тестовую БД один раз перед всеми тестами"""
    engine = create_async_engine(POSTGRES_URL, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    
    async with engine.connect() as conn:
        # Проверяем, существует ли БД
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'aiti_test'")
        )
        exists = result.scalar()
        
        if not exists:
            await conn.execute(text("CREATE DATABASE aiti_test"))
            print("\n[TEST] Created test database 'aiti_test'")
        else:
            print("\n[TEST] Test database 'aiti_test' already exists")
    
    await engine.dispose()
    yield
    


@pytest_asyncio.fixture(scope="function")
async def engine(create_test_database):
    """Создаем новый engine для каждого теста с NullPool"""
    test_engine = create_async_engine(
        TEST_DATABASE_URL, 
        echo=False, 
        poolclass=NullPool  # Не кэшируем connections
    )
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    """Создаем новую сессию для каждого теста с чистой БД"""
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Пересоздаем схему
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """HTTP клиент для тестирования API с тестовой БД"""
    # Переопределяем dependency
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_data(db_session: AsyncSession):
    """Создает тестовые данные для каждого теста"""
    
    # Категория
    category = Category(id=1, name="Электроника")
    db_session.add(category)
    await db_session.flush()
    
    # Товары
    product_in_stock = Product(id=1, name="Товар А", quantity=10, price=1000.00, category_id=1)
    product_out_of_stock = Product(id=2, name="Товар Б", quantity=0, price=2000.00, category_id=1)
    db_session.add_all([product_in_stock, product_out_of_stock])
    await db_session.flush()
    
    # Клиент
    client_obj = Client(id=1, name="Тестовый клиент", address="Тестовый адрес")
    db_session.add(client_obj)
    await db_session.flush()
    
    # Заказ
    order = Order(id=1, client_id=1)
    db_session.add(order)
    await db_session.flush()
    
    await db_session.commit()
    
    yield {
        "category": category,
        "product_in_stock": product_in_stock,
        "product_out_of_stock": product_out_of_stock,
        "client": client_obj,
        "order": order,
    }
