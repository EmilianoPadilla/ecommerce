from pydantic import BaseModel, ConfigDict
from typing import Optional


##################   ORDER_ITEM   #########################

class OrderItemCreate(BaseModel):
    quantity: int
    unit_price: int
    order_id: int
    product_id: int


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[int] = None
    order_id: Optional[int] = None
    product_id: Optional[int] = None


class OrderItemResponse(BaseModel):
    id: int
    quantity: int
    unit_price: int
    order_id: int
    product_id: int

    model_config = ConfigDict(from_attributes=True)