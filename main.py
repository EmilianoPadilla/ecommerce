from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import users, orders, orderitems, products, categories, auth
from src.routers import cart

from src.database.database import engine
from src.models.base import Base

from src.models.users import UserDB
from src.models.orders import OrderDB
from src.models.orderitems import OrderItemDB
from src.models.products import ProductDB
from src.models.categories import CategoryDB
from src.models.cart import CartItemDB
from src.routers import auth


Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://obolus-by-emilianopadilla.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to our e-commerce! Have a nice day! "}

app.include_router(users.router)
app.include_router(orders.router)
app.include_router(orderitems.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(auth.router)
app.include_router(cart.router)