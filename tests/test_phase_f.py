"""Tests for Phase F: validation, security, DR, release gates."""

import os
import tempfile
import pytest

from validation import run_standard_checks, ValidationReport, reconcile_ecl
from security import sanitize_identifier, mask_secret, sha256_hex
from dr import backup_file, write_manifest
from governance import ReleaseGateStatus, can_mark_official, RELEASE_GATES


def test_validation_ok():
    rows = [{"account_id": "A1", "outstanding": 100.0, "dpd": 0, "origination_date": "2024-01-01", "maturity_date": "2025-01-01"}]
    rep = run_standard_checks(rows, 100.0)
    assert rep.ok


def test_validation_control_total_fail():
    rows = [{"account_id": "A1", "outstanding": 100.0, "dpd": 0}]
    rep = run_standard_checks(rows, 200.0)
    assert not rep.ok


def test_reconcile():
    assert reconcile_ecl(100.0, 100.0).passed is True
    assert reconcile_ecl(100.0, 110.0).passed is False


def test_security():
    assert sanitize_identifier("loan_master") == "loan_master"
    with pytest.raises(ValueError):
        sanitize_identifier("loan;drop")
    assert mask_secret("secret1234", 4) == "secr******"
    assert sha256_hex("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_dr_backup():
    d = tempfile.mkdtemp()
    src = os.path.join(d, "data.txt")
    with open(src, "w") as f:
        f.write("hello")
    bdir = os.path.join(d, "backup")
    dst = backup_file(src, bdir)
    assert os.path.exists(dst)
    mf = os.path.join(d, "manifest.json")
    write_manifest(mf, {"ok": True})
    assert os.path.exists(mf)


def test_release_gates():
    st = ReleaseGateStatus()
    assert st.label() == "PRELIMINARY"
    assert not can_mark_official(st)
    for g in RELEASE_GATES:
        st.set(g, True)
    assert st.all_passed
    assert st.label() == "OFFICIAL"
    assert can_mark_official(st)
    assert st.missing == []
