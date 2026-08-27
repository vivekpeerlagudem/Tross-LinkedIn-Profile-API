"""Unit tests for LiveLinkedInProvider using mocked HTTP transport (zero live network calls)."""

import json
import pytest
import httpx

from app.core.errors import (
    ProfileNotFoundException,
    ProviderUnavailableException,
    RateLimitedException,
)
from app.providers.live_provider import LiveLinkedInProvider


class TestLiveLinkedInProviderMocked:
    """Test suite verifying LiveLinkedInProvider with mocked HTTPX transport."""

    @pytest.mark.asyncio
    async def test_missing_credentials_raises_provider_unavailable(self):
        """Ensures that unconfigured credentials fail cleanly without making requests."""
        provider = LiveLinkedInProvider(li_at="", jsessionid="")
        with pytest.raises(ProviderUnavailableException) as exc_info:
            await provider.get_raw_profile("alex-morgan-dev")
        assert "credentials" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_header_construction(self):
        """Verifies that headers, cookies, and CSRF token are formatted securely and correctly."""
        provider = LiveLinkedInProvider(
            li_at="mock_li_at_secret",
            jsessionid='"ajax:1234567890"',
        )
        headers = provider._build_headers()
        assert headers["csrf-token"] == "ajax:1234567890"
        assert headers["Cookie"] == 'li_at=mock_li_at_secret; JSESSIONID="ajax:1234567890"'
        assert headers["x-restli-protocol-version"] == "2.0.0"
        assert "User-Agent" in headers

    @pytest.mark.asyncio
    async def test_successful_200_response(self):
        """Verifies parsing of successful HTTP 200 response."""
        mock_payload = {
            "profile": {
                "public_id": "test-user",
                "first_name": "Test",
                "last_name": "User",
                "headline": "Software Architect",
            },
            "experience": [],
            "skills": [{"name": "Python"}],
        }

        def mock_handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/voyager/api/identity/profiles/alex-morgan-dev/profileView"
            assert "alex-morgan-dev" in str(request.url)
            return httpx.Response(200, json=mock_payload)

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = LiveLinkedInProvider(
                li_at="dummy_cookie",
                jsessionid="dummy_csrf",
                client=client,
            )
            raw = await provider.get_raw_profile("alex-morgan-dev")
            assert raw["profile"]["public_id"] == "test-user"
            assert raw["profile"]["headline"] == "Software Architect"

    @pytest.mark.asyncio
    async def test_404_not_found_response(self):
        """Verifies that upstream 404 translates to ProfileNotFoundException."""
        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(404, json={"message": "Profile not found"})

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = LiveLinkedInProvider(
                li_at="dummy_cookie",
                jsessionid="dummy_csrf",
                client=client,
            )
            with pytest.raises(ProfileNotFoundException):
                await provider.get_raw_profile("unknown-user")

    @pytest.mark.asyncio
    async def test_401_expired_session_response(self):
        """Verifies that upstream 401 raises ProviderUnavailableException indicating expired session."""
        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"message": "Unauthorized"})

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = LiveLinkedInProvider(
                li_at="expired_cookie",
                jsessionid="expired_csrf",
                client=client,
            )
            with pytest.raises(ProviderUnavailableException) as exc_info:
                await provider.get_raw_profile("any-user")
            assert "expired" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_429_rate_limited_response(self):
        """Verifies that upstream 429 translates to RateLimitedException."""
        def mock_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(429, json={"message": "Too Many Requests"})

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = LiveLinkedInProvider(
                li_at="dummy_cookie",
                jsessionid="dummy_csrf",
                client=client,
            )
            with pytest.raises(RateLimitedException):
                await provider.get_raw_profile("any-user")

    @pytest.mark.asyncio
    async def test_network_timeout_handling(self):
        """Verifies that timeout errors raise ProviderUnavailableException cleanly."""
        def mock_handler(request: httpx.Request) -> httpx.Response:
            raise httpx.TimeoutException("Connection timed out")

        transport = httpx.MockTransport(mock_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = LiveLinkedInProvider(
                li_at="dummy_cookie",
                jsessionid="dummy_csrf",
                client=client,
            )
            with pytest.raises(ProviderUnavailableException) as exc_info:
                await provider.get_raw_profile("any-user")
            assert "timed out" in str(exc_info.value).lower()
