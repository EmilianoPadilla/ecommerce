from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base



##################   ORDERITEM   #########################

class OrderItemDB(Base):
    __tablename__ = "orderitems"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer)
    unit_price = Column(Integer)

    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship("OrderDB", back_populates="orderitems")

    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("ProductDB", back_populates="orderitems")
