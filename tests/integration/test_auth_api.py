import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.crud.crud_user import user_crud
from app.schemas.user import UserCreate


def test_register_user_success(client: TestClient):
    """Test registering a new user returns 201 Created and user profile without password."""
    payload = {
        "email": "candidate@example.com",
        "password": "Password123!",
        "full_name": "Jane Developer",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "candidate@example.com"
    assert data["full_name"] == "Jane Developer"
    assert "id" in data
    assert "hashed_password" not in data
    assert "password" not in data


def test_register_duplicate_email_fails(client: TestClient):
    """Test that attempting to register an existing email returns 400 Bad Request."""
    payload = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "full_name": "First User",
    }
    # Register first user
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Attempt second registration with same email
    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_register_short_password_fails_validation(client: TestClient):
    """Test that passwords shorter than 8 characters are rejected with 422 Unprocessable Entity."""
    payload = {
        "email": "short@example.com",
        "password": "short",
        "full_name": "Short Pwd",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client: TestClient, db_session: Session):
    """Test login with OAuth2 form returns 200 OK and JWT access token."""
    user_in = UserCreate(
        email="login_test@example.com",
        password="MySecretPassword123",
        full_name="Login User",
    )
    user_crud.create(db_session, obj_in=user_in)

    # Login with form data
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "login_test@example.com", "password": "MySecretPassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_json_success(client: TestClient, db_session: Session):
    """Test login with JSON body endpoint."""
    user_in = UserCreate(
        email="json_login@example.com",
        password="MySecretPassword123",
        full_name="JSON User",
    )
    user_crud.create(db_session, obj_in=user_in)

    response = client.post(
        "/api/v1/auth/login/json",
        json={"email": "json_login@example.com", "password": "MySecretPassword123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_fails(client: TestClient, db_session: Session):
    """Test login with incorrect password returns 401 Unauthorized."""
    user_in = UserCreate(
        email="wrong_pwd@example.com",
        password="CorrectPassword123",
        full_name="Test User",
    )
    user_crud.create(db_session, obj_in=user_in)

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrong_pwd@example.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_me_protected_endpoint(client: TestClient, db_session: Session):
    """Test accessing protected /api/v1/auth/me endpoint with Bearer token."""
    user_in = UserCreate(
        email="me_test@example.com",
        password="MySecretPassword123",
        full_name="Profile User",
    )
    user = user_crud.create(db_session, obj_in=user_in)

    # 1. Login to obtain token
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "me_test@example.com", "password": "MySecretPassword123"},
    )
    token = login_res.json()["access_token"]

    # 2. Access /me with Authorization header
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me_test@example.com"
    assert data["full_name"] == "Profile User"
    assert data["id"] == user.id


def test_get_me_unauthorized_without_token(client: TestClient):
    """Test accessing /api/v1/auth/me without token returns 401 Unauthorized."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
