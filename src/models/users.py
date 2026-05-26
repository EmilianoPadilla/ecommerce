from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.models.base import Base

##################   USER   #########################

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    orders = relationship("OrderDB", back_populates="user")
