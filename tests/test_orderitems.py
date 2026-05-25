import uuid
import pytest
from dotenv import load_dotenv
import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.database.database import get_db
from app.models.base import Base


# =====================================================
# TEST DATABASE
# =====================================================

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)


# =====================================================
# DB FIXTURE WITH ROLLBACK
# =====================================================

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()

    if transaction.is_active:
        transaction.rollback()

    connection.close()


# =====================================================
# CLIENT FIXTURE
# =====================================================

@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


# =====================================================
# RANDOM USER DATA
# =====================================================

def unique_user():
    random_id = uuid.uuid4().hex[:8]

    return {
        "username": f"user_{random_id}",
        "email": f"{random_id}@test.com",
        "password": "123456"
    }


# =====================================================
# FIXTURES
# =====================================================

@pytest.fixture
def created_user(client):
    payload = unique_user()

    response = client.post(
        "/users/",
        json=payload
    )

    data = response.json()
    data["password"] = payload["password"]

    return data


@pytest.fixture
def auth_token(client, created_user):
    response = client.post(
        "/login",
        data={
            "username": created_user["email"],
            "password": created_user["password"]
        }
    )

    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {
        "Authorization": f"Bearer {auth_token}"
    }


# =====================================================
# ORDER FIXTURE
# =====================================================

def order_payload():
    return {
        "total": 500,
        "purchased_on": "2026-05-14T12:00:00"
    }


@pytest.fixture
def created_order(client, auth_headers):
    response = client.post(
        "/orders/",
        json=order_payload(),
        headers=auth_headers
    )

    return response.json()


# =====================================================
# PRODUCT FIXTURE
# =====================================================

def product_payload(category_id):
    random_id = uuid.uuid4().hex[:8]

    return {
        "name": f"product_{random_id}",
        "description": "Test product",
        "price": 199,
        "stock": 10,
        "category_id": category_id
    }


@pytest.fixture
def created_product(client, auth_headers, created_category):
    response = client.post(
        "/products/",
        json=product_payload(created_category["id"]),
        headers=auth_headers
    )

    return response.json()

# =====================================================
# CATEGORY FIXTURE
# =====================================================

def category_payload():
    random_id = uuid.uuid4().hex[:8]

    return {
        "name": f"category_{random_id}"
    }


@pytest.fixture
def created_category(client, auth_headers):
    response = client.post(
        "/categories/",
        json=category_payload(),
        headers=auth_headers
    )

    return response.json()

# =====================================================
# ORDER ITEM FIXTURE
# =====================================================

def order_item_payload(order_id, product_id):
    return {
        "quantity": 2,
        "unit_price": 199,
        "order_id": order_id,
        "product_id": product_id
    }


@pytest.fixture
def created_order_item(client, auth_headers, created_order, created_product):
    payload = order_item_payload(
        created_order["id"],
        created_product["id"]
    )

    response = client.post(
        "/orderitems/",
        json=payload,
        headers=auth_headers
    )

    return response.json()


# =====================================================
# GET ORDER ITEMS
# =====================================================

def test_get_order_items(client, auth_headers):
    response = client.get(
        "/orderitems/",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_order_item(client, auth_headers, created_order_item):
    item_id = created_order_item["id"]

    response = client.get(
        f"/orderitems/{item_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == item_id


def test_get_nonexistent_order_item(client, auth_headers):
    response = client.get(
        "/orderitems/999999",
        headers=auth_headers
    )

    assert response.status_code == 404


# =====================================================
# CREATE ORDER ITEM
# =====================================================

def test_create_order_item(client, auth_headers, created_order, created_product):
    payload = order_item_payload(
        created_order["id"],
        created_product["id"]
    )

    response = client.post(
        "/orderitems/",
        json=payload,
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["quantity"] == payload["quantity"]


# =====================================================
# UPDATE ORDER ITEM
# =====================================================

def test_update_order_item(client, auth_headers, created_order_item):
    item_id = created_order_item["id"]

    updated_data = {
        "quantity": 5
    }

    response = client.patch(
        f"/orderitems/{item_id}",
        json=updated_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 5


def test_update_nonexistent_order_item(client, auth_headers):
    response = client.patch(
        "/orderitems/999999",
        json={"quantity": 10},
        headers=auth_headers
    )

    assert response.status_code == 404


# =====================================================
# DELETE ORDER ITEM
# =====================================================

def test_delete_order_item(client, auth_headers, created_order_item):
    item_id = created_order_item["id"]

    response = client.delete(
        f"/orderitems/{item_id}",
        headers=auth_headers
    )

    assert response.status_code == 200


def test_delete_nonexistent_order_item(client, auth_headers):
    response = client.delete(
        "/orderitems/999999",
        headers=auth_headers
    )

    assert response.status_code == 404