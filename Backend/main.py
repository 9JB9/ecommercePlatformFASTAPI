from typing import Annotated

# Fastapi 
from fastapi import Depends, FastAPI, status, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Database
from database import engine, Base, get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
import models

# Cross Origin Resource Sharing (front and backend connection)
from fastapi.middleware.cors import CORSMiddleware

# Schemas
from schemas import SneakerResponse, UserResponse, UserCreate

from starlette.exceptions import HTTPException as StarletteHTTPException

import routers

# Table creation in database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(routers.users, prefix="/api/users", tags=["users"])
app.include_router(routers.cart, prefix="/api/cart", tags=["cart"])

# Get Sneakers
@app.get(
    "/api/sneakers",
    response_model=list[SneakerResponse]
)
def get_sneakers(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Product))
    sneakers = result.scalars().all()
    return sneakers


# Handle General HTTP Errors
@app.exception_handler(StarletteHTTPException)
def handle_general_http_errors(request: Request, exception: StarletteHTTPException):

    message = {"detail": exception.detail if exception else "This endpoint does not exist."}

    return JSONResponse(
        content=message,
        status_code=status.HTTP_404_NOT_FOUND
    )

# Handle Validation Errors
@app.exception_handler(RequestValidationError)
def handle_validation_errors(request: Request, exception: StarletteHTTPException):
    return JSONResponse(
            content=exception.errors(),
            status_code=status.HTTP_404_NOT_FOUND
    )
