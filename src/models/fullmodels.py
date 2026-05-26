from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

##################   USER   #########################

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    orders = relationship("OrderDB", back_populates="user")


##################   ORDER   #########################

class OrderDB(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Integer)
    purchased_on = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserDB", back_populates="orders")

    orderitems = relationship("OrderItemDB", back_populates="order")


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


##################   PRODUCT   #########################

class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    stock = Column(Integer)

    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("CategoryDB", back_populates="products")

    orderitems = relationship("OrderItemDB", back_populates="product")


##################   CATEGORY   #########################

class CategoryDB(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    products = relationship("ProductDB", back_populates="category")