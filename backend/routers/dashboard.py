from fastapi import APIRouter

from backend.storage.db import get_conn

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def dashboard():
    with get_conn() as conn:
        permits = conn.execute("SELECT risk_level, status FROM work_permits").fetchall()
        checklists_count = conn.execute("SELECT COUNT(*) AS n FROM checklists").fetchone()["n"]

    active_permits = len([p for p in permits if (p["status"] or "").lower() == "active"])
    buckets = {"Low": 0, "Medium": 0, "High": 0}
    for p in permits:
        risk = p["risk_level"] if p["risk_level"] in buckets else "Medium"
        buckets[risk] += 1

    total = max(1, len(permits))
    risk_score = round(((buckets["High"] * 80) + (buckets["Medium"] * 50) + (buckets["Low"] * 20)) / total)

    return {
        "risk_score": risk_score,
        "active_permits": active_permits,
        "smart_alerts": buckets["High"] + buckets["Medium"],
        "checklists_count": checklists_count,
        "reports": [
            {"label": "Low", "value": buckets["Low"]},
            {"label": "Medium", "value": buckets["Medium"]},
            {"label": "High", "value": buckets["High"]},
        ],
    }
