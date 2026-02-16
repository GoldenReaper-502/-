from datetime import datetime, timezone
import json
from uuid import uuid4

from fastapi import APIRouter

from backend.core.errors import AppError
from backend.models.permits import WorkPermitCreate, WorkPermitOut, WorkPermitUpdate
from backend.storage.db import get_conn

router = APIRouter(tags=["work-permits"])


def now_iso():
    return datetime.now(timezone.utc).isoformat()


@router.get("/core/work-permits", response_model=list[WorkPermitOut])
def list_permits():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM work_permits ORDER BY updated_at DESC").fetchall()

    return [
        WorkPermitOut(
            id=r["id"],
            title=r["title"],
            risk_level=r["risk_level"],
            approved_by=r["approved_by"],
            status=r["status"],
            checklist_items=json.loads(r["checklist_items"]),
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )
        for r in rows
    ]


@router.post("/core/work-permits", response_model=WorkPermitOut)
def create_permit(payload: WorkPermitCreate):
    pid = str(uuid4())
    ts = now_iso()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO work_permits VALUES (?,?,?,?,?,?,?,?)",
            (
                pid,
                payload.title,
                payload.risk_level,
                payload.approved_by,
                payload.status,
                json.dumps(payload.checklist_items),
                ts,
                ts,
            ),
        )
        conn.commit()
    return WorkPermitOut(id=pid, created_at=ts, updated_at=ts, **payload.model_dump())


@router.put("/core/work-permits/{permit_id}", response_model=WorkPermitOut)
def update_permit(permit_id: str, payload: WorkPermitUpdate):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM work_permits WHERE id=?", (permit_id,)).fetchone()
        if not row:
            raise AppError("Permit not found", 404)

        data = dict(row)
        ts = now_iso()

        if payload.title is not None:
            data["title"] = payload.title
        if payload.risk_level is not None:
            data["risk_level"] = payload.risk_level
        if payload.approved_by is not None:
            data["approved_by"] = payload.approved_by
        if payload.status is not None:
            data["status"] = payload.status
        if payload.checklist_items is not None:
            data["checklist_items"] = json.dumps(payload.checklist_items)

        conn.execute(
            """
            UPDATE work_permits
            SET title=?, risk_level=?, approved_by=?, status=?, checklist_items=?, updated_at=?
            WHERE id=?
            """,
            (
                data["title"],
                data["risk_level"],
                data["approved_by"],
                data["status"],
                data["checklist_items"],
                ts,
                permit_id,
            ),
        )
        conn.commit()

    return WorkPermitOut(
        id=data["id"],
        title=data["title"],
        risk_level=data["risk_level"],
        approved_by=data["approved_by"],
        status=data["status"],
        checklist_items=json.loads(data["checklist_items"]),
        created_at=data["created_at"],
        updated_at=ts,
    )


@router.delete("/core/work-permits/{permit_id}")
def delete_permit(permit_id: str):
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM work_permits WHERE id=?", (permit_id,)).fetchone()
        if not row:
            raise AppError("Permit not found", 404)
        conn.execute("DELETE FROM work_permits WHERE id=?", (permit_id,))
        conn.commit()
    return {"ok": True, "deleted_id": permit_id}
