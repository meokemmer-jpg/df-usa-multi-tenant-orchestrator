"""USA Multi-Tenant Orchestrator Core [CRUX-MK].

Multi-Tenant-Boundary fuer DE+USA-Hotels mit DSGVO+CCPA-Compliance.
Mock-Default. ENV-Var-gated Real-Mode via DF_USA_MULTI_TENANT_REAL_ENABLED.

[CRUX-MK]
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Country(str, Enum):
    DE = "DE"
    US = "US"


class ComplianceRegime(str, Enum):
    DSGVO = "dsgvo"      # EU
    CCPA = "ccpa"        # California
    DUAL = "dual"        # DE+US Hotel
    NONE = "none"


@dataclass(frozen=True)
class TenantContext:
    """Immutable Tenant-Context. Country + Hotel-ID + Compliance."""
    tenant_id: str
    country: Country
    compliance_regime: ComplianceRegime
    sandbox_mode: bool = True


@dataclass
class TenantRegistration:
    tenant_id: str
    country: Country
    hotel_name: str
    compliance_regime: ComplianceRegime
    registered_at_iso: str
    active: bool = True


class TenantBoundaryError(Exception):
    """Raised wenn Cross-Tenant-Read versucht wird."""


class MultiTenantOrchestrator:
    """Provisioning + Boundary-Check fuer DE+US Hotels."""

    def __init__(self, sandbox_mode: Optional[bool] = None):
        if sandbox_mode is None:
            sandbox_mode = (
                os.environ.get("DF_USA_MULTI_TENANT_REAL_ENABLED", "false").lower() != "true"
            )
        self.sandbox_mode = sandbox_mode
        self._tenants: dict[str, TenantRegistration] = {}

    def _derive_regime(self, country: Country, dual: bool) -> ComplianceRegime:
        if dual:
            return ComplianceRegime.DUAL
        if country == Country.DE:
            return ComplianceRegime.DSGVO
        if country == Country.US:
            return ComplianceRegime.CCPA
        return ComplianceRegime.NONE

    def register_tenant(
        self,
        tenant_id: str,
        country: Country,
        hotel_name: str,
        registered_at_iso: str,
        dual_compliance: bool = False,
    ) -> TenantRegistration:
        if not tenant_id or not hotel_name:
            raise ValueError("tenant_id + hotel_name required")
        if tenant_id in self._tenants:
            raise ValueError(f"Tenant already registered: {tenant_id}")
        reg = TenantRegistration(
            tenant_id=tenant_id,
            country=country,
            hotel_name=hotel_name,
            compliance_regime=self._derive_regime(country, dual_compliance),
            registered_at_iso=registered_at_iso,
        )
        self._tenants[tenant_id] = reg
        return reg

    def get_context(self, tenant_id: str) -> TenantContext:
        if tenant_id not in self._tenants:
            raise KeyError(f"Tenant not found: {tenant_id}")
        reg = self._tenants[tenant_id]
        return TenantContext(
            tenant_id=reg.tenant_id,
            country=reg.country,
            compliance_regime=reg.compliance_regime,
            sandbox_mode=self.sandbox_mode,
        )

    def check_boundary(self, requesting_tenant: str, target_tenant: str) -> bool:
        """Boundary-Check: NUR same-tenant erlaubt."""
        if requesting_tenant != target_tenant:
            raise TenantBoundaryError(
                f"Cross-Tenant-Read: {requesting_tenant} -> {target_tenant}"
            )
        return True

    def list_tenants_by_country(self, country: Country) -> list[TenantRegistration]:
        return [t for t in self._tenants.values() if t.country == country and t.active]

    def deactivate(self, tenant_id: str) -> None:
        if tenant_id not in self._tenants:
            raise KeyError(f"Tenant not found: {tenant_id}")
        self._tenants[tenant_id] = TenantRegistration(
            tenant_id=self._tenants[tenant_id].tenant_id,
            country=self._tenants[tenant_id].country,
            hotel_name=self._tenants[tenant_id].hotel_name,
            compliance_regime=self._tenants[tenant_id].compliance_regime,
            registered_at_iso=self._tenants[tenant_id].registered_at_iso,
            active=False,
        )
