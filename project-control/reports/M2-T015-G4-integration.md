# M2-T015 — G4 integration & regression gate

Recorded by the orchestrator (integration owner) 2026-08-09 at main `1b3af35`. Evidence: the authoritative
CI run on the integration (PR #213), captured verbatim in `project-control/reports/M2-T015-CI-evidence.md`.

- **Full build/lint/type-check/test suite:** api CI job (Python 3.12) SUCCESS — `ruff check .` All checks
  passed; `pytest -q` **2025 passed** (documents subset 939 / 1 skipped). web (lint + typecheck + build)
  SUCCESS; web-e2e SUCCESS.
- **Contract compatibility:** contracts + contracts-schema-bundle + contracts-typegen SUCCESS (byte-identical
  drift checks); `validate_contracts.py` exit 0.
- **Control-plane regression:** control-plane (ADR-005 workflow regression) SUCCESS.
- **Production install path:** exact-production-install (Render pip + validate_profile + pip-audit) SUCCESS.
- **No duplicate/contradictory implementation:** the documents module is net-new (additive; earlier units
  reviewed); the fixture pack + matrix are additive; no pipeline logic changed in the rework.
- **Low-storage / temp-file:** synthetic fixtures are small committed bytes (sha256-pinned, binary-marked);
  no large/persistent local artifacts.
- **Required checks green:** all 8 required contexts SUCCESS. The only red is the NON-required
  `web-dependency-security` (nanoid age-gate, eligible 2026-08-10; Tier-A-unaffected; M0-T047 precedent).

**G4 verdict: PASS** — integration is green on both events; regression suite intact; no duplicate implementations.

---

## G4 independent attestation — code-reviewer (read-only) at `1b3af35`: VERDICT PASS

Independent reviewer (≠ producer). Isolated PR #213's actual contribution via merge first-parent diff
`git diff 1b3af35^1 1b3af35` (parents `b9b5bd8` prior-main, `408513b` PR head): **91 files, +20024 / −2, all
additive, all inside M2-T015 allowed_paths.** The `tools/agent_supervisor/*` + `.claude/*` churn in the raw
`897e7df..1b3af35` range is from the OTHER merge parent, NOT PR #213. No shared consumer/wiring modified
(no `app/main.py`, router, `connectors/**`, `profile/**`) — self-contained, not yet consumed (UI = Packet C),
structurally cannot regress runtime. Only shared-tooling edit is the additive `generate_ts_types.py` typegen
extension (M2-T010-permitted, drift-clean). CI green (api 3.12: ruff clean + 2025 passed; web; web-e2e;
contracts trio; control-plane; exact-production-install); ruff exit 0 reproduced locally. No duplicate
implementation; regression suite intact (925→939 documents, purely additive fixture-pack tests). Only red is
the non-required `web-dependency-security` (nanoid age-gate). **G4 verdict: PASS at `1b3af35`.**
