from pydantic import BaseModel, ConfigDict
from typing import Optional


##################   PRODUCT   #########################

class ProductCreate(BaseModel):
    name: str
    price: int
    stock: int
    category_id: int
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    stock: int
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)