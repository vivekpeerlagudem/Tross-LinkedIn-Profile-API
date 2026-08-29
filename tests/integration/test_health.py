"""Integration tests for health and documentation endpoints."""

from fastapi.testclient import TestClient


def test_root_endpoint(test_client: TestClient):
    """Verifies that GET / returns 200 with API metadata and navigation links."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Tross LinkedIn Profile API"
    assert data["version"] == "0.1.0"
    assert data["status"] == "healthy"
    assert data["provider"] == "mock"
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"
    assert data["openapi"] == "/openapi.json"
    assert data["profile_endpoint"] == "/v1/profile"


def test_health_check_endpoint(test_client: TestClient):
    """Verifies that /health returns 200 and correct metadata."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["provider"] == "mock"
    assert "version" in data


def test_swagger_docs_accessible(test_client: TestClient):
    """Verifies that /docs interactive OpenAPI UI is accessible."""
    response = test_client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "html" in response.text.lower()


def test_openapi_json_schema(test_client: TestClient):
    """Verifies that /openapi.json produces valid OpenAPI schema."""
    response = test_client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "/" in schema["paths"]
    assert "/v1/profile" in schema["paths"]
    assert "/health" in schema["paths"]
