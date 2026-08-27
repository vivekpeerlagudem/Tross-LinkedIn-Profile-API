"""Unit tests for the ProfileNormalizer component."""

from app.models.response import ProfileData, YearMonth
from app.providers.normalizer import ProfileNormalizer


class TestProfileNormalizer:
    """Test suite for ProfileNormalizer."""

    def test_normalize_year_month_various_formats(self):
        # Dict format
        ym1 = ProfileNormalizer.normalize_year_month({"year": 2023, "month": 5})
        assert isinstance(ym1, YearMonth)
        assert ym1.year == 2023
        assert ym1.month == 5

        # String format YYYY-MM
        ym2 = ProfileNormalizer.normalize_year_month("2021-08")
        assert isinstance(ym2, YearMonth)
        assert ym2.year == 2021
        assert ym2.month == 8

        # Integer year
        ym3 = ProfileNormalizer.normalize_year_month(2019)
        assert isinstance(ym3, YearMonth)
        assert ym3.year == 2019
        assert ym3.month is None

        # None / Invalid
        assert ProfileNormalizer.normalize_year_month(None) is None
        assert ProfileNormalizer.normalize_year_month("invalid-date") is None

    def test_normalize_location_string_and_dict(self):
        loc1 = ProfileNormalizer.normalize_location("Austin, Texas, United States")
        assert loc1 is not None
        assert loc1.city == "Austin"
        assert loc1.country == "United States"
        assert loc1.raw == "Austin, Texas, United States"

        loc2 = ProfileNormalizer.normalize_location({"city": "Berlin", "country": "Germany", "raw": "Berlin, Germany"})
        assert loc2 is not None
        assert loc2.city == "Berlin"
        assert loc2.country == "Germany"

        assert ProfileNormalizer.normalize_location(None) is None

    def test_normalize_sections_detection(self):
        raw_parsed = {
            "profile": {
                "public_id": "alex-morgan-dev",
                "full_name": "Alex Morgan",
                "headline": "Staff Engineer",
                "location": "Austin, TX",
            },
            "experience": [
                {
                    "title": "Staff Engineer",
                    "company": "Acme Corp",
                    "start_date": "2020-01",
                    "end_date": None,
                    "is_current": True,
                }
            ],
            "education": [],
            "skills": [{"name": "Python"}],
            "certifications": [],
            "languages": [],
        }

        profile_data = ProfileNormalizer.normalize(
            raw_parsed=raw_parsed,
            vanity_id="alex-morgan-dev",
            provider_name="mock",
        )

        assert isinstance(profile_data, ProfileData)
        assert profile_data.profile.full_name == "Alex Morgan"
        assert "profile" in profile_data.metadata.sections_found
        assert "experience" in profile_data.metadata.sections_found
        assert "skills" in profile_data.metadata.sections_found
        assert "education" in profile_data.metadata.sections_missing
        assert "certifications" in profile_data.metadata.sections_missing
        assert "languages" in profile_data.metadata.sections_missing
