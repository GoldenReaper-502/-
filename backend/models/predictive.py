from pydantic import BaseModel, Field
from typing import Any


class PredictRiskRequest(BaseModel):
    location: str = Field(..., min_length=1)
    historical_incidents: int = Field(0, ge=0)
    environmental_factors: list[Any] = Field(default_factory=list)


class PredictRiskResponse(BaseModel):
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: str
    recommendations: list[str]
