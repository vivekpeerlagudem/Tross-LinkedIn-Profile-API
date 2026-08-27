"""Candidate live data provider interface for future research & verification phases."""

from typing import Any, Dict
from app.core.errors import ProviderUnavailableException
from app.providers.base import ProfileDataProvider


class CandidateLiveProfileProvider(ProfileDataProvider):
    """
    Isolated provider stub representing candidate live retrieval mechanisms.
    This provider remains inactive and isolated until research and verification are completed.
    """

    @property
    def provider_name(self) -> str:
        return "candidate"

    async def get_raw_profile(self, vanity_id: str) -> Dict[str, Any]:
        """
        Stub placeholder for candidate live retrieval.
        Raises ProviderUnavailableException until candidate mechanism is verified.
        """
        raise ProviderUnavailableException(
            "Live candidate retrieval is currently in research phase. Use DATA_PROVIDER=mock for full functionality."
        )
