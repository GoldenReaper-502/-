from fastapi import APIRouter
from pydantic import BaseModel, Field
from uuid import uuid4

from backend.services.store import store

router = APIRouter(prefix="/core/checklists", tags=["Checklists"])


class ChecklistIn(BaseModel):
    equipment: str
    camera_id: str
    items: list[str] = Field(default_factory=list)
    status: str = "Pending"


class Checklist(ChecklistIn):
    id: str


@router.get("", response_model=list[Checklist])
def list_checklists():
    return store.checklists


@router.post("", response_model=Checklist)
def create_checklist(payload: ChecklistIn):
    checklist = {"id": str(uuid4()), **payload.model_dump()}
    with store.lock:
        store.checklists.append(checklist)
    return checklist
