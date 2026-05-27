# E-Commerce API (FastAPI + PostgreSQL)

## Description

This is my backend API project for an e-commerce system built with FastAPI and PostgreSQL.

It supports user authentication, product management, categories, and order processing, while storing information within a PostgreSQL database.

---

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- OAuth2
- JWT Authentication
- Uvicorn
- Docker
- Pytest

---

## Features

- User registration and OAuth2 login
- JWT authentication
- Password hashing
- CRUD operations for users
- CRUD operations for products
- CRUD operations for categories
- CRUD operations for orders
- CRUD operations for order items
- Relational database design
- Input validation with Pydantic
- API testing with Pytest
- Docker containerization
- Deployment on Render

---

## Requirements

- Python 3.13+
- PostgreSQL
- Docker (optional)

---

## Project Structure

```text
ecommerce/
│
├── main.py
├── requirements.txt
├── .gitignore
├── .dockerignore
├── .env
├── Dockerfile
├── docker-compose.yml
├── README.md
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_orders.py
│   ├── test_orderitems.py
│   ├── test_products.py
│   └── test_categories.py
│
└── src/
    │
    ├── auth/
    │   ├── hashing.py
    │   ├── jwt_handler.py
    │   └── dependencies.py
    │
    ├── database/
    │   └── database.py
    │
    ├── models/
    │   ├── base.py
    │   ├── users.py
    │   ├── orders.py
    │   ├── orderitems.py
    │   ├── products.py
    │   └── categories.py
    │
    ├── schemas/
    │   ├── users.py
    │   ├── orders.py
    │   ├── orderitems.py
    │   ├── products.py
    │   └── categories.py
    │
    └── routers/
        ├── users.py
        ├── orders.py
        ├── orderitems.py
        ├── products.py
        ├── categories.py
        └── auth.py
```

---

## Environment Variables

### Local Environment (`.env` file)

```env
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Production Environment (Render Dashboard)

Set the same environment variables inside the Render Dashboard under:

```text
Dashboard → Your Service → Environment
```

---

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/EmilianoPadilla/ecommerce.git
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

#### Linux / Mac

```bash
source venv/bin/activate
```

#### Windows

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the server

```bash
uvicorn src.main:app --reload
```

---

## Deployment

This API is deployed on Render:

https://emilianopadilla-ecommerce-backend.onrender.com/

---

## API Documentation

FastAPI Swagger documentation:

https://emilianopadilla-ecommerce-backend.onrender.com/docs

---

## API Endpoints

### Authentication

```http
POST /login
```

### Users

```http
GET    /users
POST   /users
GET    /users/{user_id}
PUT    /users/{user_id}
PATCH  /users/{user_id}
DELETE /users/{user_id}
```

### Orders

```http
GET    /orders
POST   /orders
GET    /orders/{order_id}
PUT    /orders/{order_id}
PATCH  /orders/{order_id}
DELETE /orders/{order_id}
```

### Order Items

```http
GET    /orderitems
POST   /orderitems
GET    /orderitems/{orderitem_id}
PUT    /orderitems/{orderitem_id}
PATCH  /orderitems/{orderitem_id}
DELETE /orderitems/{orderitem_id}
```

### Products

```http
GET    /products
POST   /products
GET    /products/{product_id}
PUT    /products/{product_id}
PATCH  /products/{product_id}
DELETE /products/{product_id}
```

### Categories

```http
GET    /categories
POST   /categories
GET    /categories/{category_id}
PUT    /categories/{category_id}
PATCH  /categories/{category_id}
DELETE /categories/{category_id}
```

---

## Example Request

### Create User

```http
POST /users
```

### Request Body

```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

---

## Notes

This project was built as part of a backend learning roadmap focused on FastAPI, authentication, testing, Docker, and deployment.
