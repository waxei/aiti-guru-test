import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from api.main import app
from api.models.base import Base
from api.models import Category, Product, Client, Order
from api.db.session import get_db


TEST_DATABASE_URL = "postgresql+asyncpg://aiti_user:aiti_password@postgres:5432/aiti_db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="function")
async def test_data(db_session: AsyncSession):
    """Создает тестовые данные для каждого теста"""
    
    # Категория и товар
    category = Category(id=1, name="Электроника")
    product_in_stock = Product(id=1, name="Товар А", quantity=10, price=1000.00, category_id=1)
    product_out_of_stock = Product(id=2, name="Товар Б", quantity=0, price=2000.00, category_id=1)
    
    # Клиент и заказ
    client = Client(id=1, name="Тестовый клиент", address="Тестовый адрес")
    order = Order(id=1, client_id=1)
    
    db_session.add_all([category, product_in_stock, product_out_of_stock, client, order])
    await db_session.commit()
    
    yield {
        "category": category,
        "product_in_stock": product_in_stock,
        "product_out_of_stock": product_out_of_stock,
        "client": client,
        "order": order,
    }
    
    # Очистка после теста
    await db_session.execute(Base.metadata.drop_all(bind=engine))
    await db_session.execute(Base.metadata.create_all(bind=engine))

