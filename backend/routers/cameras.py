from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.core.deps import get_current_user, get_tenant_scope
from backend.core.errors import AppError
from backend.storage.repository import repo, now_iso

router = APIRouter(tags=['cameras'])


class CameraIn(BaseModel):
    name: str
    site_id: str
    stream_url: str
    vendor: str
    location: str
    status: str = 'offline'


@router.get('/cameras')
def list_cameras(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    return repo.list_tenant('cameras', tenant)


@router.post('/cameras')
def create_camera(payload: CameraIn, user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    camera = repo.create('cameras', {**payload.model_dump(), 'company_id': tenant, 'updated_at': now_iso()})
    repo.append_audit('camera.create', user.get('id'), tenant, {'camera_id': camera['id']})
    return camera


@router.get('/cameras/{camera_id}')
def get_camera(camera_id: str, user: dict = Depends(get_current_user)):
    cam = repo.get('cameras', camera_id)
    if not cam:
        raise AppError('Camera not found', 404)
    tenant = get_tenant_scope(user)
    if tenant and cam.get('company_id') != tenant:
        raise AppError('Forbidden', 403)
    return cam


@router.post('/cameras/{camera_id}/test')
def test_camera(camera_id: str, user: dict = Depends(get_current_user)):
    cam = repo.get('cameras', camera_id)
    if not cam:
        raise AppError('Camera not found', 404)
    tenant = get_tenant_scope(user)
    if tenant and cam.get('company_id') != tenant:
        raise AppError('Forbidden', 403)
    ok = cam.get('status') == 'online' or 'rtsp://' in cam.get('stream_url', '')
    return {
        'camera_id': camera_id,
        'success': bool(ok),
        'message': 'Mock camera test passed' if ok else 'Mock camera test failed',
        'adapter': {
            'rtsp_onvif_discovery': 'TODO',
            'webrtc_hls_proxy': 'TODO',
        },
    }
