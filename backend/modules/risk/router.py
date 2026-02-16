from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/core", tags=["Risk"])


class PredictRiskRequest(BaseModel):
    location: str
    historical_incidents: int = Field(ge=0)
    environmental_factors: list[str] = Field(default_factory=list)


class PredictRiskResponse(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    recommendations: list[str]


@router.post("/predict-risk", response_model=PredictRiskResponse)
def predict_risk(payload: PredictRiskRequest):
    base = min(100, payload.historical_incidents * 8)
    env_weight = min(40, len(payload.environmental_factors) * 7)
    risk_score = min(100, base + env_weight + 20)

    if risk_score < 40:
        level = "Low"
    elif risk_score < 75:
        level = "Medium"
    else:
        level = "High"

    recommendations = [
        "Increase toolbox talks frequency",
        "Run focused HSE audit in target location",
        "Verify permit-to-work compliance",
    ]

    if "heat" in [f.lower() for f in payload.environmental_factors]:
        recommendations.append("Apply heat stress controls and hydration schedule")

    return PredictRiskResponse(
        risk_score=risk_score,
        risk_level=level,
        recommendations=recommendations,
    )
