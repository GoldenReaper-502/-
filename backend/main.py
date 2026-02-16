from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.errors import AppError, app_error_handler, generic_error_handler
from backend.core.logging import setup_logging
from backend.routers.assistant import router as assistant_router
from backend.routers.auth import router as auth_router
from backend.routers.cameras import router as cameras_router
from backend.routers.checklists import router as checklists_router
from backend.routers.companies import router as companies_router
from backend.routers.core_compat import router as core_compat_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.dev import router as dev_router
from backend.routers.incidents import router as incidents_router
from backend.routers.permits import router as permits_router
from backend.routers.platform import router as platform_router
from backend.routers.reports import router as reports_router
from backend.routers.risk import router as risk_router
from backend.routers.system import router as system_router
from backend.storage.repository import repo


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url=f"{settings.api_prefix}/docs",
        openapi_url=f"{settings.api_prefix}/openapi.json",
        redoc_url=f"{settings.api_prefix}/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)

    @app.on_event('startup')
    def on_startup() -> None:
        repo.load()

    @app.get('/health')
    def health():
        return {'ok': True, 'service': settings.app_name}

    for router in [
        platform_router,
        auth_router,
        companies_router,
        system_router,
        dashboard_router,
        cameras_router,
        incidents_router,
        risk_router,
        permits_router,
        checklists_router,
        reports_router,
        assistant_router,
        core_compat_router,
        dev_router,
    ]:
        app.include_router(router, prefix=settings.api_prefix)

    return app


app = create_app()


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('backend.main:app', host='127.0.0.1', port=8000, reload=True)
