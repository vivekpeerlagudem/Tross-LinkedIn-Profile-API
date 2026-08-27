"""Integration tests for error handling and edge cases."""

from fastapi.testclient import TestClient


def test_invalid_url_returns_400(test_client: TestClient):
    """Tests that a non-LinkedIn URL returns HTTP 400 with INVALID_URL error code."""
    payload = {"url": "https://www.google.com/search?q=alex"}
    response = test_client.post("/v1/profile", json=payload)
    assert response.status_code == 400

    body = response.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "INVALID_URL"
    assert "linkedin" in body["error"]["message"].lower()


def test_malformed_url_returns_400(test_client: TestClient):
    """Tests that malformed or non-profile paths return 400."""
    payload = {"url": "https://www.linkedin.com/company/acme"}
    response = test_client.post("/v1/profile", json=payload)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_URL"


def test_ssrf_attempt_rejected_400(test_client: TestClient):
    """Tests that local IP or AWS metadata URLs are rejected."""
    payload = {"url": "http://169.254.169.254/latest/meta-data"}
    response = test_client.post("/v1/profile", json=payload)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_URL"


def test_profile_not_found_returns_404(test_client: TestClient):
    """Tests that non-existent vanity ID returns HTTP 404 with PROFILE_NOT_FOUND."""
    payload = {"url": "https://www.linkedin.com/in/not-found-user"}
    response = test_client.post("/v1/profile", json=payload)
    assert response.status_code == 404

    body = response.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "PROFILE_NOT_FOUND"


def test_missing_body_returns_400(test_client: TestClient):
    """Tests that missing body or empty payload returns 400 validation error."""
    response = test_client.post("/v1/profile", json={})
    assert response.status_code == 400
    assert response.json()["status"] == "error"
