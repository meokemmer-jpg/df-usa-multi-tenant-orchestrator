"""Tests fuer DF-USA-Multi-Tenant-Orchestrator [CRUX-MK]. 10 Tests (6 main + 4 orchestrator)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.usa_multi_tenant_orchestrator_main import (
    MultiTenantOrchestrator,
    Country,
    ComplianceRegime,
    TenantBoundaryError,
)
from src.audit_logger import AuditLogger
from src.adapter_orchestrator import main as orchestrator_main


# ============== Main: 6 Tests ==============

def test_register_de_tenant_yields_dsgvo():
    """Test 1: DE-Tenant bekommt DSGVO-Regime."""
    o = MultiTenantOrchestrator(sandbox_mode=True)
    reg = o.register_tenant("H1", Country.DE, "Hey Lou Berlin", "2026-04-01")
    assert reg.compliance_regime == ComplianceRegime.DSGVO
    assert reg.active is True


def test_register_us_tenant_yields_ccpa():
    """Test 2: US-Tenant bekommt CCPA-Regime."""
    o = MultiTenantOrchestrator(sandbox_mode=True)
    reg = o.register_tenant("H2", Country.US, "Hey Lou Cape Coral", "2026-05-12")
    assert reg.compliance_regime == ComplianceRegime.CCPA


def test_dual_compliance_regime():
    """Test 3: dual_compliance=True → DUAL-Regime."""
    o = MultiTenantOrchestrator(sandbox_mode=True)
    reg = o.register_tenant("H3", Country.US, "Hey Lou Miami", "2026-06-01",
                             dual_compliance=True)
    assert reg.compliance_regime == ComplianceRegime.DUAL


def test_cross_tenant_boundary_raises():
    """Test 4: Cross-Tenant-Read raises TenantBoundaryError."""
    o = MultiTenantOrchestrator(sandbox_mode=True)
    o.register_tenant("H1", Country.DE, "X", "2026-04-01")
    o.register_tenant("H2", Country.US, "Y", "2026-04-01")
    with pytest.raises(TenantBoundaryError):
        o.check_boundary("H1", "H2")


def test_list_tenants_by_country_filters():
    """Test 5: list_tenants_by_country liefert nur Country-Match."""
    o = MultiTenantOrchestrator(sandbox_mode=True)
    o.register_tenant("H1", Country.DE, "X", "2026-04-01")
    o.register_tenant("H2", Country.DE, "Y", "2026-04-01")
    o.register_tenant("H3", Country.US, "Z", "2026-04-01")
    de = o.list_tenants_by_country(Country.DE)
    us = o.list_tenants_by_country(Country.US)
    assert len(de) == 2
    assert len(us) == 1


def test_duplicate_registration_raises():
    """Test 6: Duplicate tenant_id raises."""
    o = MultiTenantOrchestrator(sandbox_mode=True)
    o.register_tenant("H1", Country.DE, "X", "2026-04-01")
    with pytest.raises(ValueError):
        o.register_tenant("H1", Country.US, "X-Dup", "2026-04-02")


# ============== Orchestrator: 4 Tests ==============

def test_audit_chain_valid(tmp_path):
    """Test 7: Audit-Chain valid."""
    a = AuditLogger(audit_path=tmp_path / "a.jsonl", secret="s")
    a.append({"e": "1"})
    a.append({"e": "2"})
    assert a.verify_chain()["valid"] is True


def test_audit_hash_chain_continuity(tmp_path):
    """Test 8: Hash-Chain prev_hash-Continuity."""
    a = AuditLogger(audit_path=tmp_path / "b.jsonl", secret="s")
    h1 = a.append({"x": 1})
    h2 = a.append({"x": 2})
    assert h1 != h2
    res = a.verify_chain()
    assert res["entries_verified"] == 2


def test_sandbox_default_via_env(monkeypatch):
    """Test 9: ENV-Var DF_USA_MULTI_TENANT_REAL_ENABLED=false → sandbox."""
    monkeypatch.delenv("DF_USA_MULTI_TENANT_REAL_ENABLED", raising=False)
    o = MultiTenantOrchestrator()
    assert o.sandbox_mode is True


def test_orchestrator_main_exits_zero(monkeypatch, tmp_path):
    """Test 10: orchestrator_main() liefert exit-code 0."""
    monkeypatch.setenv("HOME", str(tmp_path))
    rc = orchestrator_main([])
    assert rc == 0
