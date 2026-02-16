from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.errors import AppError, app_error_handler, generic_error_handler
from backend.core.logging import setup_logging
from backend.storage.db import init_db

from backend.routers.platform import router as platform_router
from backend.routers.predictive import router as predictive_router
from backend.routers.behavior import router as behavior_router
from backend.routers.permits import router as permits_router
from backend.routers.checklists import router as checklists_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.core_compat import router as core_compat_router

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
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, generic_error_handler)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"ok": True}


app.include_router(platform_router, prefix=settings.api_prefix)
app.include_router(core_compat_router, prefix=settings.api_prefix)
app.include_router(predictive_router, prefix=settings.api_prefix)
app.include_router(behavior_router, prefix=settings.api_prefix)
app.include_router(permits_router, prefix=settings.api_prefix)
app.include_router(checklists_router, prefix=settings.api_prefix)
app.include_router(dashboard_router, prefix=settings.api_prefix)
