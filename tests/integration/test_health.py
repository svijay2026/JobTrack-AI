from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test that the root endpoint returns a 200 OK and valid JSON welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "documentation" in data
    assert data["documentation"] == "/docs"


def test_health_check_endpoint(client: TestClient):
    """Test that the /api/v1/health endpoint connects to the database and reports healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["app_name"] == "JobTrack AI"
    assert "version" in data
