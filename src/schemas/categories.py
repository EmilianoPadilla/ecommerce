from pydantic import BaseModel, ConfigDict
from typing import Optional


##################   CATEGORY   #########################

class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)