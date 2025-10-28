from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Numeric, Text, DateTime
from sqlalchemy.orm import relationship, backref
from .base import Base
from datetime import datetime, UTC

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    address = Column(Text)
    
    orders = relationship('Order', back_populates='client', cascade="all, delete-orphan")

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), index=True)

    client = relationship('Client', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    order = relationship('Order', back_populates='items')
    # Здесь SQLAlchemy связывает 'Product' с моделью из файла products.py
    product = relationship('Product')