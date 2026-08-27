"""API route definitions for health and profile endpoints."""

from fastapi import APIRouter, Depends, status
from app.api.dependencies import get_profile_service
from app.core.config import settings
from app.models.errors import ErrorResponse
from app.models.request import ProfileRequest
from app.models.response import ProfileResponse
from app.services.profile_service import ProfileService

router = APIRouter()


@router.get(
    "/health",
    tags=["Health"],
    summary="Health Check Probe",
    description="Returns the current application health status, version, and active provider.",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    """Returns application status and active data provider configuration."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "provider": settings.DATA_PROVIDER.value,
    }


@router.post(
    "/v1/profile",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    tags=["Profile"],
    summary="Get Normalized LinkedIn Profile",
    description=(
        "Accepts a valid LinkedIn profile URL, retrieves profile details, and returns "
        "a normalized, structured JSON representation containing Profile, Experience, "
        "Education, Skills, Certifications, Languages, and extraction metadata."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Invalid LinkedIn Profile URL"},
        404: {"model": ErrorResponse, "description": "Profile Not Found"},
        429: {"model": ErrorResponse, "description": "Rate Limited"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        502: {"model": ErrorResponse, "description": "Upstream Provider Unavailable"},
    },
)
async def get_profile(
    payload: ProfileRequest,
    service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    """Retrieves and normalizes profile data from the given URL."""
    return await service.get_profile_by_url(payload.url)
