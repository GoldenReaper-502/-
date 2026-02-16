from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.core.deps import get_current_user, get_tenant_scope
from backend.storage.repository import now_iso, repo

router = APIRouter(tags=['core-compat'])


class DetectRequest(BaseModel):
    source: str = 'camera'
    payload: dict = Field(default_factory=dict)


class ChatRequest(BaseModel):
    message: str


class IncidentRequest(BaseModel):
    title: str
    location: str
    severity: str = 'medium'


@router.post('/core/detect')
def detect_objects(payload: DetectRequest, user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    detection = {
        'id': str(uuid4()),
        'source': payload.source,
        'payload': payload.payload,
        'message': 'Detection analyzed',
    }
    repo.create('alerts', {'company_id': tenant, 'message': 'Detection event', 'severity': 'Medium', 'created_at': now_iso()})
    return {'ok': True, 'detections': [detection]}


@router.post('/core/chat')
def chat(payload: ChatRequest, user: dict = Depends(get_current_user)):
    return {'ok': True, 'reply': f"AI mock reply for {user.get('role')}: {payload.message}"}


@router.post('/core/incident')
def create_incident(payload: IncidentRequest, user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    incident = repo.create(
        'incidents',
        {
            'company_id': tenant,
            'site_id': 'n/a',
            'camera_id': None,
            'type': payload.title,
            'severity': payload.severity.title(),
            'status': 'Open',
            'description': payload.location,
            'assigned_to': None,
            'notes': [],
            'created_at': now_iso(),
            'closed_at': None,
        },
    )
    return {'ok': True, 'incident': incident}


@router.post('/core/near-miss')
def create_near_miss(payload: IncidentRequest, user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    near_miss = repo.create(
        'incidents',
        {
            'company_id': tenant,
            'site_id': 'n/a',
            'camera_id': None,
            'type': f"NearMiss:{payload.title}",
            'severity': payload.severity.title(),
            'status': 'Open',
            'description': payload.location,
            'assigned_to': None,
            'notes': [],
            'created_at': now_iso(),
            'closed_at': None,
        },
    )
    return {'ok': True, 'near_miss': near_miss}
