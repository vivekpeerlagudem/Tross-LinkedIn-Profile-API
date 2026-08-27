"""Live LinkedIn data provider using Voyager REST client over httpx."""

from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.errors import (
    ProfileNotFoundException,
    ProviderUnavailableException,
    RateLimitedException,
)
from app.core.logging import logger
from app.providers.base import ProfileDataProvider



class LiveLinkedInProvider(ProfileDataProvider):
    """
    Live LinkedIn provider connecting to LinkedIn internal Voyager REST endpoints.
    Requires server-side session credentials (LINKEDIN_LI_AT and LINKEDIN_JSESSIONID).
    """

    def __init__(
        self,
        li_at: Optional[str] = None,
        jsessionid: Optional[str] = None,
        base_url: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None,
    ):
        self._li_at = li_at if li_at is not None else settings.LINKEDIN_LI_AT
        self._jsessionid = jsessionid if jsessionid is not None else settings.LINKEDIN_JSESSIONID
        self._base_url = (base_url or settings.LINKEDIN_BASE_URL).rstrip("/")
        self._client = client

    @property
    def provider_name(self) -> str:
        return "live"

    def _get_csrf_token(self) -> str:
        """Sanitizes JSESSIONID value for the csrf-token header (strips surrounding double quotes)."""
        if not self._jsessionid:
            return ""
        return self._jsessionid.strip().strip('"')

    def _build_headers(self) -> Dict[str, str]:
        """Constructs secure request headers with required anti-CSRF and restli protocol headers."""
        csrf = self._get_csrf_token()
        # Cookie string formatting
        cookie_header = f'li_at={self._li_at}; JSESSIONID="{csrf}"'

        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/vnd.linkedin.normalized+json+2.1",
            "x-restli-protocol-version": "2.0.0",
            "csrf-token": csrf,
            "Cookie": cookie_header,
            "x-li-lang": "en_US",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def get_raw_profile(self, vanity_id: str) -> Dict[str, Any]:
        """
        Retrieves raw profile data from LinkedIn Voyager REST API.

        Raises:
            ProviderUnavailableException: If credentials are missing, expired, or network fails.
            ProfileNotFoundException: If the profile is not found (HTTP 404).
            RateLimitedException: If upstream rate limit is hit (HTTP 429).
        """
        # Validate that credentials are configured
        if not self._li_at or not self._jsessionid:
            logger.error("Live provider called without LINKEDIN_LI_AT or LINKEDIN_JSESSIONID.")
            raise ProviderUnavailableException(
                "Live LinkedIn credentials (LINKEDIN_LI_AT, LINKEDIN_JSESSIONID) are not configured. "
                "Please configure them in your environment or use DATA_PROVIDER=mock."
            )

        endpoint = f"{self._base_url}/voyager/api/identity/profiles/{vanity_id}/profileView"
        headers = self._build_headers()

        # Execute asynchronous request (using injected client or creating short-lived client)
        try:
            if self._client:
                response = await self._client.get(endpoint, headers=headers)
            else:
                async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
                    response = await client.get(endpoint, headers=headers)
        except httpx.TimeoutException as exc:
            logger.error(f"Timeout querying upstream LinkedIn for vanity_id '{vanity_id}': {exc}")
            raise ProviderUnavailableException("Upstream LinkedIn request timed out.")
        except httpx.RequestError as exc:
            logger.error(f"Network error querying upstream LinkedIn for vanity_id '{vanity_id}': {exc}")
            raise ProviderUnavailableException(f"Network error communicating with upstream LinkedIn service: {exc}")

        # Evaluate HTTP status codes
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"Successfully retrieved profile payload from Voyager for '{vanity_id}'.")
                return data
            except Exception as e:
                logger.error(f"Failed to parse JSON response from Voyager: {e}")
                raise ProviderUnavailableException("Invalid JSON received from upstream LinkedIn.")

        elif response.status_code == 404:
            logger.warning(f"Profile '{vanity_id}' returned 404 from upstream Voyager.")
            raise ProfileNotFoundException(f"Profile '{vanity_id}' was not found on LinkedIn.")

        elif response.status_code in (401, 403):
            logger.error(f"Authentication failure from upstream Voyager: HTTP {response.status_code}.")
            raise ProviderUnavailableException(
                "Upstream LinkedIn session is invalid or expired. Please update LINKEDIN_LI_AT / LINKEDIN_JSESSIONID."
            )

        elif response.status_code == 429:
            logger.warning(f"Rate limited by upstream Voyager: HTTP 429 for '{vanity_id}'.")
            raise RateLimitedException("LinkedIn upstream rate limit encountered. Please retry later.")

        else:
            logger.error(f"Unexpected status code {response.status_code} from upstream Voyager.")
            raise ProviderUnavailableException(
                f"LinkedIn upstream returned unexpected status code {response.status_code}."
            )
