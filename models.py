from datetime import date, datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from enum import StrEnum


class ClosureDay(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reason: Optional[str] = Field(default=None)
    closure_date: date = Field(unique=True, index=True)


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    products: list["Product"] = Relationship(back_populates="category")


class UserRole(StrEnum):
    STANDARD = "standard"
    ADMIN = "admin"


class OrderStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
    role: UserRole = Field(default=UserRole.STANDARD)
    is_blocked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    username: str = Field(unique=True, index=True)

    orders: list["Order"] = Relationship(back_populates="user")


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    pickup_date: date
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    user_id: int = Field(foreign_key="user.id")

    user: User = Relationship(back_populates="orders")
    order_products: list["OrderProduct"] = Relationship(back_populates="order")
    order_menus: list["OrderMenu"] = Relationship(back_populates="order")


class OrderProduct(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")

    order: Order = Relationship(back_populates="order_products")
    product: "Product" = Relationship(back_populates="order_products")


class OrderMenu(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    order_id: int = Field(foreign_key="order.id")
    menu_id: int = Field(foreign_key="menu.id")
    
    order: Order = Relationship(back_populates="order_menus")
    menu: "Menu" = Relationship(back_populates="order_menus")


class Menu(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    price: float = Field(ge=0)
    start_date : date = Field(default_factory=lambda: datetime.now(timezone.utc).date())
    end_date : Optional[date] = Field(default=None)
    is_available: bool = Field(default=True)
    is_deleted: bool = Field(default=False)

    order_menus: list["OrderMenu"] = Relationship(back_populates="menu")
    menu_products: list["MenuProduct"] = Relationship(back_populates="menu")

class MenuProduct(SQLModel, table=True):
    quantity: int = Field(ge=1)
    menu_id: int = Field(primary_key=True, foreign_key="menu.id")
    product_id: int = Field(primary_key=True, foreign_key="product.id")

    menu: Menu = Relationship(back_populates="menu_products")
    product: "Product" = Relationship(back_populates="menu_products")

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    is_available: bool = Field(default=True)
    is_deleted: bool = Field(default=False)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    category: Optional[Category] = Relationship(back_populates="products")
    order_products: list["OrderProduct"] = Relationship(back_populates="product")
    menu_products: list["MenuProduct"] = Relationship(back_populates="product")

