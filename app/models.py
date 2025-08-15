from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(index=True, unique=True)
    name: str
    price: float  # VAT-exclusive
    stock: int
    categories_csv: str = Field(default="")  # simple CSV for demo

    def categories(self) -> list[str]:
        return [c.strip() for c in self.categories_csv.split(",") if c.strip()]

class Cart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_key: str = Field(index=True, unique=True)
    promo_csv: str = Field(default="")

    items: List["CartItem"] = Relationship(back_populates="cart")

    def promos(self) -> set[str]:
        return {c.strip().upper() for c in self.promo_csv.split(",") if c.strip()}

class CartItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="cart.id")
    product_id: int = Field(foreign_key="product.id")
    qty: int

    cart: Cart = Relationship(back_populates="items")
    product: Product = Relationship()

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_ex_vat: float
    discount: float
    vat: float
    shipping: float
    grand_total: float
    promo_csv: str = Field(default="")

    items: List["OrderItem"] = Relationship(back_populates="order")

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    sku: str
    name: str
    unit_price: float
    qty: int
    line_total: float

    order: Order = Relationship(back_populates="items")
