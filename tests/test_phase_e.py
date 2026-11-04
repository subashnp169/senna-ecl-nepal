"""Tests for Phase E: tenants, connectors, auth."""

import sqlite3
import tempfile
import os
import pytest

from tenants.models import Tenant, User, AuditLog, check_access, Permission
from connectors.sftp_batch.connector import validate_manifest, load_manifest, BatchManifest
from connectors.sql_views.connector import SQLViewConnector, SQLViewConfig
from apps.api.app.app.auth import create_token, verify_token


def test_rbac():
    u = User("u1", "t1", "a@b.com", "viewer")
    assert check_access(u, Permission.READ) is True
    assert check_access(u, Permission.WRITE) is False
    admin = User("u2", "t1", "b@b.com", "admin")
    assert check_access(admin, Permission.ADMIN) is True


def test_audit_log():
    log = AuditLog()
    log.record("t1", "u1", "login", "session")
    assert len(log.for_tenant("t1")) == 1
    assert len(log.for_user("u1")) == 1


def test_sftp_manifest():
    m = {"batch_id": "b1", "institution_id": "i1", "as_of_date": "2025-06-30", "files": ["a.csv"]}
    assert validate_manifest(m) == []
    d = tempfile.mkdtemp()
    path = os.path.join(d, "m.json")
    import json
    with open(path, "w") as f:
        json.dump(m, f)
    bm = load_manifest(path)
    assert bm.batch_id == "b1"


def test_sftp_manifest_invalid():
    assert validate_manifest({})  # errors


def test_sql_view_connector():
    d = tempfile.mkdtemp()
    db = os.path.join(d, "t.db")
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE v (as_of_date TEXT, val INTEGER)")
    conn.execute("INSERT INTO v VALUES ('2025-06-30', 42)")
    conn.commit()
    conn.close()
    cfg = SQLViewConfig(connection_string=db, view_name="v")
    c = SQLViewConnector(cfg)
    rows = c.fetch("2025-06-30")
    assert rows == [{"as_of_date": "2025-06-30", "val": 42}]


def test_auth_token():
    tok = create_token("u1", "t1", "admin")
    payload = verify_token(tok)
    assert payload is not None
    assert payload["sub"] == "u1"
    assert payload["tenant"] == "t1"
    assert verify_token(tok + "x") is None
    assert verify_token("garbage") is None
