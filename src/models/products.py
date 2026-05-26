from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base


##################   PRODUCT   #########################

class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Integer)
    stock = Column(Integer)

    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("CategoryDB", back_populates="products")

    orderitems = relationship("OrderItemDB", back_populates="product")
