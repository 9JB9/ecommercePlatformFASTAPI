from typing import Annotated

# Fastapi 
from fastapi import Depends, status, HTTPException, APIRouter

# Database
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
import models

# Schemas
from schemas import UserResponse, UserCreate

router = APIRouter()

# Create User
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
        raise HTTPException(detail="User already exists", status_code=status.HTTP_404_NOT_FOUND)

    new_user = models.User(
        email= user.email,
        password= user.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
