from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship, backref
from .base import Base

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey('categories.id'), index=True)
    products = relationship('Product', back_populates='category')
    
    children = relationship(
        'Category',
        backref=backref('parent', remote_side=[id]),
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        UniqueConstraint('name', 'parent_id', name='uq_category_parent_name'),
    )

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    price = Column(Numeric(10, 2), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), index=True)

    category = relationship('Category', back_populates='products')