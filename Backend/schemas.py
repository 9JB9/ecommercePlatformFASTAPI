from pydantic import BaseModel, ConfigDict, EmailStr, Field
# from .models import Product

class SneakerResponse(BaseModel):
    product_id: int
    name: str
    price: float
    image_url: str
    gender: str
    link: str
    brand: str
    description: str

class UserBase(BaseModel):
    email: EmailStr
    # add username attribute

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int

class UserPrivate(UserPublic):
    email: EmailStr

class UserUpdate(BaseModel):
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None)

class Token(BaseModel):
    access_token: str
    token_type: str

class CartItemBase(BaseModel):
    product_id: int

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)

class CartItemResponse(BaseModel):
    cart_item_id: int
    quantity: int
    product: SneakerResponse

class OrderItemResponse(BaseModel):
    order_item_id: int
    item_name: str
    quantity: int

class OrderResponse(BaseModel):
    order_id: int
    total: int
    items: list[OrderItemResponse]
    user: UserPublic
