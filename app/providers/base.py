"""Abstract data provider interface for LinkedIn profile retrieval."""

from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class ProfileDataProvider(Protocol):
    """Protocol interface defining operations for profile data providers."""

    @property
    def provider_name(self) -> str:
        """Name of the provider implementation (e.g., 'mock', 'candidate')."""
        ...

    async def get_raw_profile(self, vanity_id: str) -> Dict[str, Any]:
        """
        Retrieves the raw profile dictionary for a given LinkedIn vanity ID.

        Args:
            vanity_id: Clean LinkedIn vanity identifier (e.g., 'alex-morgan-dev').

        Returns:
            Dict[str, Any]: Raw profile data dictionary.

        Raises:
            ProfileNotFoundException: When profile does not exist.
            ProviderUnavailableException: When upstream retrieval fails.
        """
        ...
