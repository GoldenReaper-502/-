from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Any
from uuid import uuid4


@dataclass
class InMemoryStore:
    permits: list[dict[str, Any]] = field(default_factory=list)
    checklists: list[dict[str, Any]] = field(default_factory=list)
    alerts: list[dict[str, Any]] = field(default_factory=list)
    incidents: list[dict[str, Any]] = field(default_factory=list)
    lock: Lock = field(default_factory=Lock)

    def seed(self) -> None:
        if self.permits:
            return
        with self.lock:
            self.permits.extend(
                [
                    {
                        "id": str(uuid4()),
                        "title": "Hot Work Permit - Area A",
                        "risk_level": "High",
                        "approved_by": "HSE Manager",
                        "status": "Active",
                        "checklist_items": ["Fire extinguisher", "Gas test", "PPE verified"],
                    },
                    {
                        "id": str(uuid4()),
                        "title": "Confined Space Entry",
                        "risk_level": "Medium",
                        "approved_by": "Site Supervisor",
                        "status": "Pending",
                        "checklist_items": ["Ventilation", "Rescue plan"],
                    },
                ]
            )
            self.checklists.extend(
                [
                    {
                        "id": str(uuid4()),
                        "equipment": "Excavator",
                        "camera_id": "CAM-01",
                        "items": ["Hydraulics OK", "Alarm working", "Brakes tested"],
                        "status": "Ready",
                    }
                ]
            )


store = InMemoryStore()
store.seed()
