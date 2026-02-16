from fastapi import APIRouter, Depends

from backend.core.deps import get_current_user, get_tenant_scope
from backend.storage.repository import repo

router = APIRouter(tags=['system'])


@router.get('/core/system/status')
def system_status(user: dict = Depends(get_current_user)):
    tenant = get_tenant_scope(user)
    return {
        'healthy': True,
        'status': 'ok',
        'message': 'Core API operational',
        'modules_status': {
            'auth': 'ok',
            'cameras': 'ok',
            'incidents': 'ok',
            'permits': 'ok',
            'risk': 'ok',
            'assistant': 'mock-ready',
        },
        'counts': {
            'users': len(repo.list_tenant('users', tenant)),
            'cameras': len(repo.list_tenant('cameras', tenant)),
            'incidents': len(repo.list_tenant('incidents', tenant)),
            'permits': len(repo.list_tenant('permits', tenant)),
        },
    }
