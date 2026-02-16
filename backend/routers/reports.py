from fastapi import APIRouter, Depends
from fastapi.responses import Response

from backend.core.deps import get_current_user, get_tenant_scope
from backend.storage.repository import repo

router = APIRouter(tags=['reports'])


def _to_csv(rows: list[dict], fields: list[str]) -> str:
    lines = [','.join(fields)]
    for row in rows:
        vals = [str(row.get(f, '')) for f in fields]
        lines.append(','.join(vals))
    return '\n'.join(lines)


@router.get('/reports/incidents.csv')
def incidents_report(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    rows = repo.list_tenant('incidents', tenant)
    return Response(_to_csv(rows, ['id', 'type', 'severity', 'status', 'site_id', 'created_at']), media_type='text/csv')


@router.get('/reports/permits.csv')
def permits_report(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    rows = repo.list_tenant('permits', tenant)
    return Response(_to_csv(rows, ['id', 'title', 'risk_level', 'status', 'site_id', 'created_at']), media_type='text/csv')


@router.get('/reports/risk.csv')
def risk_report(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    rows = repo.list_tenant('risk_assessments', tenant)
    return Response(_to_csv(rows, ['id', 'hazard', 'risk_score', 'residual_score', 'level', 'created_at']), media_type='text/csv')
