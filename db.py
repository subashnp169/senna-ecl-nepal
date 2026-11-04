"""SQLite persistence for runs, snapshots, reports."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from config import DB_PATH


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS runs (
        run_id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        as_of_date TEXT NOT NULL,
        institution_id TEXT NOT NULL,
        source_file TEXT,
        status TEXT NOT NULL,
        loan_count INTEGER,
        total_ead REAL,
        total_ecl REAL,
        coverage REAL,
        snapshot_checksum TEXT,
        error TEXT,
        created_at TEXT NOT NULL,
        finished_at TEXT
    );
    CREATE TABLE IF NOT EXISTS run_artifacts (
        run_id TEXT NOT NULL,
        kind TEXT NOT NULL,
        path TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(run_id) REFERENCES runs(run_id)
    );
    """)
    conn.commit()
    conn.close()


def create_run(run_id, tenant_id, as_of_date, institution_id, source_file) -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO runs (run_id,tenant_id,as_of_date,institution_id,source_file,status,created_at) VALUES (?,?,?,?,?,?,?)",
        (run_id, tenant_id, as_of_date, institution_id, source_file, "running", datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def finish_run(run_id, status, loan_count=0, total_ead=0.0, total_ecl=0.0, coverage=0.0, checksum="", error="") -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE runs SET status=?,loan_count=?,total_ead=?,total_ecl=?,coverage=?,snapshot_checksum=?,error=?,finished_at=? WHERE run_id=?",
        (status, loan_count, total_ead, total_ecl, coverage, checksum, error, datetime.now().isoformat(), run_id),
    )
    conn.commit()
    conn.close()


def add_artifact(run_id, kind, path) -> None:
    conn = get_conn()
    conn.execute("INSERT INTO run_artifacts (run_id,kind,path,created_at) VALUES (?,?,?,?)",
                 (run_id, kind, path, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def list_runs(limit: int = 50):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


init_db()
