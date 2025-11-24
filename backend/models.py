"""Pydantic models shared across the LeetSearch backend."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Profile(BaseModel):
    """LeetCode profile payload stored in the local cache."""

    username: str
    realName: Optional[str] = None
    aboutMe: Optional[str] = None
    countryName: Optional[str] = None
    ranking: Optional[int] = None
    school: Optional[str] = None
    company: Optional[str] = None
    websites: Optional[List[str]] = None


class ProfileResponse(BaseModel):
    """API response envelope for a single profile."""

    cached: bool
    profile: Profile


class CollegeUserResult(BaseModel):
    """Subset of profile data returned from college searches."""

    username: str
    realName: Optional[str] = None
    school: Optional[str] = None
    ranking: Optional[int] = None
    country: Optional[str] = None


class CollegeSearchResponse(BaseModel):
    """Response format for /search/college."""

    query: str
    total: int
    results: List[CollegeUserResult]


class HealthResponse(BaseModel):
    """Simple health/readiness payload for monitoring."""

    status: str = "ok"
    profiles_cached: int
    last_updated: Optional[datetime] = None


class RefreshRequest(BaseModel):
    """Body accepted by /refresh to trigger a scraper cycle."""

    pages: int = Field(
        default=2,
        ge=1,
        le=10,
        description="How many contest ranking pages to scrape in one cycle.",
    )
    max_users: int = Field(
        default=25,
        ge=1,
        le=200,
        description="Upper bound on profiles fetched per refresh cycle.",
    )


class RefreshResponse(BaseModel):
    """Acknowledgement from the refresh endpoint."""

    started: bool
    pages: int
    max_users: int
    message: str

