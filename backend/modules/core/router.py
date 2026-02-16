from fastapi import APIRouter
from pydantic import BaseModel, Field
from uuid import uuid4

from backend.modules.core.schemas import PlatformInfo, SystemStatus, GenericResponse
from backend.services.store import store

router = APIRouter(tags=["Core"])


class DetectRequest(BaseModel):
    source: str = "camera"
    payload: dict = Field(default_factory=dict)


class ChatRequest(BaseModel):
    message: str


class IncidentRequest(BaseModel):
    title: str
    location: str
    severity: str = "medium"


@router.get("/platform/info", response_model=PlatformInfo)
def platform_info():
    return PlatformInfo()


@router.get("/core/system/status", response_model=SystemStatus)
def system_status():
    return SystemStatus()


@router.post("/core/detect")
def detect_objects(payload: DetectRequest):
    alert = {
        "id": str(uuid4()),
        "type": "detection",
        "source": payload.source,
        "payload": payload.payload,
        "message": "Detection analyzed",
    }
    with store.lock:
        store.alerts.append(alert)
    return {"detections": [alert], "ok": True}


@router.post("/core/chat", response_model=GenericResponse)
def chat(payload: ChatRequest):
    return GenericResponse(ok=True, message="AI assistant response", data={"reply": f"Received: {payload.message}"})


@router.post("/core/incident")
def create_incident(payload: IncidentRequest):
    incident = {"id": str(uuid4()), "type": "incident", **payload.model_dump()}
    with store.lock:
        store.incidents.append(incident)
    return {"ok": True, "incident": incident}


@router.post("/core/near-miss")
def create_near_miss(payload: IncidentRequest):
    near_miss = {"id": str(uuid4()), "type": "near-miss", **payload.model_dump()}
    with store.lock:
        store.incidents.append(near_miss)
    return {"ok": True, "near_miss": near_miss}
