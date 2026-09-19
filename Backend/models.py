from sqlalchemy import ForeignKey, Integer, String, Text, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String)

    password: Mapped[str] = mapped_column(String)
    orders: Mapped[list["Order"]] = relationship(back_populates="user") # note that if user had orders and no cascade, error would occur
    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Numeric(10, 2)) # active price (not fixed)
    image_url: Mapped[str] = mapped_column(String)
    gender: Mapped[str] = mapped_column(String)
    link: Mapped[str] = mapped_column(String) # the stockx link
    brand: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

class OrderItem(Base):
    # table represents item that is ordered at time of purchase
    __tablename__ = "order_items"

    order_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fixed_price: Mapped[float] = mapped_column(Numeric(10,2))
    item_name: Mapped[str] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    order_id : Mapped[int] = mapped_column(ForeignKey("orders.order_id")) # orders being the name of the table its from and not the name of the class it's from :(
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id")) # tying the item to where the product originally comes from

    order: Mapped["Order"] = relationship(back_populates="items") # incomplete
    product: Mapped["Product"] = relationship() 
    
class CartItem(Base):
    # table represents a mutable queue before any order is made
    __tablename__ = "cart_items"

    cart_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    user: Mapped["User"] = relationship(back_populates="cart_items")
    product: Mapped["Product"] = relationship() # no point in having cart_items in product, but product will never actually hold 
                                                # cart items... cart items just happen to be stored inside of product...

class Order(Base):
    __tablename__ = "orders"
    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    status: Mapped[str] = mapped_column(String, default="pending")
    total: Mapped[float] = mapped_column(Numeric(10,2))
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order") # sqlalchemy handles the list wrapper as a notice to return multiple rows, its pretty cool
    user: Mapped["User"] = relationship(back_populates="orders")


