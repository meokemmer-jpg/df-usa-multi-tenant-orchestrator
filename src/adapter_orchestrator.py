"""Adapter-Orchestrator (LaunchAgent-Entry) [CRUX-MK]."""

from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorResult:
    tenants_active: int
    tenants_de: int
    tenants_us: int
    sandbox_mode: bool
    audit_hash: str


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO)
    if Path("/tmp/df-usa-multi-tenant-orchestrator.stop").exists():
        logger.info("STOP.flag detected, exiting cleanly")
        return 0

    from .usa_multi_tenant_orchestrator_main import (
        MultiTenantOrchestrator, Country
    )
    from .audit_logger import AuditLogger

    orch = MultiTenantOrchestrator()
    audit = AuditLogger()

    # Sandbox-Demo-Daten
    orch.register_tenant("HILDESHEIM-PILOT-01", Country.DE, "Hey Lou Hildesheim",
                          "2026-04-01", dual_compliance=False)
    orch.register_tenant("CAPE-CORAL-PILOT-01", Country.US, "Hey Lou Cape Coral",
                          "2026-05-12", dual_compliance=False)

    de = orch.list_tenants_by_country(Country.DE)
    us = orch.list_tenants_by_country(Country.US)

    audit_hash = audit.append({
        "type": "multi_tenant_orchestration_run",
        "tenants_active": len(de) + len(us),
        "tenants_de": len(de),
        "tenants_us": len(us),
        "sandbox_mode": orch.sandbox_mode,
    })

    result = OrchestratorResult(
        tenants_active=len(de) + len(us),
        tenants_de=len(de),
        tenants_us=len(us),
        sandbox_mode=orch.sandbox_mode,
        audit_hash=audit_hash,
    )
    logger.info(f"USA-Multi-Tenant-Orchestrator: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
