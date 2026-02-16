from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.core.deps import get_current_user, get_tenant_scope
from backend.core.errors import AppError
from backend.storage.repository import now_iso, repo

router = APIRouter(tags=['incidents'])


class IncidentIn(BaseModel):
    type: str
    severity: str
    site_id: str
    camera_id: str | None = None
    description: str


class AssignIn(BaseModel):
    user_id: str


class NoteIn(BaseModel):
    note: str


@router.get('/incidents')
def list_incidents(status: str | None = None, severity: str | None = None, user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    items = repo.list_tenant('incidents', tenant)
    if status:
        items = [i for i in items if i.get('status', '').lower() == status.lower()]
    if severity:
        items = [i for i in items if i.get('severity', '').lower() == severity.lower()]
    return items


@router.post('/incidents')
def create_incident(payload: IncidentIn, user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    item = repo.create(
        'incidents',
        {
            **payload.model_dump(),
            'company_id': tenant,
            'status': 'Open',
            'assigned_to': None,
            'notes': [],
            'created_at': now_iso(),
            'closed_at': None,
        },
    )
    repo.create('alerts', {'company_id': tenant, 'message': f"Incident created: {item['type']}", 'severity': item['severity'], 'created_at': now_iso()})
    repo.append_audit('incident.create', user.get('id'), tenant, {'incident_id': item['id']})
    return item


@router.post('/incidents/{incident_id}/assign')
def assign_incident(incident_id: str, payload: AssignIn, user: dict = Depends(get_current_user)):
    incident = repo.get('incidents', incident_id)
    if not incident:
        raise AppError('Incident not found', 404)
    tenant = get_tenant_scope(user)
    if tenant and incident.get('company_id') != tenant:
        raise AppError('Forbidden', 403)
    updated = repo.update('incidents', incident_id, {'assigned_to': payload.user_id})
    repo.append_audit('incident.assign', user.get('id'), tenant, {'incident_id': incident_id, 'assigned_to': payload.user_id})
    return updated


@router.post('/incidents/{incident_id}/notes')
def add_note(incident_id: str, payload: NoteIn, user: dict = Depends(get_current_user)):
    incident = repo.get('incidents', incident_id)
    if not incident:
        raise AppError('Incident not found', 404)
    tenant = get_tenant_scope(user)
    if tenant and incident.get('company_id') != tenant:
        raise AppError('Forbidden', 403)
    notes = incident.get('notes', []) + [{'user_id': user.get('id'), 'note': payload.note, 'at': now_iso()}]
    return repo.update('incidents', incident_id, {'notes': notes})


@router.post('/incidents/{incident_id}/close')
def close_incident(incident_id: str, user: dict = Depends(get_current_user)):
    incident = repo.get('incidents', incident_id)
    if not incident:
        raise AppError('Incident not found', 404)
    tenant = get_tenant_scope(user)
    if tenant and incident.get('company_id') != tenant:
        raise AppError('Forbidden', 403)
    updated = repo.update('incidents', incident_id, {'status': 'Closed', 'closed_at': now_iso()})
    repo.append_audit('incident.close', user.get('id'), tenant, {'incident_id': incident_id})
    return updated


@router.get('/alerts')
def list_alerts(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    items = repo.list_tenant('alerts', tenant)
    return sorted(items, key=lambda x: x.get('created_at', ''), reverse=True)[:100]
