from pydantic import BaseModel, ConfigDict, EmailStr, Field
# from .models import Product

# Schemas related to 
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


