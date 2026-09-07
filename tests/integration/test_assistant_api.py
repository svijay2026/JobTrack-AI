import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.crud.crud_user import user_crud
from app.schemas.user import UserCreate


@pytest.fixture
def auth_header(client: TestClient, db_session: Session) -> dict:
    user_in = UserCreate(
        email="assistant_user@example.com",
        password="MySecretPassword123",
        full_name="Alex Rivera",
    )
    user_crud.create(db_session, obj_in=user_in)

    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "assistant_user@example.com", "password": "MySecretPassword123"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_chat_with_assistant_success(client: TestClient, auth_header: dict):
    """Test AI assistant responds with coaching advice and suggestions."""
    response = client.post(
        "/api/v1/assistant/chat",
        headers=auth_header,
        json={"message": "How can I improve my resume for senior engineering roles?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "suggested_prompts" in data
    assert len(data["suggested_prompts"]) > 0
    assert "timestamp" in data


def test_chat_with_assistant_pipeline_query(client: TestClient, auth_header: dict):
    """Test asking about application pipeline returns pipeline breakdown."""
    response = client.post(
        "/api/v1/assistant/chat",
        headers=auth_header,
        json={"message": "Analyze my application pipeline status"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "Pipeline" in data["reply"] or "Total" in data["reply"]


def test_chat_with_assistant_unauthorized(client: TestClient):
    """Test accessing assistant without auth token returns 401."""
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "Hello assistant"},
    )
    assert response.status_code == 401
