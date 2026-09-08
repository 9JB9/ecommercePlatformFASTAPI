from pydantic import BaseModel, ConfigDict, EmailStr, Field
# from .models import Product

# Schemas related to 
class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    image_url: str
    gender: str
    link: str
    brand: str
    description: str
class SneakerResponse(BaseModel):
    Sneakers: list[ProductResponse]

