from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.errors import register_exception_handlers
from backend.core.logging_config import setup_logging, logger
from backend.services.store import store, InMemoryStore
from backend.modules.core.router import router as core_router
from backend.modules.risk.router import router as risk_router
from backend.modules.behavior.router import router as behavior_router
from backend.modules.work_permits.router import router as permits_router
from backend.modules.checklists.router import router as checklists_router
from backend.modules.dashboard.router import router as dashboard_router


def get_store() -> InMemoryStore:
    return store


setup_logging()
app = FastAPI(title="HAZM TUWAIQ API", version="1.1.0", docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:4173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

api = FastAPI()

app.include_router(core_router, prefix="/api")
app.include_router(risk_router, prefix="/api")
app.include_router(behavior_router, prefix="/api")
app.include_router(permits_router, prefix="/api")
app.include_router(checklists_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


@app.get("/api/health")
def health(_: InMemoryStore = Depends(get_store)):
    return {"ok": True, "message": "Service healthy"}


logger.info("HAZM TUWAIQ API initialized")
