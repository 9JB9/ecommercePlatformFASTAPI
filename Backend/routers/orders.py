from typing import Annotated

# Fastapi
from fastapi import Depends, status, HTTPException, APIRouter
# Database
from database import get_db
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
import models

# Dependencies
from dependencies import get_existing_user

# Schemas
from schemas import OrderResponse

router = APIRouter()

# POST, Checkout cart items (creates an order from the user's cart)
@router.post(
    "/{user_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def checkout_cart(user: Annotated[models.User, Depends(get_existing_user)], db: Annotated[Session, Depends(get_db)]):

    # if cart_items is empty, dont checkout
    cart_items = db.execute(
        select(models.CartItem)
        .options(selectinload(models.CartItem.product))
        .where(models.CartItem.user_id == user.user_id)
    ).scalars().all()

    if not cart_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    total = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)

    # add order to database
    new_order = models.Order(
        user_id=user.user_id,
        total=total,
    )
    db.add(new_order)
    db.flush()  # populate new_order.order_id for the order items below

    # add order items to database, delete cart items from database
    for cart_item in cart_items:
        db.add(models.OrderItem(
            order_id=new_order.order_id,
            product_id=cart_item.product_id,
            item_name=cart_item.product.name,
            fixed_price=cart_item.product.price,
            quantity=cart_item.quantity,
        ))
        db.delete(cart_item)

    db.commit()
    db.refresh(new_order, attribute_names=["items", "user"])

    return new_order

# GET, Access all of a user's orders
@router.get(
    "/{user_id}",
    response_model=list[OrderResponse],
)
def get_orders(user: Annotated[models.User, Depends(get_existing_user)], db: Annotated[Session, Depends(get_db)]):

    orders = db.execute(
        select(models.Order)
        .options(selectinload(models.Order.items), selectinload(models.Order.user))
        .where(models.Order.user_id == user.user_id)
    ).scalars().all()

    return orders

# GET, Access a single order
@router.get(
    "/{user_id}/{order_id}",
    response_model=OrderResponse,
)
def get_order(order_id: int, user: Annotated[models.User, Depends(get_existing_user)], db: Annotated[Session, Depends(get_db)]):

    existing_order = db.execute(
        select(models.Order)
        .options(selectinload(models.Order.items), selectinload(models.Order.user))
        .where(models.Order.order_id == order_id)
        .where(models.Order.user_id == user.user_id)
    ).scalars().first()

    if not existing_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return existing_order
