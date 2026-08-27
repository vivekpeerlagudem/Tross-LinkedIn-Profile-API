"""Unit tests for the ProfileParser component."""

from app.providers.parser import ProfileParser


class TestProfileParser:
    """Test suite for ProfileParser methods."""

    def test_extract_profile_info_complete(self):
        raw = {
            "profile": {
                "public_id": "test-dev",
                "urn": "urn:li:synthetic_profile:100",
                "first_name": "Test",
                "last_name": "Dev",
                "full_name": "Test Dev",
                "headline": "Senior Engineer",
                "location": "San Francisco, CA",
                "about": "Engineer bio",
                "profile_picture_url": None,
                "background_picture_url": None,
            }
        }
        extracted = ProfileParser.extract_profile_info(raw, "test-dev")
        assert extracted["public_id"] == "test-dev"
        assert extracted["full_name"] == "Test Dev"
        assert extracted["headline"] == "Senior Engineer"

    def test_extract_profile_info_fallback_name(self):
        raw = {"profile": {"first_name": "Jane", "last_name": None}}
        extracted = ProfileParser.extract_profile_info(raw, "jane-vanity")
        assert extracted["full_name"] == "Jane"

    def test_extract_experience(self):
        raw = {
            "experience": [
                {
                    "title": "Backend Dev",
                    "company": "Acme",
                    "location": "Remote",
                    "start_date": {"year": 2020, "month": 1},
                    "end_date": None,
                }
            ]
        }
        exp = ProfileParser.extract_experience(raw)
        assert len(exp) == 1
        assert exp[0]["title"] == "Backend Dev"
        assert exp[0]["company"] == "Acme"

    def test_extract_skills_string_and_dict_formats(self):
        raw = {
            "skills": [
                "Python",
                {"name": "FastAPI", "endorsement_count": 10},
            ]
        }
        skills = ProfileParser.extract_skills(raw)
        assert len(skills) == 2
        assert skills[0] == {"name": "Python", "endorsement_count": None}
        assert skills[1] == {"name": "FastAPI", "endorsement_count": 10}

    def test_extract_education_and_certifications_empty(self):
        raw = {}
        assert ProfileParser.extract_education(raw) == []
        assert ProfileParser.extract_certifications(raw) == []
        assert ProfileParser.extract_languages(raw) == []

    def test_extract_from_profile_view_wrappers(self):
        raw = {
            "profileView": {
                "profile": {
                    "firstName": "Taylor",
                    "lastName": "Swift",
                    "headline": "Lead Architect",
                },
                "positionView": {
                    "elements": [{"title": "Principal Architect", "companyName": "CloudCorp"}]
                },
                "educationView": {
                    "elements": [{"schoolName": "MIT", "degreeName": "B.S."}]
                },
                "skillView": {
                    "elements": [{"name": "Architecture", "endorsementCount": 20}]
                },
                "certificationView": {
                    "elements": [{"name": "Cloud Certified", "authorityName": "Cloud Org"}]
                },
                "languageView": {
                    "elements": [{"name": "English", "proficiency": "NATIVE"}]
                },
            }
        }
        prof = ProfileParser.extract_profile_info(raw, "taylor-swift")
        assert prof["full_name"] == "Taylor Swift"
        assert prof["headline"] == "Lead Architect"

        exp = ProfileParser.extract_experience(raw)
        assert len(exp) == 1
        assert exp[0]["title"] == "Principal Architect"

        edu = ProfileParser.extract_education(raw)
        assert len(edu) == 1
        assert edu[0]["schoolName"] == "MIT"

        skills = ProfileParser.extract_skills(raw)
        assert len(skills) == 1
        assert skills[0]["name"] == "Architecture"

        certs = ProfileParser.extract_certifications(raw)
        assert len(certs) == 1
        assert certs[0]["name"] == "Cloud Certified"

        langs = ProfileParser.extract_languages(raw)
        assert len(langs) == 1
        assert langs[0]["name"] == "English"
