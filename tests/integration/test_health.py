from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test that the root endpoint returns a 200 OK and valid response (HTML SPA or JSON)."""
    response = client.get("/")
    assert response.status_code == 200
    if "text/html" in response.headers.get("content-type", ""):
        assert "<html" in response.text.lower() or "doctype" in response.text.lower()
    else:
        data = response.json()
        assert "message" in data or "documentation" in data


def test_health_check_endpoint(client: TestClient):
    """Test that the /api/v1/health endpoint connects to the database and reports healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["app_name"] == "JobTrack AI"
    assert "version" in data
