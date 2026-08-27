"""Profile service orchestrating validation, provider retrieval, parsing, and normalization."""

from app.core.logging import logger
from app.models.response import ProfileResponse
from app.providers.base import ProfileDataProvider
from app.providers.normalizer import ProfileNormalizer
from app.providers.parser import ProfileParser
from app.utils.url import validate_and_extract_vanity_id


class ProfileService:
    """Service layer orchestrating the profile extraction workflow."""

    def __init__(self, provider: ProfileDataProvider):
        self._provider = provider

    async def get_profile_by_url(self, raw_url: str) -> ProfileResponse:
        """
        Validates URL, retrieves raw data via provider, parses, and normalizes into response model.

        Args:
            raw_url: Input URL from client request.

        Returns:
            ProfileResponse: Structured profile response.
        """
        # Step 1: Validate URL and extract vanity ID (SSRF defense)
        vanity_id = validate_and_extract_vanity_id(raw_url)
        logger.info(f"Processing profile request for vanity ID: {vanity_id} (provider: {self._provider.provider_name})")

        # Step 2: Retrieve raw payload from provider abstraction
        raw_data = await self._provider.get_raw_profile(vanity_id)

        # Step 3: Parse raw heterogeneous structures
        parsed_data = {
            "profile": ProfileParser.extract_profile_info(raw_data, vanity_id),
            "experience": ProfileParser.extract_experience(raw_data),
            "education": ProfileParser.extract_education(raw_data),
            "skills": ProfileParser.extract_skills(raw_data),
            "certifications": ProfileParser.extract_certifications(raw_data),
            "languages": ProfileParser.extract_languages(raw_data),
        }

        # Step 4: Normalize parsed data into standardized Pydantic models
        profile_data = ProfileNormalizer.normalize(
            raw_parsed=parsed_data,
            vanity_id=vanity_id,
            provider_name=self._provider.provider_name,
        )

        return ProfileResponse(status="success", data=profile_data)
