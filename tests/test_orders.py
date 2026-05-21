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
# TEST DATABASE (POSTGRESQL)
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
# USER FIXTURE
# =====================================================

@pytest.fixture
def created_user(client):
    payload = unique_user()

    response = client.post(
        "/users/",
        json=payload
    )

    return {
        "data": response.json(),
        "email": payload["email"],
        "password": payload["password"]
    }


# =====================================================
# ORDER DATA
# =====================================================

def order_payload():
    return {
        "total": 199,
        "purchased_on": "2026-05-14T12:00:00"
    }


# =====================================================
# TOKEN FIXTURE
# =====================================================

@pytest.fixture
def auth_token(client, created_user): #function that will use client and created_user as params
    response = client.post( 
        "/login",
        data={
            "username": created_user["email"],
            "password": created_user["password"]
        }
    ) #this uses the newly created user to login on the /login endpoint using the username and password of the user

    return response.json()["access_token"] #.json converts response into python dict and then ["access_token"] extracts the token


# =====================================================
# AUTH HEADERS
# =====================================================

@pytest.fixture #this functions takes the token generated from auth_token and returns it to be sent in the header format expected
def auth_headers(auth_token):
    return {
        "Authorization": f"Bearer {auth_token}"
    }


# =====================================================
# CREATED ORDER FIXTURE
# =====================================================

@pytest.fixture
def created_order(client, auth_headers):
    response = client.post(
        "/orders/",
        json=order_payload(),
        headers=auth_headers
    )

    return response.json()


# =====================================================
# GET ORDERS
# =====================================================

def test_get_orders(client, auth_headers):
    response = client.get(
        "/orders/",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_order(client, auth_headers, created_order):
    order_id = created_order["id"]

    response = client.get(
        f"/orders/{order_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_get_nonexistent_order(client, auth_headers):
    response = client.get(
        "/orders/999999",
        headers=auth_headers
    )

    assert response.status_code == 404


# =====================================================
# CREATE ORDER
# =====================================================

def test_create_order(client, auth_headers):
    response = client.post(
        "/orders/",
        json=order_payload(),
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["total"] == 199
    assert "id" in data
    assert "user_id" in data


def test_create_order_without_token(client):
    response = client.post(
        "/orders/",
        json=order_payload()
    )

    assert response.status_code == 401


# =====================================================
# UPDATE ORDER
# =====================================================

def test_update_order(client, auth_headers, created_order):
    order_id = created_order["id"]

    response = client.put(
        f"/orders/{order_id}",
        json={
            "total": 500,
            "purchased_on": "2026-05-15T12:00:00"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["total"] == 500


def test_update_nonexistent_order(client, auth_headers):
    response = client.put(
        "/orders/999999",
        json={
            "total": 500,
            "purchased_on": "2026-05-15T12:00:00"
        },
        headers=auth_headers
    )

    assert response.status_code == 404


# =====================================================
# DELETE ORDER
# =====================================================

def test_delete_order(client, auth_headers, created_order):
    order_id = created_order["id"]

    response = client.delete(
        f"/orders/{order_id}",
        headers=auth_headers
    )

    assert response.status_code == 200


def test_delete_nonexistent_order(client, auth_headers):
    response = client.delete(
        "/orders/999999",
        headers=auth_headers
    )

    assert response.status_code == 404