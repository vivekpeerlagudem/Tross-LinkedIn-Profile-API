"""Data normalizer converting parsed raw dictionaries into standardized Pydantic models."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from app.models.response import (
    CertificationItem,
    EducationItem,
    ExperienceItem,
    LanguageItem,
    LocationInfo,
    ProfileData,
    ProfileInfo,
    ProfileMetadata,
    SkillItem,
    YearMonth,
)
from app.utils.url import get_canonical_profile_url


class ProfileNormalizer:
    """Normalizes parsed profile components into strictly-typed response models."""

    @staticmethod
    def normalize_year_month(val: Any) -> Optional[YearMonth]:
        """Normalizes date input from integer, dict, or ISO-formatted string into YearMonth."""
        if not val:
            return None

        if isinstance(val, YearMonth):
            return val

        if isinstance(val, dict):
            year = val.get("year")
            month = val.get("month")
            if year is not None:
                try:
                    return YearMonth(year=int(year), month=int(month) if month is not None else None)
                except (ValueError, TypeError):
                    pass

        if isinstance(val, (int, float)):
            return YearMonth(year=int(val), month=None)

        if isinstance(val, str):
            val = val.strip()
            # Handle YYYY-MM
            if "-" in val:
                parts = val.split("-")
                try:
                    year = int(parts[0])
                    month = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
                    return YearMonth(year=year, month=month)
                except ValueError:
                    pass
            elif val.isdigit() and len(val) == 4:
                return YearMonth(year=int(val), month=None)

        return None

    @staticmethod
    def normalize_location(raw_loc: Any) -> Optional[LocationInfo]:
        """Normalizes location representations into LocationInfo."""
        if not raw_loc:
            return None

        if isinstance(raw_loc, str):
            raw_str = raw_loc.strip()
            if not raw_str:
                return None
            parts = [p.strip() for p in raw_str.split(",") if p.strip()]
            city = parts[0] if len(parts) > 0 else None
            state = parts[1] if len(parts) > 2 else None
            country = parts[-1] if len(parts) > 1 else None
            return LocationInfo(city=city, state=state, country=country, raw=raw_str)

        if isinstance(raw_loc, dict):
            raw_str = raw_loc.get("raw") or raw_loc.get("name") or raw_loc.get("defaultLocalizedName")
            return LocationInfo(
                city=raw_loc.get("city"),
                state=raw_loc.get("state"),
                country=raw_loc.get("country"),
                raw=raw_str,
            )

        return None

    @classmethod
    def normalize(
        cls,
        raw_parsed: Dict[str, Any],
        vanity_id: str,
        provider_name: str,
    ) -> ProfileData:
        """Transforms parsed dictionary structure into validated ProfileData model."""
        prof_dict = raw_parsed.get("profile", {})

        # Location normalization
        loc_info = cls.normalize_location(prof_dict.get("location"))

        profile = ProfileInfo(
            public_id=prof_dict.get("public_id") or vanity_id,
            urn=prof_dict.get("urn"),
            first_name=prof_dict.get("first_name"),
            last_name=prof_dict.get("last_name"),
            full_name=prof_dict.get("full_name") or vanity_id,
            headline=prof_dict.get("headline"),
            location=loc_info,
            about=prof_dict.get("about"),
            profile_picture_url=prof_dict.get("profile_picture_url"),
            background_picture_url=prof_dict.get("background_picture_url"),
            profile_url=get_canonical_profile_url(vanity_id),
        )

        # Experience normalization
        experience: List[ExperienceItem] = []
        for exp in raw_parsed.get("experience", []):
            start = cls.normalize_year_month(exp.get("start_date") or exp.get("timePeriod", {}).get("startDate"))
            end = cls.normalize_year_month(exp.get("end_date") or exp.get("timePeriod", {}).get("endDate"))
            is_current = exp.get("is_current", exp.get("current", end is None))

            experience.append(
                ExperienceItem(
                    title=exp.get("title") or "Position",
                    company=exp.get("company") or exp.get("companyName") or "Organization",
                    company_urn=exp.get("company_urn") or exp.get("companyUrn"),
                    location=exp.get("location") or exp.get("locationName"),
                    start_date=start,
                    end_date=end,
                    is_current=bool(is_current),
                    description=exp.get("description"),
                    employment_type=exp.get("employment_type") or exp.get("employmentType"),
                )
            )

        # Education normalization
        education: List[EducationItem] = []
        for edu in raw_parsed.get("education", []):
            start_yr = edu.get("start_year")
            end_yr = edu.get("end_year")
            if not start_yr and isinstance(edu.get("timePeriod"), dict):
                start_yr = edu["timePeriod"].get("startDate", {}).get("year")
            if not end_yr and isinstance(edu.get("timePeriod"), dict):
                end_yr = edu["timePeriod"].get("endDate", {}).get("year")

            education.append(
                EducationItem(
                    school=edu.get("school") or edu.get("schoolName") or "Institution",
                    school_urn=edu.get("school_urn") or edu.get("schoolUrn"),
                    degree=edu.get("degree") or edu.get("degreeName"),
                    field_of_study=edu.get("field_of_study") or edu.get("fieldsOfStudy") or edu.get("fieldOfStudy"),
                    start_year=int(start_yr) if start_yr else None,
                    end_year=int(end_yr) if end_yr else None,
                    description=edu.get("description"),
                    activities=edu.get("activities") or edu.get("activitiesAndSocieties"),
                )
            )

        # Skills normalization
        skills: List[SkillItem] = []
        for sk in raw_parsed.get("skills", []):
            if isinstance(sk, dict) and sk.get("name"):
                skills.append(
                    SkillItem(
                        name=sk["name"],
                        endorsement_count=sk.get("endorsement_count"),
                    )
                )

        # Certifications normalization
        certifications: List[CertificationItem] = []
        for cert in raw_parsed.get("certifications", []):
            start = cls.normalize_year_month(cert.get("start_date") or cert.get("timePeriod", {}).get("startDate"))
            end = cls.normalize_year_month(cert.get("end_date") or cert.get("timePeriod", {}).get("endDate"))
            certifications.append(
                CertificationItem(
                    name=cert.get("name") or cert.get("name_str") or "Certification",
                    authority=cert.get("authority") or cert.get("authorityName"),
                    license_number=cert.get("license_number") or cert.get("licenseNumber"),
                    url=cert.get("url"),
                    start_date=start,
                    end_date=end,
                )
            )

        # Languages normalization
        languages: List[LanguageItem] = []
        for lang in raw_parsed.get("languages", []):
            if isinstance(lang, dict) and lang.get("name"):
                languages.append(
                    LanguageItem(
                        name=lang["name"],
                        proficiency=lang.get("proficiency"),
                    )
                )

        # Sections presence evaluation
        sections_found: List[str] = ["profile"]
        sections_missing: List[str] = []
        warnings: List[str] = []

        if experience:
            sections_found.append("experience")
        else:
            sections_missing.append("experience")

        if education:
            sections_found.append("education")
        else:
            sections_missing.append("education")

        if skills:
            sections_found.append("skills")
        else:
            sections_missing.append("skills")

        if certifications:
            sections_found.append("certifications")
        else:
            sections_missing.append("certifications")

        if languages:
            sections_found.append("languages")
        else:
            sections_missing.append("languages")

        metadata = ProfileMetadata(
            fetched_at=datetime.utcnow(),
            provider=provider_name,
            sections_found=sections_found,
            sections_missing=sections_missing,
            warnings=warnings,
        )

        return ProfileData(
            profile=profile,
            experience=experience,
            education=education,
            skills=skills,
            certifications=certifications,
            languages=languages,
            metadata=metadata,
        )
