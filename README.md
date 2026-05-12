# DF-USA-Multi-Tenant-Orchestrator [CRUX-MK]

**Welle-51 USA-Markt-Expansion.** Multi-Tenant-Boundary fuer DE+USA-Hotels mit DSGVO+CCPA-Compliance.

## Stack-Begruendung

- **Tenant-Isolation:** Per-Country (DE/US) + Per-Hotel-ID Boundary
- **Compliance:** DSGVO (EU) + CCPA (California) + Sec-883-Carve-Out-Awareness
- **K_0+Q_0:** Hotel-Daten + Familien-Daten (Cape-Coral-Brueder-Trennung)
- **Sandbox-Default:** ENV-Var-gated Real-Mode + PHRONESIS_TICKET-Pflicht
- **Cross-DF:** Upstream zu `df-usa-cross-border-tax-optimizer`, Downstream zu `df-florida-hotel-acquisition-tracker`

## CRUX-Bindung

- **K_0:** Hotel-Profit + Acquisition-Decisions
- **Q_0:** Familien-Datenschutz Cape-Coral-Relocation
- **I_min:** Per-Country-Boundary strukturiert
- **W_0:** Mock-Default verhindert Production-Risk

[CRUX-MK]
