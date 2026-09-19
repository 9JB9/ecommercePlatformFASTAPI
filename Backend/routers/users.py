from typing import Annotated

# Fastapi 
from fastapi import Depends, status, HTTPException, APIRouter
from fastapi.responses import JSONResponse

# Database
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
import models

# Schemas
from schemas import UserResponse, UserCreate, UserUpdate

# Dependencies
from dependencies import get_existing_user

router = APIRouter()

# GET, get user
@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(user: Annotated[models.User, Depends(get_existing_user)]):

    return user

# POST, create user
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):

    result = db.execute(
        select(models.User).where(models.User.email == user.email)
    )

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(detail="User already exists", status_code=status.HTTP_409_CONFLICT)

    new_user = models.User(
        email= user.email,
        password= user.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# PATCH, update user
@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(user_update: UserUpdate, user: Annotated[models.User, Depends(get_existing_user)], db: Annotated[Session, Depends(get_db)]):

    update_data = user_update.model_dump(exclude_unset=True)

    # if email is changing, make sure no other user already has it
    if "email" in update_data:
        email_taken = db.execute(
            select(models.User).where(models.User.email == update_data["email"], models.User.user_id != user.user_id)
        ).scalars().first()

        if email_taken:
            raise HTTPException(detail="Email already in use", status_code=status.HTTP_409_CONFLICT)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user

# DELETE, delete user
# will cascade delete all cart items too
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(user: Annotated[models.User, Depends(get_existing_user)], db: Annotated[Session, Depends(get_db)]):

    db.delete(user)
    db.commit()




# For testing only

# Delete all User
# will cascade delete all cart items too
# @router.delete(
#     "/delete-all-users"
# )
# def delete_users(db: Annotated[Session, Depends(get_db)]):
#     users = db.execute(select(models.User)).scalars().all()

#     for user in users:
#         db.delete(user)

#     db.commit()
    
#     return JSONResponse(content={"message": "successfully deleted all users"})