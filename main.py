from fastapi import FastAPI
from app.routers import users, orders, orderitems, products, categories, auth

from app.database.database import engine
from app.models.base import Base

from app.models.users import UserDB
from app.models.orders import OrderDB
from app.models.orderitems import OrderItemDB
from app.models.products import ProductDB
from app.models.categories import CategoryDB
from app.routers import auth


Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome to our e-commerce!"}

app.include_router(users.router)
app.include_router(orders.router)
app.include_router(orderitems.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(auth.router)
