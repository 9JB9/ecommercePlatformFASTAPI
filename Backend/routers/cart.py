from typing import Annotated

# Fastapi 
from fastapi import Depends, status, HTTPException, APIRouter

# Database
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
import models

# Schemas
from schemas import CartItemResponse, CartItemCreate, OrderResponse

router = APIRouter()

"""
Brainstorming
Must be same user

GET Access items in cart
POST Add item to cart
PATCH Edit item in cart
    -increase amount or decrease
DELETE Delete item in cart
POST Checkout cart items
"""

# GET, Access items in cart
@router.get(
    "/{user_id}",
    response_model=list[CartItemResponse],
)
def get_cart_items(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.CartItem).where(models.CartItem.user_id == user_id)
    )

    cart_items = result.scalars().all()

    return cart_items

# POST, Add item to cart
@router.post(
    "/{user_id}",
    response_model=CartItemResponse,
)
def add_item_to_cart(item: CartItemCreate, user_id: int, db: Annotated[Session, Depends(get_db)]):

    # if item exists in cart, increase quantity by 1 
    result = db.execute(
        select(models.CartItem).where(models.CartItem.user_id == user_id).where(models.CartItem.product_id == item.product_id)
    )

    existing_cart_item = result.scalars().first()

    if existing_cart_item:
        existing_cart_item.quantity += 1
        db.add(existing_cart_item)
        db.commit()
        db.refresh(existing_cart_item, attribute_names=["user", "product"])

    # verify item.product_id is an actual product (not sure if necessary)
    result = db.execute(
        select(models.Product).where(models.Product.id == item.product_id)
    )

    existing_product = result.scalars().first()

    if not existing_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "This product does not exist."})

    # add item to database
    new_item = models.CartItem(
        user_id=user_id,
        product_id=item.product_id,
        quantity=1
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item, attribute_names=["product"])

    return new_item

# POST, Checkout cart items
@router.post(
    "/{user_id}/checkout",
    response_model=OrderResponse,
)
def checkout_cart(item: CartItemCreate, user_id: int, db: Annotated[Session, Depends(get_db)]):
    # first, add order to database

    # then, add order items to database

    # delete cart items

