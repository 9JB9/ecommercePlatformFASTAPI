from pydantic import BaseModel, ConfigDict, EmailStr, Field
# from .models import Product

class SneakerResponse(BaseModel):
    id: int
    name: str
    price: float
    image_url: str
    gender: str
    link: str
    brand: str
    description: str

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

class CartItemBase(BaseModel):
    product_id: str 

class CartItemCreate(BaseModel):
    pass

class CartItemResponse(BaseModel):
    id: int
    quantity: int
    product: SneakerResponse

class OrderResponse(BaseModel):
    