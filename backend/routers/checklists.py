from datetime import datetime, timezone
import json
from uuid import uuid4

from fastapi import APIRouter

from backend.core.errors import AppError
from backend.models.checklists import ChecklistCreate, ChecklistOut
from backend.storage.db import get_conn

router = APIRouter(tags=["checklists"])


def now_iso():
    return datetime.now(timezone.utc).isoformat()


@router.get("/core/checklists", response_model=list[ChecklistOut])
def list_checklists():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM checklists ORDER BY updated_at DESC").fetchall()
    return [
        ChecklistOut(
            id=r["id"],
            name=r["name"],
            equipment_type=r["equipment_type"],
            camera_id=r["camera_id"],
            items=json.loads(r["items"]),
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )
        for r in rows
    ]


@router.post("/core/checklists", response_model=ChecklistOut)
def create_checklist(payload: ChecklistCreate):
    cid = str(uuid4())
    ts = now_iso()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO checklists VALUES (?,?,?,?,?,?,?)",
            (cid, payload.name, payload.equipment_type, payload.camera_id, json.dumps(payload.items), ts, ts),
        )
        conn.commit()
    return ChecklistOut(id=cid, created_at=ts, updated_at=ts, **payload.model_dump())


@router.delete("/core/checklists/{checklist_id}")
def delete_checklist(checklist_id: str):
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM checklists WHERE id=?", (checklist_id,)).fetchone()
        if not row:
            raise AppError("Checklist not found", 404)
        conn.execute("DELETE FROM checklists WHERE id=?", (checklist_id,))
        conn.commit()
    return {"ok": True, "deleted_id": checklist_id}
