"""Integration tests for POST /v1/profile endpoint."""

from fastapi.testclient import TestClient


def test_post_profile_full_synthetic(test_client: TestClient):
    """Tests successful retrieval and normalization of full synthetic profile."""
    payload = {"url": "https://www.linkedin.com/in/alex-morgan-dev"}
    response = test_client.post("/v1/profile", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "success"
    data = body["data"]

    # Check profile section
    profile = data["profile"]
    assert profile["public_id"] == "alex-morgan-dev"
    assert profile["full_name"] == "Alex Morgan"
    assert profile["headline"] is not None
    assert profile["profile_url"] == "https://www.linkedin.com/in/alex-morgan-dev"
    assert profile["location"]["city"] == "Austin"

    # Check experience
    assert len(data["experience"]) >= 1
    assert data["experience"][0]["title"] == "Lead Platform Engineer"

    # Check education
    assert len(data["education"]) >= 1
    assert data["education"][0]["school"] == "University of Texas at Austin"

    # Check skills
    assert len(data["skills"]) >= 1

    # Check certifications and languages
    assert len(data["certifications"]) >= 1
    assert len(data["languages"]) >= 1

    # Check metadata
    metadata = data["metadata"]
    assert metadata["provider"] == "mock"
    assert "profile" in metadata["sections_found"]
    assert "experience" in metadata["sections_found"]


def test_post_profile_partial_synthetic(test_client: TestClient):
    """Tests retrieval with missing sections (Jordan Lee fixture)."""
    payload = {"url": "https://www.linkedin.com/in/jordan-lee-tech"}
    response = test_client.post("/v1/profile", json=payload)
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["profile"]["public_id"] == "jordan-lee-tech"
    assert len(data["certifications"]) == 0
    assert len(data["languages"]) == 0

    metadata = data["metadata"]
    assert "certifications" in metadata["sections_missing"]
    assert "languages" in metadata["sections_missing"]


def test_post_profile_dynamic_synthetic(test_client: TestClient):
    """Tests that any valid LinkedIn URL returns a valid synthetic profile in mock mode."""
    payload = {"url": "https://www.linkedin.com/in/taylor-swift-dev"}
    response = test_client.post("/v1/profile", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["profile"]["public_id"] == "taylor-swift-dev"
