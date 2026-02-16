from fastapi import APIRouter

from backend.services.store import store

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
def dashboard_overview():
    active_permits = [p for p in store.permits if p.get("status", "").lower() == "active"]
    smart_alerts = len(store.alerts) + max(1, len(store.incidents))
    incidents = store.incidents[-10:]

    risk_score = min(100, 35 + len(active_permits) * 8 + smart_alerts * 4)

    return {
        "risk_score": risk_score,
        "active_permits": len(active_permits),
        "smart_alerts": smart_alerts,
        "incidents": incidents,
        "reports": [
            {"label": "Jan", "value": max(5, risk_score - 20)},
            {"label": "Feb", "value": max(10, risk_score - 12)},
            {"label": "Mar", "value": risk_score},
        ],
        "totals": {
            "incidents": len(store.incidents),
            "near_misses": len([i for i in store.incidents if i.get("type") == "near-miss"]),
            "detections": len(store.alerts),
        },
    }
