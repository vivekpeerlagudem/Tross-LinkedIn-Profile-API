"""Structured response schemas for profile information."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class YearMonth(BaseModel):
    year: Optional[int] = Field(None, description="Year (e.g. 2023)")
    month: Optional[int] = Field(None, description="Month (1-12)")


class LocationInfo(BaseModel):
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State / Province")
    country: Optional[str] = Field(None, description="Country name")
    raw: Optional[str] = Field(None, description="Raw formatted location string as shown on profile")


class ProfileInfo(BaseModel):
    public_id: str = Field(..., description="LinkedIn vanity identifier")
    urn: Optional[str] = Field(None, description="Unique LinkedIn URN identifier if available")
    first_name: Optional[str] = Field(None, description="Given / first name")
    last_name: Optional[str] = Field(None, description="Family / last name")
    full_name: str = Field(..., description="Full display name")
    headline: Optional[str] = Field(None, description="Profile headline / professional title")
    location: Optional[LocationInfo] = Field(None, description="Location details")
    about: Optional[str] = Field(None, description="About summary section text")
    profile_picture_url: Optional[str] = Field(None, description="Profile avatar image URL")
    background_picture_url: Optional[str] = Field(None, description="Profile background banner URL")
    profile_url: str = Field(..., description="Canonical HTTPS profile URL")


class ExperienceItem(BaseModel):
    title: str = Field(..., description="Job title / role")
    company: str = Field(..., description="Company / organization name")
    company_urn: Optional[str] = Field(None, description="Company URN if present")
    location: Optional[str] = Field(None, description="Work location")
    start_date: Optional[YearMonth] = Field(None, description="Employment start date")
    end_date: Optional[YearMonth] = Field(None, description="Employment end date (null if current)")
    is_current: bool = Field(False, description="True if this is the user's active/current position")
    description: Optional[str] = Field(None, description="Job duties and description text")
    employment_type: Optional[str] = Field(None, description="Full-time, Part-time, Contract, etc.")


class EducationItem(BaseModel):
    school: str = Field(..., description="University / Institution name")
    school_urn: Optional[str] = Field(None, description="School URN if present")
    degree: Optional[str] = Field(None, description="Degree or certificate title (e.g. B.S., M.S.)")
    field_of_study: Optional[str] = Field(None, description="Major / field of study")
    start_year: Optional[int] = Field(None, description="Start year")
    end_year: Optional[int] = Field(None, description="End/Graduation year")
    description: Optional[str] = Field(None, description="Activities, societies or notes")
    activities: Optional[str] = Field(None, description="Societies and extracurriculars")


class SkillItem(BaseModel):
    name: str = Field(..., description="Skill name")
    endorsement_count: Optional[int] = Field(None, description="Number of peer endorsements")


class CertificationItem(BaseModel):
    name: str = Field(..., description="Certification / License name")
    authority: Optional[str] = Field(None, description="Issuing organization")
    license_number: Optional[str] = Field(None, description="License or credential ID")
    url: Optional[str] = Field(None, description="Verification or credential URL")
    start_date: Optional[YearMonth] = Field(None, description="Issue date")
    end_date: Optional[YearMonth] = Field(None, description="Expiration date (null if does not expire)")


class LanguageItem(BaseModel):
    name: str = Field(..., description="Language name")
    proficiency: Optional[str] = Field(None, description="Proficiency level (e.g. Native, Professional working)")


class ProfileMetadata(BaseModel):
    fetched_at: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp of retrieval")
    provider: str = Field(..., description="Active data provider name (e.g. 'mock', 'candidate')")
    sections_found: List[str] = Field(..., description="List of profile sections present with data")
    sections_missing: List[str] = Field(..., description="List of empty or missing sections")
    warnings: List[str] = Field(default_factory=list, description="Any extraction notes or non-fatal warnings")


class ProfileData(BaseModel):
    profile: ProfileInfo
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    skills: List[SkillItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    languages: List[LanguageItem] = Field(default_factory=list)
    metadata: ProfileMetadata


class ProfileResponse(BaseModel):
    status: str = Field("success", description="Status code indicating success")
    data: ProfileData
