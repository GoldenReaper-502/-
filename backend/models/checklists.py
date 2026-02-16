from pydantic import BaseModel, Field
from typing import Optional


class ChecklistBase(BaseModel):
    name: str = Field(..., min_length=2)
    equipment_type: Optional[str] = None
    camera_id: Optional[str] = None
    items: list[str] = Field(default_factory=list)


class ChecklistCreate(ChecklistBase):
    pass


class ChecklistOut(ChecklistBase):
    id: str
    created_at: str
    updated_at: str
