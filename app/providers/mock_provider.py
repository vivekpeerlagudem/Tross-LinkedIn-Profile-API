"""Mock data provider returning synthetic LinkedIn profile data without external network calls."""

import json
from pathlib import Path
from typing import Any, Dict
from app.core.errors import ProfileNotFoundException
from app.core.logging import logger
from app.providers.base import ProfileDataProvider

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures"


class MockProfileProvider(ProfileDataProvider):
    """Provides synthetic profile fixtures for development, testing, and offline evaluation."""

    def __init__(self, fixtures_dir: Path = FIXTURES_DIR):
        self._fixtures_dir = fixtures_dir
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_fixtures()

    @property
    def provider_name(self) -> str:
        return "mock"

    def _load_fixtures(self) -> None:
        """Pre-loads synthetic JSON fixtures into memory."""
        fixture_files = {
            "alex-morgan-dev": "synthetic_full_profile.json",
            "jordan-lee-tech": "synthetic_partial_profile.json",
            "sam-taylor-ai": "synthetic_minimal_profile.json",
        }

        for vanity_id, filename in fixture_files.items():
            path = self._fixtures_dir / filename
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self._cache[vanity_id] = json.load(f)
                except Exception as e:
                    logger.warning(f"Could not load fixture {filename}: {e}")

    async def get_raw_profile(self, vanity_id: str) -> Dict[str, Any]:
        """
        Returns raw synthetic profile data for the given vanity ID.

        Raises:
            ProfileNotFoundException: If the vanity ID is designated as not found.
        """
        # Specific test triggers for 404 testing
        if vanity_id in ("not-found-user", "non-existent-user", "missing-profile", "user-404"):
            raise ProfileNotFoundException(f"Profile '{vanity_id}' does not exist.")

        # Check explicit fixture personas
        if vanity_id in self._cache:
            return self._cache[vanity_id]

        # Dynamic fallback synthetic profile for any generic valid vanity ID
        return {
            "profile": {
                "public_id": vanity_id,
                "urn": f"urn:li:synthetic_profile:{hash(vanity_id) % 100000}",
                "first_name": vanity_id.replace("-", " ").replace("_", " ").title().split()[0],
                "last_name": vanity_id.replace("-", " ").replace("_", " ").title().split()[-1]
                if len(vanity_id.split("-")) > 1
                else "Developer",
                "full_name": vanity_id.replace("-", " ").replace("_", " ").title(),
                "headline": "Software Engineer & Systems Specialist",
                "location": "Global Tech Hub",
                "about": f"Synthetic professional profile representing {vanity_id}.",
                "profile_picture_url": None,
                "background_picture_url": None,
            },
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Synthetic Technology Corp",
                    "location": "Remote",
                    "start_date": {"year": 2021, "month": 1},
                    "end_date": None,
                    "is_current": True,
                    "description": "Designing and deploying production software systems.",
                }
            ],
            "education": [
                {
                    "school": "Synthetic Institute of Technology",
                    "degree": "B.S. in Computer Science",
                    "field_of_study": "Computer Science",
                    "start_year": 2017,
                    "end_year": 2021,
                }
            ],
            "skills": [
                {"name": "Python", "endorsement_count": 10},
                {"name": "FastAPI", "endorsement_count": 8},
                {"name": "Docker", "endorsement_count": 6},
            ],
            "certifications": [],
            "languages": [{"name": "English", "proficiency": "NATIVE_OR_BILINGUAL"}],
        }
