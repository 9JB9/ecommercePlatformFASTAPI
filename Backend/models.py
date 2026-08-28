from sqlalchemy import ForeignKey, Integer, String, Text, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database import Base
from collections.abc import AsyncGenerator # this is going to be used to check for an async return value
from sqlalchemy.ext.asyncio import AsyncSession

"""
Some learning/refresher notes:
    1. inside of the mapped_column(), what is the primary_key and index attributes?
        a. primary_key -> tells the database that this column (named id, but name can be whatever you choose it to be)
           is the master identifier for every row in the table
        b. index=True -> creates an index (similar to that of a textxbook) for that column of the database, to make searching
           and finding values in a database easier (when found, a pointer points to the proper row). Not to be overused, since
           it is heavy on resource and can actually tank performance when inserting, updating and deleting things this way.
    2. relationship()?
        a. links two tables together on the python side... lets us use dot notation to access data, avoids all teh SQL jargon
        b. an argument is needed unless it is given in type annotation using Mapped (by argument, im talking about the tablename)
        c. back_populates helps keep data in sync, if change is made one way, it changes it for both IN-MEMORY, NOT DB ITSELF 
           (you are supposed to pass variablename, specifically the variablename from the other class that you are linking to)
    3. foreignkey
        a. in a many to one relationship, the foreignkey goes on the "many" side
        b. it behaves sort of like a pointer, but mechanically it runs a lot deeper (and it is not a pointer). It is a column that
           shows what other table this data belongs to... more or less.. you pass it the tablename along with the attribute you want
           to link it to
"""


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[int] = mapped_column(String) # figure out the restrictions later, if they are even to be applied here
    # figure out password and place it here... to tired to figure this part out because of how encryption plays a part, 
    # but i assume it will just come through as a string so i will leave that here for now
    password: Mapped[str] = mapped_column(String)
    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    cart_items: Mapped["CartItem"] = relationship(back_populates="user")

class Product(Base):
    # table of all the products and their information
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Numeric(10, 2)) # active price (not fixed)
    image_url: Mapped[str] = mapped_column(String)
    gender: Mapped[str] = mapped_column(String)
    link: Mapped[str] = mapped_column(String) # the stockx link
    brand: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

class OrderItem(Base):
    # this will represent an order as it is being procesed
    # implying all details are locked in (like a snapshot)
    # no longer relying on live data (this would require items to be updated, but we aren't making queries to the kickdb anymore)

    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fixed_price: Mapped[float] = mapped_column(Numeric(10,2))
    item_name: Mapped[str] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    # since this is supposed to represent a product that has been snapshot due to an order being placed
    # we nede to relate this back to the order itself

    order_id : Mapped[int] = mapped_column(ForeignKey("orders.id")) # orders being the name of the table its from and not the name of the class it's from :(
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id")) # tying the item to where the product originally comes from

    order: Mapped["Order"] = relationship(back_populates="items") # incomplete
    product: Mapped["Product"] = relationship() 
    
class CartItem(Base):
    # data that is mutable and prone to change.
    # queue before any order is made

    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)    

    user: Mapped["User"] = relationship(back_populates="cart_items")
    product: Mapped["Product"] = relationship() # no point in having cart_items in product, but product will never actually hold 
                                                # cart items... cart items just happen to be stored inside of product...

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String, default="pending")
    total: Mapped[float] = mapped_column(Numeric(10,2))
    created_date: Mapped[datetime] = mapped_column(DateTime)

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order") # sqlalchemy handles the list wrapper as a notice to return multiple rows, its pretty cool
    user: Mapped["User"] = relationship(back_populates="orders")

"""
    Quick note on AsyncGenerators... Python by default knows they exist, you don't need this import to have them work
    But unlike 'int' and 'str' and other built in types, there isn't a specific way to refer to async generators in python.
    Even though without the import if you check for the type of an async generator, it returns 'async_generator'... 
    In a nutshell, it just falls into, python not having it as a built in type you can refer to, but it is recognized by
    the interpreter...

    so that's where the import comes in. it gives you an abstract class to work with, that lets you refer to these 
    async generators... collections.abc are mostly purely for type annotations anyway (they are abstract classes)
    so this is not exactly CRUCIAL. But as far as my understanding of type annotation goes right now, especially with
    Pydantic and all this other type stuff, this is important to have either way.
"""

