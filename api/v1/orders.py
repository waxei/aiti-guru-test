from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.db import get_db
from api.models import Order, OrderItem, Product
from api.schemas import (
    AddItemToOrderRequest,
    OrderItemResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/add-item",
    response_model=OrderItemResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Неверный запрос"},
        404: {"model": ErrorResponse, "description": "Заказ или товар не найдены"},
        422: {"model": ErrorResponse, "description": "Недостаточно товара на складе"},
    },
    summary="Добавление товара в заказ",
    description="""
    Добавляет товар в заказ. Если товар уже есть в заказе, его количество увеличивается.
    
    **Бизнес-логика:**
    - Проверяет существование заказа
    - Проверяет существование товара
    - Проверяет наличие товара на складе
    - Если товар уже есть в заказе - увеличивает количество
    - Если товара нет в заказе - создает новую позицию
    - Уменьшает количество товара на складе
    """,
)
async def add_item_to_order(
    request: AddItemToOrderRequest,
    db: AsyncSession = Depends(get_db),
) -> OrderItemResponse:
    """
    Добавляет товар в заказ.
    
    Args:
        request: Запрос с ID заказа, ID товара и количеством
        db: Сессия базы данных
        
    Returns:
        OrderItemResponse: Информация о позиции заказа
        
    Raises:
        HTTPException 404: Если заказ или товар не найдены
        HTTPException 422: Если недостаточно товара на складе
    """
    
    # 1. Проверяем существование заказа
    order_query = select(Order).where(Order.id == request.order_id)
    order_result = await db.execute(order_query)
    order = order_result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с ID {request.order_id} не найден",
        )
    
    # 2. Проверяем существование товара и его количество
    product_query = select(Product).where(Product.id == request.product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Товар с ID {request.product_id} не найден",
        )
    
    # 3. Проверяем наличие товара на складе
    if product.quantity < request.quantity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Недостаточно товара на складе. "
                f"Запрошено: {request.quantity}, доступно: {product.quantity}"
            ),
        )
    
    # 4. Проверяем, есть ли товар уже в заказе
    order_item_query = select(OrderItem).where(
        OrderItem.order_id == request.order_id,
        OrderItem.product_id == request.product_id,
    )
    order_item_result = await db.execute(order_item_query)
    order_item = order_item_result.scalar_one_or_none()
    
    if order_item:
        # Товар уже есть в заказе - увеличиваем количество
        order_item.quantity += request.quantity
    else:
        # Товара нет в заказе - создаем новую позицию
        order_item = OrderItem(
            order_id=request.order_id,
            product_id=request.product_id,
            quantity=request.quantity,
            price=product.price,
        )
        db.add(order_item)
    
    # 5. Уменьшаем количество товара на складе
    product.quantity -= request.quantity
    
    # 6. Сохраняем изменения
    await db.commit()
    await db.refresh(order_item)
    
    return OrderItemResponse.model_validate(order_item)


@router.get(
    "/{order_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Заказ не найден"},
    },
    summary="Получение информации о заказе",
    description="Возвращает полную информацию о заказе со всеми позициями",
)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Получает информацию о заказе.
    
    Args:
        order_id: ID заказа
        db: Сессия базы данных
        
    Returns:
        dict: Информация о заказе с позициями
        
    Raises:
        HTTPException 404: Если заказ не найден
    """
    query = select(Order).where(Order.id == order_id).options(selectinload(Order.items))
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с ID {order_id} не найден",
        )
    
    return {
        "id": order.id,
        "client_id": order.client_id,
        "created_at": order.created_at,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": str(item.price),
            }
            for item in order.items
        ],
    }

