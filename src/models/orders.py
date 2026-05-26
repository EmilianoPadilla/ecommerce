from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.models.base import Base


##################   ORDER   #########################

class OrderDB(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Integer)
    purchased_on = Column(DateTime)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserDB", back_populates="orders")

    orderitems = relationship("OrderItemDB", back_populates="order")
