import pytest
from httpx import AsyncClient


class TestAddItemToOrder:
    """Тесты эндпоинта POST /api/v1/orders/add-item"""
    
    @pytest.mark.asyncio
    async def test_add_item_success(self, client: AsyncClient, test_data):
        """Успешное добавление товара в заказ"""
        response = await client.post(
            "/api/v1/orders/add-item",
            json={
                "order_id": 1,
                "product_id": 1,
                "quantity": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == 1
        assert data["product_id"] == 1
        assert data["quantity"] == 2
        assert "price" in data
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_add_item_increases_quantity(self, client: AsyncClient, test_data):
        """Повторное добавление товара увеличивает количество"""
        # Первое добавление
        response1 = await client.post(
            "/api/v1/orders/add-item",
            json={"order_id": 1, "product_id": 1, "quantity": 2}
        )
        assert response1.status_code == 200
        first_quantity = response1.json()["quantity"]
        
        # Второе добавление того же товара
        response2 = await client.post(
            "/api/v1/orders/add-item",
            json={"order_id": 1, "product_id": 1, "quantity": 3}
        )
        assert response2.status_code == 200
        second_quantity = response2.json()["quantity"]
        
        assert second_quantity == first_quantity + 3
    
    @pytest.mark.asyncio
    async def test_add_item_order_not_found(self, client: AsyncClient, test_data):
        """Ошибка 404 если заказ не существует"""
        response = await client.post(
            "/api/v1/orders/add-item",
            json={"order_id": 999, "product_id": 1, "quantity": 1}
        )
        
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_add_item_product_not_found(self, client: AsyncClient, test_data):
        """Ошибка 404 если товар не существует"""
        response = await client.post(
            "/api/v1/orders/add-item",
            json={"order_id": 1, "product_id": 999, "quantity": 1}
        )
        
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_add_item_insufficient_stock(self, client: AsyncClient, test_data):
        """Ошибка 422 если товара недостаточно на складе"""
        response = await client.post(
            "/api/v1/orders/add-item",
            json={"order_id": 1, "product_id": 1, "quantity": 999}
        )
        
        assert response.status_code == 422
        assert "недостаточно" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_add_item_out_of_stock(self, client: AsyncClient, test_data):
        """Ошибка 422 если товара нет на складе (quantity=0)"""
        response = await client.post(
            "/api/v1/orders/add-item",
            json={"order_id": 1, "product_id": 2, "quantity": 1}
        )
        
        assert response.status_code == 422
        assert "недостаточно" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_add_item_invalid_quantity_zero(self, client: AsyncClient, test_data):
        """Ошибка валидации если quantity = 0"""
        response = await client.post(
            "/api/v1/orders/add-item",
            json={"order_id": 1, "product_id": 1, "quantity": 0}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_add_item_invalid_quantity_negative(self, client: AsyncClient, test_data):
        """Ошибка валидации если quantity < 0"""
        response = await client.post(
            "/api/v1/orders/add-item",
            json={"order_id": 1, "product_id": 1, "quantity": -5}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_add_item_missing_fields(self, client: AsyncClient, test_data):
        """Ошибка валидации если отсутствуют обязательные поля"""
        response = await client.post(
            "/api/v1/orders/add-item",
            json={"order_id": 1}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_add_item_invalid_types(self, client: AsyncClient, test_data):
        """Ошибка валидации если неверные типы данных"""
        response = await client.post(
            "/api/v1/orders/add-item",
            json={"order_id": "invalid", "product_id": 1, "quantity": 1}
        )
        
        assert response.status_code == 422


class TestGetOrder:
    """Тесты эндпоинта GET /api/v1/orders/{order_id}"""
    
    @pytest.mark.asyncio
    async def test_get_order_success(self, client: AsyncClient, test_data):
        """Успешное получение заказа"""
        response = await client.get("/api/v1/orders/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["client_id"] == 1
        assert "created_at" in data
        assert "items" in data
        assert isinstance(data["items"], list)
    
    @pytest.mark.asyncio
    async def test_get_order_with_items(self, client: AsyncClient, test_data):
        """Получение заказа с позициями"""
        # Добавляем товар в заказ
        await client.post(
            "/api/v1/orders/add-item",
            json={"order_id": 1, "product_id": 1, "quantity": 2}
        )
        
        # Получаем заказ
        response = await client.get("/api/v1/orders/1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
        assert data["items"][0]["product_id"] == 1
        assert data["items"][0]["quantity"] == 2
    
    @pytest.mark.asyncio
    async def test_get_order_not_found(self, client: AsyncClient, test_data):
        """Ошибка 404 если заказ не существует"""
        response = await client.get("/api/v1/orders/999")
        
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"].lower()


class TestHealthCheck:
    """Тесты служебных эндпоинтов"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Проверка health endpoint"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Проверка корневого endpoint"""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data

