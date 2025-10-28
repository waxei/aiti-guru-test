from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional


class AddItemToOrderRequest(BaseModel):
    """Запрос на добавление товара в заказ"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "order_id": 1,
            "product_id": 5,
            "quantity": 2
        }
    })
    
    order_id: int = Field(..., description="ID заказа", gt=0)
    product_id: int = Field(..., description="ID номенклатуры (товара)", gt=0)
    quantity: int = Field(..., description="Количество товара", gt=0)


class OrderItemResponse(BaseModel):
    """Ответ с информацией о позиции заказа"""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 10,
                "order_id": 1,
                "product_id": 5,
                "quantity": 2,
                "price": "1299.99"
            }
        }
    )
    
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: Decimal


class ProductResponse(BaseModel):
    """Ответ с информацией о товаре"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    quantity: int
    price: Decimal
    category_id: Optional[int] = None


class OrderResponse(BaseModel):
    """Ответ с информацией о заказе"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    client_id: int
    created_at: datetime
    items: list[OrderItemResponse] = []


class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    detail: str

