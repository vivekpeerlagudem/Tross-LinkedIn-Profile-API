"""Standard error response schemas."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code", examples=["INVALID_URL", "PROFILE_NOT_FOUND"])
    message: str = Field(..., description="Human-readable explanation of the error")
    details: Optional[Any] = Field(None, description="Optional extra error details or validation breakdown")


class ErrorResponse(BaseModel):
    status: str = Field("error", examples=["error"])
    error: ErrorDetail
