"""URL validation and identifier extraction utilities for LinkedIn profile URLs with SSRF protection."""

import re
from urllib.parse import urlparse
from app.core.errors import InvalidUrlException

# Strict pattern for valid LinkedIn profile path: /in/<vanity_id>
# Vanity IDs can contain alphanumeric characters, dashes, underscores, and percent-encoded chars
VANITY_ID_REGEX = re.compile(r"^[a-zA-Z0-9_\-%]{3,100}$")

# Allowed LinkedIn hostnames
ALLOWED_HOST_SUFFIXES = (
    "linkedin.com",
    "www.linkedin.com",
)


def validate_and_extract_vanity_id(raw_url: str) -> str:
    """
    Validates that a URL is a legitimate, safe LinkedIn individual profile URL and extracts the vanity ID.

    Raises:
        InvalidUrlException: If the URL fails format, host, protocol, or SSRF security checks.

    Returns:
        str: The sanitized vanity ID.
    """
    if not raw_url or not isinstance(raw_url, str):
        raise InvalidUrlException("A non-empty URL string must be provided.")

    cleaned_url = raw_url.strip()

    # Reject URLs that do not start with http:// or https://
    if not (cleaned_url.startswith("http://") or cleaned_url.startswith("https://")):
        raise InvalidUrlException("URL must start with http:// or https:// protocol scheme.")

    try:
        parsed = urlparse(cleaned_url)
    except Exception as exc:
        raise InvalidUrlException(f"Malformed URL structure: {exc}")

    # Check hostname
    hostname = parsed.hostname
    if not hostname:
        raise InvalidUrlException("Invalid URL: hostname could not be parsed.")

    hostname = hostname.lower()

    # SSRF & Whitelist check: Must be *.linkedin.com or linkedin.com
    is_valid_host = (
        hostname == "linkedin.com"
        or hostname.endswith(".linkedin.com")
    )
    if not is_valid_host:
        raise InvalidUrlException(
            f"Invalid domain '{hostname}'. Only LinkedIn profile URLs are supported."
        )

    # Reject non-profile paths (such as /company/, /jobs/, /feed/, /school/, /in without ID)
    path = parsed.path.strip("/")
    path_segments = [seg for seg in path.split("/") if seg]

    if len(path_segments) < 2 or path_segments[0].lower() != "in":
        raise InvalidUrlException(
            "URL must point to an individual profile (expected path format: /in/<vanity_id>)."
        )

    vanity_id = path_segments[1]

    # Validate vanity ID characters
    if not VANITY_ID_REGEX.match(vanity_id):
        raise InvalidUrlException(
            f"Invalid LinkedIn profile identifier '{vanity_id}'. Must be 3-100 alphanumeric or hyphen characters."
        )

    return vanity_id


def get_canonical_profile_url(vanity_id: str) -> str:
    """Returns standard canonical HTTPS URL for a given vanity ID."""
    return f"https://www.linkedin.com/in/{vanity_id}"
