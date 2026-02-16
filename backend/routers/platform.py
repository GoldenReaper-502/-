from fastapi import APIRouter

from backend.core.config import settings

router = APIRouter(tags=['platform'])


@router.get('/platform/info')
def platform_info():
    return {
        'name': settings.app_name,
        'version': settings.version,
        'tagline': 'HAZM TUWAIQ — AI Safety Platform',
        'endpoints': {
            'docs': f"{settings.api_prefix}/docs",
            'openapi': f"{settings.api_prefix}/openapi.json",
            'health': '/health',
        },
    }
