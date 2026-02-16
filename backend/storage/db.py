import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "hazm.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS work_permits (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            approved_by TEXT,
            status TEXT NOT NULL,
            checklist_items TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
        )
        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS checklists (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            equipment_type TEXT,
            camera_id TEXT,
            items TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
        )
        conn.commit()
