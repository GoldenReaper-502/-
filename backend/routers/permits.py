from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.core.deps import get_current_user, get_tenant_scope
from backend.core.errors import AppError
from backend.storage.repository import now_iso, repo

router = APIRouter(tags=['permits'])


class PermitIn(BaseModel):
    title: str
    site_id: str
    risk_level: str
    approver: str | None = None
    checklist_items: list[str] = []


@router.get('/core/work-permits')
def list_permits(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    return repo.list_tenant('permits', tenant)


@router.post('/core/work-permits')
def create_permit(payload: PermitIn, user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    permit = repo.create(
        'permits',
        {
            **payload.model_dump(),
            'company_id': tenant,
            'status': 'draft',
            'created_by': user.get('id'),
            'created_at': now_iso(),
        },
    )
    return permit


@router.put('/core/work-permits/{permit_id}')
def update_permit(permit_id: str, payload: dict, user: dict = Depends(get_current_user)):
    permit = repo.get('permits', permit_id)
    if not permit:
        raise AppError('Permit not found', 404)
    tenant = get_tenant_scope(user)
    if tenant and permit.get('company_id') != tenant:
        raise AppError('Forbidden', 403)

    status = payload.get('status')
    role = user.get('role')
    if status in {'approved', 'rejected'} and role not in {'Supervisor', 'SafetyManager', 'CompanyAdmin', 'SuperAdmin'}:
        raise AppError('Only approvers can approve/reject permits', 403)

    updates = {k: v for k, v in payload.items() if k in {'title', 'site_id', 'risk_level', 'approver', 'checklist_items', 'status'}}
    updates['updated_at'] = now_iso()
    updated = repo.update('permits', permit_id, updates)
    repo.append_audit('permit.update', user.get('id'), tenant, {'permit_id': permit_id, 'updates': updates})
    return updated


@router.delete('/core/work-permits/{permit_id}')
def delete_permit(permit_id: str, user: dict = Depends(get_current_user)):
    permit = repo.get('permits', permit_id)
    if not permit:
        raise AppError('Permit not found', 404)
    tenant = get_tenant_scope(user)
    if tenant and permit.get('company_id') != tenant:
        raise AppError('Forbidden', 403)
    repo.delete('permits', permit_id)
    return {'ok': True, 'deleted_id': permit_id}
