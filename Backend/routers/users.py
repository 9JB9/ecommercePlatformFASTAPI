import secrets
from typing import Annotated
from datetime import datetime, UTC, timedelta

# Fastapi
from fastapi import Depends, status, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select, func
import models

# Schemas
from schemas import UserPublic, UserCreate, UserUpdate, UserPrivate, Token

# Authentication
from auth import create_access_token, hash_password, verify_password, CurrentUser
from config import settings


router = APIRouter()


# Ownership check: the {user_id} in the path must be the user the token belongs to
def get_owned_user(user_id: int, user: CurrentUser) -> models.User:
    if user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user",
        )
    return user

OwnedUser = Annotated[models.User, Depends(get_owned_user)]

# POST, create user
@router.post(
    "",
    response_model=UserPrivate,
    status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):

    result = db.execute(
        select(models.User).where(func.lower(models.User.email) == user.email.lower())
    )

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(detail="User already exists", status_code=status.HTTP_409_CONFLICT)

    new_user = models.User(
        email= user.email.lower(),
        password_hash= hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

## login_for_access_token
@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    # Look up user by email (case-insensitive)
    # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email
    result = db.execute(
        select(models.User).where(
            func.lower(models.User.email) == form_data.username.lower(),
        ),
    )
    user = result.scalars().first()

    # Verify user exists and password is correct
    # Don't reveal which one failed (security best practice)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user id as subject
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.user_id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")

## get_current_user
# declared before /{user_id} so "me" is not parsed as a user id
@router.get("/me", response_model=UserPrivate)
def read_current_user(user: CurrentUser):
    """Get the currently authenticated user."""
    return user

# GET, get user
@router.get(
    "/{user_id}",
    response_model=UserPublic,
)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):

    existing_user = db.execute(
        select(models.User).where(models.User.user_id == user_id)
    ).scalars().first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return existing_user


# PATCH, update user
@router.patch(
    "/{user_id}",
    response_model=UserPrivate,
)
def update_user(user_update: UserUpdate, user: OwnedUser, db: Annotated[Session, Depends(get_db)]):

    update_data = user_update.model_dump(exclude_unset=True) # converted into dictionary
    current_password = update_data.pop("current_password", None)

    # changing credentials requires proving you know the current password,
    # so a stolen token alone cannot lock the owner out of their account
    if "password" in update_data or "email" in update_data:
        if not current_password or not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Current password is incorrect",
            )

    # if email is changing, make sure no other user already has it
    if "email" in update_data:
        email_taken = db.execute(
            select(models.User).where(func.lower(models.User.email) == update_data["email"].lower(), models.User.user_id != user.user_id)
        ).scalars().first()

        if email_taken:
            raise HTTPException(detail="Email already in use", status_code=status.HTTP_409_CONFLICT)

    for field, value in update_data.items():
        if field == "email":
            user.email = value.lower()
        elif field == "password":
            user.password_hash = hash_password(value)
        else:
            setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user

# DELETE, delete user
# will cascade delete all cart items too
# users with no orders are hard deleted
# users with orders are soft deleted + anonymized so order history is kept
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(user: OwnedUser, db: Annotated[Session, Depends(get_db)]):

    has_orders = db.execute(
        select(models.Order.order_id).where(models.Order.user_id == user.user_id).limit(1)
    ).first()

    if has_orders:
        # scrub personal data, the row stays so Order.user_id still points at something
        user.email = f"deleted-{user.user_id}@invalid.example" # .example is reserved (RFC 2606) and, unlike .invalid, passes EmailStr
        user.password_hash = hash_password(secrets.token_urlsafe(32)) # destroy the old hash, leave a well-formed one nothing can match
        user.deleted_at = datetime.now(UTC)
        user.cart_items.clear() # delete-orphan cascade removes the cart rows
    else:
        db.delete(user)
    db.commit()

