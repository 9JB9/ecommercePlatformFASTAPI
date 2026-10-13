from typing import Annotated

# Fastapi
from fastapi import Depends, status, HTTPException, APIRouter, Query
# Database
from database import get_db
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
import models

# Dependencies
from auth import get_current_admin

# Schemas
from schemas import AdminUserDetail, AdminUserResponse, OrderResponse, OrderStatus, OrderStatusUpdate

# the dependency on the router itself protects every route below, a new route can't forget the admin check
router = APIRouter(dependencies=[Depends(get_current_admin)])

# which status an order may move to from its current one, anything not listed is rejected
ALLOWED_TRANSITIONS = {
    OrderStatus.PENDING: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED, OrderStatus.CANCELLED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}

# GET, Access every user (soft-deleted users included unless filtered out)
@router.get(
    "/users",
    response_model=list[AdminUserResponse],
)
def get_users(db: Annotated[Session, Depends(get_db)], include_deleted: bool = True):

    query = select(models.User).order_by(models.User.user_id)
    if not include_deleted:
        query = query.where(models.User.deleted_at.is_(None))

    return db.execute(query).scalars().all()

# GET, Access a single user and all of their orders
@router.get(
    "/users/{user_id}",
    response_model=AdminUserDetail,
)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):

    existing_user = db.execute(
        select(models.User)
        .options(selectinload(models.User.orders).selectinload(models.Order.items))
        .where(models.User.user_id == user_id)
    ).scalars().first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return existing_user

# GET, Access every order, newest first, optionally only one status
@router.get(
    "/orders",
    response_model=list[OrderResponse],
)
def get_orders(
    db: Annotated[Session, Depends(get_db)],
    status_filter: Annotated[OrderStatus | None, Query(alias="status")] = None, # still ?status= in the url, renamed so it doesn't shadow fastapi's status module
):

    query = (
        select(models.Order)
        .options(selectinload(models.Order.items), selectinload(models.Order.user))
        .order_by(models.Order.created_date.desc(), models.Order.order_id.desc()) # order_id breaks ties between orders made in the same instant
    )
    if status_filter is not None:
        query = query.where(models.Order.status == status_filter)

    return db.execute(query).scalars().all()

# PATCH, Move an order to its next status
@router.patch(
    "/orders/{order_id}/status",
    response_model=OrderResponse,
)
def update_order_status(order_id: int, update: OrderStatusUpdate, db: Annotated[Session, Depends(get_db)]):

    existing_order = db.execute(
        select(models.Order)
        .options(selectinload(models.Order.items), selectinload(models.Order.user))
        .where(models.Order.order_id == order_id)
    ).scalars().first()

    if not existing_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    current_status = OrderStatus(existing_order.status)
    if update.status not in ALLOWED_TRANSITIONS[current_status]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change order from {current_status} to {update.status}",
        )

    existing_order.status = update.status
    db.commit()
    db.refresh(existing_order, attribute_names=["items", "user"])

    return existing_order
