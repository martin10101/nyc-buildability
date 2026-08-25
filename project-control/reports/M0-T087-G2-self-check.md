# M0-T087 — G2 producer self-check

Producer: orchestrator. Date: 2026-08-25. Reviewed identity = the task checkpoint commit
(allowed_paths manifest: `tools/agent_supervisor` [adds campaign_continuity.py only],
`tools/test_agent_supervisor_bootstrap_continuity.py`,
`project-control/reports/M0-T087-bootstrap-continuity.md`).

## Deliverables vs objective
- Durable campaign-continuity slice: fail-closed record schema + validation, atomic LF writes,
  exact-once sequence-guarded advance, staleness detection, read-only `--status` entry point.
  No existing supervisor module modified (additive slice; cli/hook integration deferred to owning
  phases). Reuse decision documented: `session_continuity.py` solves provider-session resume, a
  different boundary — no duplicate machinery built.
- Live campaign record `project-control/campaigns/D-024-fable-codex-loop.json` (control-plane act):
  authority + digest, lineage base, 5 standing restrictions, exact next action, frozen identity.
- **E2E proof executed**: fresh isolated context, campaign-ignorant prompt, oriented from durable
  artifacts alone → correct campaign/authority/next-action (incl. "already claimed — don't
  re-claim" discrepancy resolved in the ledger's favor per the repo's precedence rule), frozen
  identity verified == live HEAD == origin, all restrictions enumerated, READY TO RESUME.
- Acceptance pack AS-1..AS-6 in the task record.

## Verification runs (exact outcomes)
- `pytest tools/test_agent_supervisor_bootstrap_continuity.py -q` → **35 passed** (0.34s).
- Full supervisor suite (freeze §4 duty) → **1905 passed, 2 skipped, 0 failed** (233s)
  (= prior 1870 baseline + 35 new; ≥1165/0 re-established with margin).
- `ruff check` both files → clean (2 unused imports auto-fixed pre-commit).
- Live `--status` run prints full orientation; exit 0.
- No worker-facing quota language in any deliverable (R045); no new dependency (stdlib only).
- Pyright: one narrowing fix applied (`validate(data: object)` so the runtime type guard is real).

## Known limitations (disclosed in the producer report)
- Live cross-terminal turnover + §16.9 golden-run crossing owed by M0-T092/M0-T096 (rows bind them).
- `--status` is root-relative by design (Gate 0 guarantees the context).

Result: PASS — ready for independent G3/G4/G5 + DCV at the frozen checkpoint identity.
Supervisor-freeze qualifying evidence: **D-024-R099** (cited here, in the packet, and in the commit).
