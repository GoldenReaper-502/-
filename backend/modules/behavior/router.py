from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/core", tags=["Behavior"])


class BehaviorEvent(BaseModel):
    worker_id: str
    event_type: str
    duration_seconds: int = Field(default=0, ge=0)
    confidence: float = Field(default=0.5, ge=0, le=1)


class BehaviorRequest(BaseModel):
    location: str
    events: list[BehaviorEvent] = Field(default_factory=list)


class BehaviorResponse(BaseModel):
    risk_alert: bool
    risk_score: int
    findings: list[str]
    recommendation: str


@router.post("/behavior-analysis", response_model=BehaviorResponse)
def behavior_analysis(payload: BehaviorRequest):
    risky_types = {"no_helmet", "unsafe_posture", "restricted_zone_entry", "running"}

    findings: list[str] = []
    score = 0
    for event in payload.events:
        if event.event_type in risky_types:
            findings.append(f"{event.worker_id}: {event.event_type}")
            score += int(20 * event.confidence) + min(20, event.duration_seconds // 10)

    score = min(100, score)
    risk_alert = score >= 40

    return BehaviorResponse(
        risk_alert=risk_alert,
        risk_score=score,
        findings=findings,
        recommendation=(
            "Immediate supervisor intervention required" if risk_alert else "Behavior within acceptable threshold"
        ),
    )
