from pydantic import BaseModel, Field
from typing import Any


class BehaviorEvent(BaseModel):
    type: str = Field(..., min_length=1)
    severity: int = Field(1, ge=1, le=5)
    meta: dict[str, Any] = Field(default_factory=dict)


class BehaviorAnalysisRequest(BaseModel):
    location: str = Field(..., min_length=1)
    events: list[BehaviorEvent] = Field(default_factory=list)


class BehaviorAnalysisResponse(BaseModel):
    flagged: bool
    score: int
    alerts: list[str]
    suggestions: list[str]
