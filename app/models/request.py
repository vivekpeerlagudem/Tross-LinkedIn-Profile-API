"""Request models for the LinkedIn Profile API."""

from pydantic import BaseModel, Field, field_validator
from app.utils.url import validate_and_extract_vanity_id


class ProfileRequest(BaseModel):
    """Payload for profile retrieval request."""

    url: str = Field(
        ...,
        description="Public LinkedIn profile URL (e.g., https://www.linkedin.com/in/username/)",
        examples=["https://www.linkedin.com/in/alex-morgan-dev"],
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("URL cannot be empty.")
        # Ensure it passes vanity ID validation
        validate_and_extract_vanity_id(v)
        return v.strip()
