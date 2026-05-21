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
# RANDOM USER
# =====================================================

def unique_user():
    random_id = uuid.uuid4().hex[:8]

    return {
        "username": f"user_{random_id}",
        "email": f"{random_id}@test.com",
        "password": "123456"
    }


# =====================================================
# USER + AUTH FIXTURES
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
# CATEGORY FIXTURES
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
# GET CATEGORIES
# =====================================================

def test_get_categories(client, auth_headers):
    response = client.get(
        "/categories/",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_category(client, auth_headers, created_category):
    category_id = created_category["id"]

    response = client.get(
        f"/categories/{category_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == category_id


def test_get_nonexistent_category(client, auth_headers):
    response = client.get(
        "/categories/999999",
        headers=auth_headers
    )

    assert response.status_code == 404


# =====================================================
# CREATE CATEGORY
# =====================================================

def test_create_category(client, auth_headers):
    payload = category_payload()

    response = client.post(
        "/categories/",
        json=payload,
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["name"] == payload["name"]


# =====================================================
# UPDATE CATEGORY
# =====================================================

def test_update_category(client, auth_headers, created_category):
    category_id = created_category["id"]

    updated_data = {
        "name": f"updated_{uuid.uuid4().hex[:8]}"
    }

    response = client.patch(
        f"/categories/{category_id}",
        json=updated_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == updated_data["name"]


def test_update_nonexistent_category(client, auth_headers):
    response = client.patch(
        "/categories/999999",
        json={"name": "ghost_category"},
        headers=auth_headers
    )

    assert response.status_code == 404


# =====================================================
# DELETE CATEGORY
# =====================================================

def test_delete_category(client, auth_headers, created_category):
    category_id = created_category["id"]

    response = client.delete(
        f"/categories/{category_id}",
        headers=auth_headers
    )

    assert response.status_code == 200


def test_delete_nonexistent_category(client, auth_headers):
    response = client.delete(
        "/categories/999999",
        headers=auth_headers
    )

    assert response.status_code == 404