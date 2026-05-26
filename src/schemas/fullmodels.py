from pydantic import BaseModel
from typing import Optional
from datetime import datetime

##################   USER   #########################

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel): #WHAT I WANT TO RESPONSE, NO PW FOR SAFETY REASONS
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


##################   ORDER   #########################

class OrderCreate(BaseModel):
    total: int
    purchased_on: datetime

class OrderUpdate(BaseModel):
    total: Optional[int] = None
    purchased_on: Optional[datetime] = None

class OrderResponse(BaseModel):
    id: int
    total: int
    purchased_on: datetime

    class Config:
        from_attributes = True


##################   ORDER_ITEM   #########################

class OrderItemCreate(BaseModel):
    quantity: int
    unit_price: int

class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[int] = None

class OrderItemResponse(BaseModel):
    id: int
    quantity: int
    unit_price: int

    class Config:
        from_attributes = True

##################   PRODUCT   #########################

class ProductCreate(BaseModel):
    name: str
    price: int
    stock: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    stock: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    stock: int

    class Config:
        from_attributes = True

##################   CATEGORY   #########################

class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


