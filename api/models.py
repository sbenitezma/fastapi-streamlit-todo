"""Pydantic models for input validation and output serialization.

This is where "garbage" is defined and rejected: empty titles, invalid statuses
or oversized lengths are turned away before touching the database.
"""

from datetime import date, datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

Status = Literal["pending", "done"]

TITLE_MAX = 200
DESCRIPTION_MAX = 2000


class TodoCreate(BaseModel):
    """Expected body for ``POST /api/todos``."""

    title: str = Field(min_length=1, max_length=TITLE_MAX)
    description: Optional[str] = Field(default=None, max_length=DESCRIPTION_MAX)
    created_at: Optional[date] = Field(
        default=None,
        description=(
            "Optional creation date (YYYY-MM-DD) so past tasks can be recorded. "
            "Defaults to the current time; may not be in the future."
        ),
    )

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title must not be empty")
        return v

    @field_validator("description")
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        return v or None

    @field_validator("created_at")
    @classmethod
    def not_in_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > datetime.now(timezone.utc).date():
            raise ValueError("created_at cannot be in the future")
        return v


class TodoUpdate(BaseModel):
    """Expected body for ``PATCH /api/todos/{id}``. Every field is optional."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=TITLE_MAX)
    description: Optional[str] = Field(default=None, max_length=DESCRIPTION_MAX)
    status: Optional[Status] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("Title must not be empty")
        return v

    @field_validator("description")
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return v.strip() or None


class TodoRead(BaseModel):
    """A task exactly as the API returns it."""

    id: int
    title: str
    description: Optional[str]
    status: Status
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
