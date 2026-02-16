from datetime import datetime, timedelta

from fastapi import APIRouter, Depends

from backend.core.deps import get_current_user, get_tenant_scope
from backend.storage.repository import repo

router = APIRouter(tags=['dashboard'])


def _count_recent(items: list[dict], days: int = 7) -> int:
    threshold = datetime.utcnow() - timedelta(days=days)
    count = 0
    for item in items:
        created = item.get('created_at')
        if not created:
            continue
        try:
            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            if dt.replace(tzinfo=None) >= threshold:
                count += 1
        except Exception:
            continue
    return count


@router.get('/dashboard')
def dashboard(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    incidents = repo.list_tenant('incidents', tenant)
    permits = repo.list_tenant('permits', tenant)
    inspections = repo.list_tenant('inspections', tenant)
    alerts = repo.list_tenant('alerts', tenant)

    open_inc = len([i for i in incidents if i.get('status') == 'Open'])
    closed_inc = len([i for i in incidents if i.get('status') == 'Closed'])
    active_permits = len([p for p in permits if p.get('status') in {'approved', 'active'}])
    expired_permits = len([p for p in permits if p.get('status') in {'closed', 'expired', 'rejected'}])

    risk_values = []
    for p in permits:
        level = p.get('risk_level', 'Medium')
        risk_values.append(80 if level == 'High' else 50 if level == 'Medium' else 20)
    global_risk = round(sum(risk_values) / max(1, len(risk_values)))

    return {
        'daily_weekly': {
            'incidents_last_24h': _count_recent(incidents, 1),
            'incidents_last_7d': _count_recent(incidents, 7),
            'inspections_last_7d': _count_recent(inspections, 7),
            'permits_last_7d': _count_recent(permits, 7),
        },
        'kpis': {
            'incidents_open': open_inc,
            'incidents_closed': closed_inc,
            'permits_active': active_permits,
            'permits_expired': expired_permits,
            'global_risk_score': global_risk,
            'smart_alerts': len(alerts),
        },
        'charts': {
            'incidents_by_status': [
                {'label': 'Open', 'value': open_inc},
                {'label': 'Closed', 'value': closed_inc},
            ],
            'permits_by_status': [
                {'label': 'Active', 'value': active_permits},
                {'label': 'Expired/Closed', 'value': expired_permits},
            ],
        },
    }
