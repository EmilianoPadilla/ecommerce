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
# RANDOM TEST DATA
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

    return response.json()


# =====================================================
# GET USERS
# =====================================================

def test_get_users(client):
    response = client.get("/users/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_user(client, created_user):
    user_id = created_user["id"]

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_get_nonexistent_user(client):
    response = client.get("/users/999999")

    assert response.status_code == 404


# =====================================================
# POST/CREATE USER
# =====================================================

def test_create_user(client):
    payload = unique_user()

    response = client.post(
        "/users/",
        json=payload
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "password" not in data
    assert "id" in data


def test_create_duplicate_user(client):
    payload = unique_user()

    client.post("/users/", json=payload)

    response = client.post(
        "/users/",
        json=payload
    )

    assert response.status_code == 400


# =====================================================
# PUT USER
# =====================================================

def test_update_user(client, created_user):
    user_id = created_user["id"]

    updated_data = {
        "username": "updated_user",
        "email": f"updated_{user_id}@test.com",
        "password": "newpassword123"
    }

    response = client.put(
        f"/users/{user_id}",
        json=updated_data
    )

    assert response.status_code == 200
    assert response.json()["username"] == updated_data["username"]


def test_update_nonexistent_user(client):
    response = client.put(
        "/users/999999",
        json=unique_user()
    )

    assert response.status_code == 404


# =====================================================
# PATCH USER
# =====================================================

def test_patch_user(client, created_user):
    user_id = created_user["id"]

    response = client.patch(
        f"/users/{user_id}",
        json={"username": "patched_user"}
    )

    assert response.status_code == 200
    assert response.json()["username"] == "patched_user"


def test_patch_nonexistent_user(client):
    response = client.patch(
        "/users/999999",
        json={"username": "ghost_user"}
    )

    assert response.status_code == 404


# =====================================================
# DELETE USER
# =====================================================

def test_delete_user(client, created_user):
    user_id = created_user["id"]

    response = client.delete(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully!"


def test_delete_nonexistent_user(client):
    response = client.delete("/users/999999")

    assert response.status_code == 404