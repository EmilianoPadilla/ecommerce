from pydantic import BaseModel, ConfigDict
from typing import Optional


##################   PRODUCT   #########################

class ProductCreate(BaseModel):
    name: str
    price: int
    stock: int
    category_id: int


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    stock: int

    model_config = ConfigDict(from_attributes=True)