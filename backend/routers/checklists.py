from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.core.deps import get_current_user, get_tenant_scope
from backend.storage.repository import now_iso, repo

router = APIRouter(tags=['checklists'])


class ChecklistIn(BaseModel):
    name: str
    equipment_type: str | None = None
    camera_id: str | None = None
    items: list[str]


class InspectionIn(BaseModel):
    template_id: str | None = None
    score: int
    findings: list[str]
    attachments: list[str] = []


@router.get('/core/checklists')
def list_checklists(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    return repo.list_tenant('checklists', tenant)


@router.post('/core/checklists')
def create_checklist(payload: ChecklistIn, user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    return repo.create(
        'checklists',
        {
            **payload.model_dump(),
            'company_id': tenant,
            'created_at': now_iso(),
            'updated_at': now_iso(),
        },
    )


@router.get('/inspections')
def inspections(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    return repo.list_tenant('inspections', tenant)


@router.post('/inspections')
def create_inspection(payload: InspectionIn, user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    return repo.create(
        'inspections',
        {
            **payload.model_dump(),
            'company_id': tenant,
            'created_at': now_iso(),
        },
    )
