from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["core-compat"])


class DetectRequest(BaseModel):
    source: str = "camera"
    payload: dict = Field(default_factory=dict)


class ChatRequest(BaseModel):
    message: str


class IncidentRequest(BaseModel):
    title: str
    location: str
    severity: str = "medium"


@router.get("/core/system/status")
def system_status():
    return {"healthy": True, "status": "ok", "message": "Core API operational"}


@router.post("/core/detect")
def detect_objects(payload: DetectRequest):
    return {
        "ok": True,
        "detections": [
            {
                "id": str(uuid4()),
                "source": payload.source,
                "payload": payload.payload,
                "message": "Detection analyzed",
            }
        ],
    }


@router.post("/core/chat")
def chat(payload: ChatRequest):
    return {"ok": True, "reply": f"Received: {payload.message}"}


@router.post("/core/incident")
def create_incident(payload: IncidentRequest):
    return {"ok": True, "incident": {"id": str(uuid4()), **payload.model_dump()}}


@router.post("/core/near-miss")
def create_near_miss(payload: IncidentRequest):
    return {"ok": True, "near_miss": {"id": str(uuid4()), **payload.model_dump()}}
