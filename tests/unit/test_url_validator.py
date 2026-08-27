"""Unit tests for URL validation and SSRF prevention."""

import pytest
from app.core.errors import InvalidUrlException
from app.utils.url import get_canonical_profile_url, validate_and_extract_vanity_id


class TestUrlValidator:
    """Test suite for validate_and_extract_vanity_id and get_canonical_profile_url."""

    @pytest.mark.parametrize(
        "valid_url, expected_vanity_id",
        [
            ("https://www.linkedin.com/in/alex-morgan-dev", "alex-morgan-dev"),
            ("https://linkedin.com/in/alex-morgan-dev/", "alex-morgan-dev"),
            ("http://www.linkedin.com/in/jordan_lee_123", "jordan_lee_123"),
            ("https://in.linkedin.com/in/sam-taylor-ai", "sam-taylor-ai"),
            ("https://uk.linkedin.com/in/dev-user-99", "dev-user-99"),
            ("https://www.linkedin.com/in/alex-morgan-dev?trk=public_profile", "alex-morgan-dev"),
            ("https://www.linkedin.com/in/alex-morgan-dev/?originalSubdomain=ca", "alex-morgan-dev"),
        ],
    )
    def test_valid_linkedin_profile_urls(self, valid_url: str, expected_vanity_id: str):
        result = validate_and_extract_vanity_id(valid_url)
        assert result == expected_vanity_id

    @pytest.mark.parametrize(
        "invalid_url, reason",
        [
            ("https://www.google.com/in/alex-morgan", "non-linkedin domain"),
            ("https://evil-linkedin.com/in/alex-morgan", "fake domain"),
            ("http://169.254.169.254/latest/meta-data", "SSRF metadata IP"),
            ("http://localhost:8000/in/alex-morgan", "SSRF localhost"),
            ("http://127.0.0.1:8000/in/alex-morgan", "SSRF loopback"),
            ("https://www.linkedin.com/company/google", "company page"),
            ("https://www.linkedin.com/jobs/view/12345", "jobs page"),
            ("https://www.linkedin.com/feed/", "feed page"),
            ("https://www.linkedin.com/school/stanford/", "school page"),
            ("https://www.linkedin.com/in/", "empty vanity ID"),
            ("ftp://www.linkedin.com/in/alex-morgan", "invalid protocol"),
            ("file:///etc/passwd", "file protocol"),
            ("not-a-valid-url", "plain text"),
            ("", "empty string"),
        ],
    )
    def test_invalid_urls_rejected(self, invalid_url: str, reason: str):
        with pytest.raises(InvalidUrlException):
            validate_and_extract_vanity_id(invalid_url)

    def test_canonical_url_generation(self):
        canonical = get_canonical_profile_url("alex-morgan-dev")
        assert canonical == "https://www.linkedin.com/in/alex-morgan-dev"
