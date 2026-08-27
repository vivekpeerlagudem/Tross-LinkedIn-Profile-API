"""Unit tests for the MockProfileProvider."""

import pytest
from app.core.errors import ProfileNotFoundException
from app.providers.mock_provider import MockProfileProvider


class TestMockProfileProvider:
    """Test suite for MockProfileProvider."""

    @pytest.mark.asyncio
    async def test_get_raw_profile_alex_morgan_fixture(self, mock_provider: MockProfileProvider):
        raw = await mock_provider.get_raw_profile("alex-morgan-dev")
        assert raw["profile"]["public_id"] == "alex-morgan-dev"
        assert len(raw["experience"]) >= 1
        assert len(raw["education"]) >= 1
        assert len(raw["skills"]) >= 1

    @pytest.mark.asyncio
    async def test_get_raw_profile_not_found(self, mock_provider: MockProfileProvider):
        with pytest.raises(ProfileNotFoundException):
            await mock_provider.get_raw_profile("not-found-user")

    @pytest.mark.asyncio
    async def test_get_raw_profile_dynamic_synthetic(self, mock_provider: MockProfileProvider):
        raw = await mock_provider.get_raw_profile("custom-synthetic-engineer")
        assert raw["profile"]["public_id"] == "custom-synthetic-engineer"
        assert "experience" in raw
        assert "skills" in raw
