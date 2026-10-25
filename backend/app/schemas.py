from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RiskLevel(str, Enum):
    BENIGN = "Benign"
    SUSPICIOUS = "Suspicious"
    MALICIOUS = "Malicious"


class EventStatus(str, Enum):
    PENDING = "Pending"
    REVIEWED = "Reviewed"
    FALSE_POSITIVE = "False Positive"
    ESCALATED = "Escalated"


class EventCreate(BaseModel):
    raw_log: Annotated[str, Field(min_length=1, max_length=10000)]
    source: Annotated[str, Field(min_length=1, max_length=128)]

    @field_validator("raw_log", "source")
    @classmethod
    def strip_non_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v


class EventCreateBatch(BaseModel):
    events: Annotated[list[EventCreate], Field(min_length=1, max_length=500)]


class EventStatusUpdate(BaseModel):
    status: EventStatus


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    raw_log: str
    source: str
    risk_level: RiskLevel
    confidence: float
    status: EventStatus
    created_at: datetime


class EventCreateResponse(EventOut):
    pass


class StatsOut(BaseModel):
    total_events: int
    by_risk_level: dict[str, int]
    by_source: dict[str, int]


class ErrorResponse(BaseModel):
    detail: str
    errors: list[dict] | None = None
