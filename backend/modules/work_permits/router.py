from fastapi import APIRouter
from pydantic import BaseModel, Field
from uuid import uuid4

from backend.services.store import store
from backend.core.errors import AppError

router = APIRouter(prefix="/core/work-permits", tags=["Work Permits"])


class WorkPermitIn(BaseModel):
    title: str
    risk_level: str
    approved_by: str
    status: str
    checklist_items: list[str] = Field(default_factory=list)


class WorkPermit(WorkPermitIn):
    id: str


@router.get("", response_model=list[WorkPermit])
def list_work_permits():
    return store.permits


@router.post("", response_model=WorkPermit)
def create_work_permit(payload: WorkPermitIn):
    permit = {"id": str(uuid4()), **payload.model_dump()}
    with store.lock:
        store.permits.append(permit)
    return permit


@router.put("/{permit_id}", response_model=WorkPermit)
def update_work_permit(permit_id: str, payload: WorkPermitIn):
    with store.lock:
        for idx, permit in enumerate(store.permits):
            if permit["id"] == permit_id:
                updated = {"id": permit_id, **payload.model_dump()}
                store.permits[idx] = updated
                return updated
    raise AppError("Work permit not found", status_code=404)


@router.delete("/{permit_id}")
def delete_work_permit(permit_id: str):
    with store.lock:
        for idx, permit in enumerate(store.permits):
            if permit["id"] == permit_id:
                del store.permits[idx]
                return {"ok": True, "message": "Deleted"}
    raise AppError("Work permit not found", status_code=404)
