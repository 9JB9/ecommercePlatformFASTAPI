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
from schemas import CartItemResponse, CartItemCreate, CartItemUpdate

router = APIRouter()

# GET, Access items in cart
@router.get(
    "/{user_id}",
    response_model=list[CartItemResponse],
)
def get_cart_items(user: Annotated[models.User, Depends(get_existing_user)], db: Annotated[Session, Depends(get_db)]):

    cart_items = db.execute(
        select(models.CartItem)
        .options(selectinload(models.CartItem.product))
        .where(models.CartItem.user_id == user.user_id)
    ).scalars().all()

    return cart_items

# POST, Add item to cart
@router.post(
    "/{user_id}",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED
)
def add_item_to_cart(item: CartItemCreate, user: Annotated[models.User, Depends(get_existing_user)], db: Annotated[Session, Depends(get_db)]):

    # verify item.product_id is an actual product (not sure if necessary)
    existing_product = db.execute(
        select(models.Product).
        where(models.Product.product_id == item.product_id)
    ).scalars().first()

    if not existing_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # if item exists in cart, increase quantity by 1
    existing_cart_item = db.execute(
        select(models.CartItem).where(models.CartItem.user_id == user.user_id).where(models.CartItem.product_id == item.product_id)
    ).scalars().first()

    if existing_cart_item:
        existing_cart_item.quantity += 1
        db.commit()
        db.refresh(existing_cart_item, attribute_names=["user", "product"])
        return existing_cart_item

    # add item to database
    new_item = models.CartItem(
        user_id=user.user_id,
        product_id=item.product_id,
        quantity=1
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item, attribute_names=["product"])

    return new_item

# PATCH, Edit item in cart
@router.patch(
    "/{user_id}/{cart_item_id}",
    response_model=CartItemResponse,
)
def update_cart_item(cart_item_id: int, item: CartItemUpdate, user: Annotated[models.User, Depends(get_existing_user)], db: Annotated[Session, Depends(get_db)]):

    existing_cart_item = db.execute(
        select(models.CartItem)
        .where(models.CartItem.cart_item_id == cart_item_id)
        .where(models.CartItem.user_id == user.user_id)
    ).scalars().first()

    if not existing_cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    existing_cart_item.quantity = item.quantity
    db.commit()
    db.refresh(existing_cart_item, attribute_names=["product"])

    return existing_cart_item

# DELETE, Delete item in cart
@router.delete(
    "/{user_id}/{cart_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_cart_item(cart_item_id: int, user: Annotated[models.User, Depends(get_existing_user)], db: Annotated[Session, Depends(get_db)]):

    existing_cart_item = db.execute(
        select(models.CartItem)
        .where(models.CartItem.cart_item_id == cart_item_id)
        .where(models.CartItem.user_id == user.user_id)
    ).scalars().first()

    if not existing_cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    db.delete(existing_cart_item)
    db.commit()

# DELETE, Delete all items in cart
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_all_cart_items(user: Annotated[models.User, Depends(get_existing_user)], db: Annotated[Session, Depends(get_db)]):

    cart_items = db.execute(
        select(models.CartItem).where(models.CartItem.user_id == user.user_id)
    ).scalars().all()

    for cart_item in cart_items:
        db.delete(cart_item)

    db.commit()
