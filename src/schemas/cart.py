from pydantic import BaseModel, ConfigDict
from typing import Optional


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None


class CartItemResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class CartItemWithProduct(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product_name: str
    product_price: int
    product_image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)