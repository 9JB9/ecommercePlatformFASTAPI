# Fastapi 
from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Database
from database import engine, Base

# Cross Origin Resource Sharing (front and backend connection)
from fastapi.middleware.cors import CORSMiddleware

from starlette.exceptions import HTTPException as StarletteHTTPException

from routers import cart, orders, products, users

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

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(cart.router, prefix="/api/cart", tags=["cart"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])


# Handle General HTTP Errors
@app.exception_handler(StarletteHTTPException)
def handle_general_http_errors(request: Request, exception: StarletteHTTPException):

    message = {"detail": exception.detail}

    return JSONResponse(
        content=message,
        status_code=exception.status_code
    )

# Handle Validation Errors
@app.exception_handler(RequestValidationError)
def handle_validation_errors(request: Request, exception: RequestValidationError):
    return JSONResponse(
            content=exception.errors(),
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    )
