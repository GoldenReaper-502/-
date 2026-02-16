from pydantic import BaseModel, Field
from typing import Optional


class WorkPermitBase(BaseModel):
    title: str = Field(..., min_length=2)
    risk_level: str = Field("Medium")
    approved_by: Optional[str] = None
    status: str = Field("draft")
    checklist_items: list[str] = Field(default_factory=list)


class WorkPermitCreate(WorkPermitBase):
    pass


class WorkPermitUpdate(BaseModel):
    title: Optional[str] = None
    risk_level: Optional[str] = None
    approved_by: Optional[str] = None
    status: Optional[str] = None
    checklist_items: Optional[list[str]] = None


class WorkPermitOut(WorkPermitBase):
    id: str
    created_at: str
    updated_at: str
