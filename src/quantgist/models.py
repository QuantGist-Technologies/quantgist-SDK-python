from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Event(BaseModel):
    id: str
    title: str
    country: str
    currency: str
    release_time: datetime
    impact: Literal["low", "medium", "high"]
    forecast: float | None = None
    previous: float | None = None
    actual: float | None = None
    surprise_score: float | None = None
    affected_symbols: list[str] = Field(default_factory=list)
    source: str


class EventsResponse(BaseModel):
    data: list[Event]
    meta: ResponseMeta


class ResponseMeta(BaseModel):
    total: int
    page: int
    per_page: int
    rate_limit_remaining: int | None = None
