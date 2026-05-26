from fastapi import FastAPI
from src.routers import users, orders, orderitems, products, categories, auth

from src.database.database import engine
from src.models.base import Base

from src.models.users import UserDB
from src.models.orders import OrderDB
from src.models.orderitems import OrderItemDB
from src.models.products import ProductDB
from src.models.categories import CategoryDB
from src.routers import auth


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
