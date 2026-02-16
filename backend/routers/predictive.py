from fastapi import APIRouter
from backend.models.predictive import PredictRiskRequest, PredictRiskResponse

router = APIRouter(tags=["predictive"])


def _risk_level(score: int) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


@router.post("/core/predict-risk", response_model=PredictRiskResponse)
def predict_risk(payload: PredictRiskRequest):
    base = min(payload.historical_incidents * 7, 70)
    env = min(len(payload.environmental_factors) * 5, 30)
    score = max(0, min(100, base + env))

    level = _risk_level(score)
    if level == "High":
        rec = [
            "إيقاف العمل مؤقتًا لحين تقييم الموقع",
            "زيادة التفتيش وفرض PPE إلزامي",
            "تفعيل تنبيهات فورية للكاميرات",
        ]
    elif level == "Medium":
        rec = [
            "تعزيز إجراءات السلامة بالموقع",
            "تنفيذ قائمة تحقق قبل بدء العمل",
        ]
    else:
        rec = ["استمرار المراقبة الدورية", "تحديث تقييم المخاطر أسبوعيًا"]

    return PredictRiskResponse(risk_score=score, risk_level=level, recommendations=rec)
