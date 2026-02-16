from fastapi import APIRouter
from backend.models.behavior import BehaviorAnalysisRequest, BehaviorAnalysisResponse

router = APIRouter(tags=["behavior"])


@router.post("/core/behavior-analysis", response_model=BehaviorAnalysisResponse)
def behavior_analysis(payload: BehaviorAnalysisRequest):
    score = 0
    alerts = []
    for ev in payload.events:
        score += ev.severity * 10
        if ev.type.upper() in ["PPE_MISSING", "FALL_RISK", "FIRE_RISK", "UNSAFE_MACHINE"]:
            alerts.append(f"سلوك خطر: {ev.type} (Severity {ev.severity})")

    score = min(score, 100)
    flagged = score >= 50 or len(alerts) > 0

    if flagged:
        suggestions = [
            "توجيه العامل للتقيد بإجراءات السلامة",
            "مراجعة معدات الوقاية الشخصية PPE",
            "إجراء توعية سريعة بالموقع",
        ]
    else:
        suggestions = ["لا توجد سلوكيات خطرة حالياً"]

    return BehaviorAnalysisResponse(flagged=flagged, score=score, alerts=alerts, suggestions=suggestions)
