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
# USER FIXTURE
# =====================================================

@pytest.fixture
def created_user(client):
    payload = unique_user()

    response = client.post(
        "/users/",
        json=payload
    )

    data = response.json()

    # Save original password for login tests
    data["password"] = payload["password"]

    return data


# =====================================================
# AUTH FIXTURES
# =====================================================

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
# LOGIN TESTS
# =====================================================

def test_login_success(client, created_user):
    response = client.post(
        "/login",
        data={
            "username": created_user["email"],
            "password": created_user["password"]
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client, created_user):
    response = client.post(
        "/login",
        data={
            "username": created_user["email"],
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/login",
        data={
            "username": "ghost23123@test.com",
            "password": "123456"
        }
    )

    assert response.status_code == 401


# =====================================================
# TOKEN / PROTECTED ROUTES
# =====================================================

def test_access_protected_route_with_token(client, auth_headers):
    response = client.get(
        "/orders/",
        headers=auth_headers
    )

    assert response.status_code == 200


def test_access_protected_route_without_token(client):
    response = client.get("/orders/")

    assert response.status_code in [401, 403]


def test_access_protected_route_with_invalid_token(client):
    response = client.get(
        "/orders/",
        headers={
            "Authorization": "Bearer invalidtoken123"
        }
    )

    assert response.status_code in [401, 403]