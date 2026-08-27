"""Parser for extracting structured entities from raw profile payloads."""

from typing import Any, Dict, List, Optional


class ProfileParser:
    """Safely extracts raw profile blocks and sections from heterogeneous upstream representations."""

    @staticmethod
    def extract_profile_info(raw: Dict[str, Any], vanity_id: str) -> Dict[str, Any]:
        """Extracts core profile summary, names, headline, location, and images."""
        profile_data = (
            raw.get("profileView", {}).get("profile")
            or raw.get("profile")
            or raw
        )

        first_name = profile_data.get("first_name") or profile_data.get("firstName")
        last_name = profile_data.get("last_name") or profile_data.get("lastName")

        full_name = profile_data.get("full_name") or profile_data.get("fullName")
        if not full_name:
            if first_name and last_name:
                full_name = f"{first_name} {last_name}".strip()
            elif first_name:
                full_name = first_name
            elif last_name:
                full_name = last_name
            else:
                full_name = vanity_id

        return {
            "public_id": profile_data.get("public_id") or profile_data.get("publicIdentifier") or vanity_id,
            "urn": profile_data.get("urn") or profile_data.get("entityUrn"),
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "headline": profile_data.get("headline") or profile_data.get("occupation"),
            "location": profile_data.get("location") or profile_data.get("locationName"),
            "about": profile_data.get("about") or profile_data.get("summary"),
            "profile_picture_url": profile_data.get("profile_picture_url") or profile_data.get("pictureUrl"),
            "background_picture_url": profile_data.get("background_picture_url") or profile_data.get("backgroundUrl"),
        }

    @staticmethod
    def extract_experience(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extracts list of positions and employment history."""
        pv = raw.get("profileView", {})
        positions = (
            raw.get("positionView")
            or raw.get("positions")
            or raw.get("experience")
            or pv.get("positionView")
            or pv.get("positions")
            or []
        )
        if isinstance(positions, dict):
            positions = positions.get("elements", [])
        return [p for p in positions if isinstance(p, dict)]

    @staticmethod
    def extract_education(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extracts list of educational institutions and degrees."""
        pv = raw.get("profileView", {})
        education = (
            raw.get("educationView")
            or raw.get("educations")
            or raw.get("schools")
            or raw.get("education")
            or pv.get("educationView")
            or pv.get("educations")
            or []
        )
        if isinstance(education, dict):
            education = education.get("elements", [])
        return [e for e in education if isinstance(e, dict)]

    @staticmethod
    def extract_skills(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extracts skills list."""
        pv = raw.get("profileView", {})
        skills = (
            raw.get("skillView")
            or raw.get("skills")
            or pv.get("skillView")
            or pv.get("skills")
            or []
        )
        if isinstance(skills, dict):
            skills = skills.get("elements", [])

        normalized_skills = []
        for s in skills:
            if isinstance(s, str):
                normalized_skills.append({"name": s, "endorsement_count": None})
            elif isinstance(s, dict):
                name = s.get("name") or s.get("skillName")
                if name:
                    normalized_skills.append({
                        "name": name,
                        "endorsement_count": s.get("endorsement_count") or s.get("endorsementCount"),
                    })
        return normalized_skills

    @staticmethod
    def extract_certifications(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extracts certifications and licenses."""
        pv = raw.get("profileView", {})
        certs = (
            raw.get("certificationView")
            or raw.get("certifications")
            or raw.get("licenses")
            or pv.get("certificationView")
            or pv.get("certifications")
            or []
        )
        if isinstance(certs, dict):
            certs = certs.get("elements", [])
        return [c for c in certs if isinstance(c, dict)]

    @staticmethod
    def extract_languages(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extracts languages spoken."""
        pv = raw.get("profileView", {})
        languages = (
            raw.get("languageView")
            or raw.get("languages")
            or pv.get("languageView")
            or pv.get("languages")
            or []
        )
        if isinstance(languages, dict):
            languages = languages.get("elements", [])

        normalized_langs = []
        for lang in languages:
            if isinstance(lang, str):
                normalized_langs.append({"name": lang, "proficiency": None})
            elif isinstance(lang, dict):
                name = lang.get("name") or lang.get("language")
                if name:
                    normalized_langs.append({
                        "name": name,
                        "proficiency": lang.get("proficiency"),
                    })
        return normalized_langs
