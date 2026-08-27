"""Dependency injection providers for FastAPI endpoints."""

from functools import lru_cache
from app.core.config import DataProviderType, settings
from app.providers.base import ProfileDataProvider
from app.providers.candidate_provider import CandidateLiveProfileProvider
from app.providers.live_provider import LiveLinkedInProvider
from app.providers.mock_provider import MockProfileProvider
from app.services.profile_service import ProfileService


@lru_cache()
def get_profile_provider() -> ProfileDataProvider:
    """Returns the configured profile data provider instance."""
    if settings.DATA_PROVIDER == DataProviderType.LIVE:
        return LiveLinkedInProvider()
    if settings.DATA_PROVIDER == DataProviderType.CANDIDATE:
        return CandidateLiveProfileProvider()
    return MockProfileProvider()


def get_profile_service() -> ProfileService:
    """Provides an instance of ProfileService with the active provider."""
    provider = get_profile_provider()
    return ProfileService(provider=provider)
