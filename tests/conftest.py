"""Pytest configuration and global fixtures."""

import pytest
from fastapi.testclient import TestClient
from app.core.config import DataProviderType, settings
from app.main import app
from app.providers.mock_provider import MockProfileProvider
from app.services.profile_service import ProfileService


@pytest.fixture(autouse=True)
def set_mock_provider_env(monkeypatch):
    """Ensures mock provider is active for all tests."""
    monkeypatch.setattr(settings, "DATA_PROVIDER", DataProviderType.MOCK)


@pytest.fixture
def test_client() -> TestClient:
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def mock_provider() -> MockProfileProvider:
    """MockProfileProvider fixture."""
    return MockProfileProvider()


@pytest.fixture
def profile_service(mock_provider) -> ProfileService:
    """ProfileService fixture with mock provider."""
    return ProfileService(provider=mock_provider)
