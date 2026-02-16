from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel

from backend.core.deps import get_current_user, get_tenant_scope
from backend.storage.repository import now_iso, repo

router = APIRouter(tags=['risk'])


class RiskAssessmentIn(BaseModel):
    hazard: str
    likelihood: int
    severity: int
    controls: list[str]
    residual_score: int


def _level(score: int) -> str:
    if score >= 15:
        return 'High'
    if score >= 8:
        return 'Medium'
    return 'Low'


@router.post('/core/predict-risk')
def predict_risk(payload: dict, user: dict = Depends(get_current_user)):
    historical = int(payload.get('historical_incidents', 0))
    factors = payload.get('environmental_factors', []) or []
    score = max(0, min(100, historical * 8 + len(factors) * 6 + 20))
    level = 'High' if score >= 70 else 'Medium' if score >= 40 else 'Low'
    rec = ['Daily toolbox talk', 'Audit permits', 'Verify PPE usage']
    if level == 'High':
        rec.insert(0, 'Immediate mitigation plan required')
    return {'risk_score': score, 'risk_level': level, 'recommendations': rec}


@router.get('/risk-assessments')
def list_risk(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    return repo.list_tenant('risk_assessments', tenant)


@router.post('/risk-assessments')
def create_risk(payload: RiskAssessmentIn, user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    risk_score = payload.likelihood * payload.severity
    return repo.create(
        'risk_assessments',
        {
            **payload.model_dump(),
            'company_id': tenant,
            'risk_score': risk_score,
            'level': _level(risk_score),
            'created_at': now_iso(),
        },
    )


@router.get('/risk-assessments/export.csv')
def export_risk_csv(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    rows = repo.list_tenant('risk_assessments', tenant)
    lines = ['id,hazard,likelihood,severity,risk_score,residual_score,level']
    for r in rows:
        lines.append(f"{r.get('id')},{r.get('hazard')},{r.get('likelihood')},{r.get('severity')},{r.get('risk_score')},{r.get('residual_score')},{r.get('level')}")
    return Response('\n'.join(lines), media_type='text/csv')
