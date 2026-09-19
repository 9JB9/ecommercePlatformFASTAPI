from typing import Annotated

# Fastapi
from fastapi import Depends, status, HTTPException

# Database
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
import models


# Look up the user from the {user_id} path param, 404 if they don't exist
# (swap for get_current_user once auth/tokens exist)
def get_existing_user(user_id: int, db: Annotated[Session, Depends(get_db)]) -> models.User:

    existing_user = db.execute(
        select(models.User).where(models.User.user_id == user_id)
    ).scalars().first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return existing_user
