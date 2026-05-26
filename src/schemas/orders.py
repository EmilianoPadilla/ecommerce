from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


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
    user_id: int

    model_config = ConfigDict(from_attributes=True)