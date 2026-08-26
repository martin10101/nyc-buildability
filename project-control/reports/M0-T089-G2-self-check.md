# M0-T089 — G2 producer self-check (orchestrator; not an independent gate)

Date: 2026-08-25. Task: D-024 B2 subagent telemetry breadth + read-only shadow status + carried
M0-T088 bundle. Full producer narrative: `M0-T089-subagent-telemetry.md`. Evidence map:
`M0-T089-evidence-map.json` (34 applicable ids, identical set to M0-T088).

## Executed checks (this checkout, Python 3.11.9)

1. Targeted packs: `python -m pytest tools/test_agent_supervisor_subagent_telemetry.py
   tools/test_agent_supervisor_telemetry_core.py tools/test_agent_supervisor_capability_probe.py -q`
   → **102 passed** (37 new B2 + 49 B1 with carried-fix assertion updates + 16 probe unmodified).
2. Full supervisor suite: `python -m pytest tools/test_agent_supervisor_*.py -q` →
   **2006 passed, 2 skipped, 0 failed (186.55s)** = M0-T088 baseline 1969/2/0 + 37 new
   (supervisor-freeze §4 suite-baseline duty re-established).
3. `ruff check` (0.13.0, CI-matched) on all five new modules + the three carried-fix modules +
   both test files → "All checks passed!".
4. `python tools/modularity_check.py --check` → failures 0; no new module near thresholds; no
   pre-existing file crossed a threshold.
5. Injection/quota greps: quota-language grep over all five B2 modules → zero hits; AST
   no-injection test green over all five B2 modules (and B1's remains green).
6. Scope: `git status` shows exactly the declared outputs + orchestrator control-plane records;
   no forbidden path; no dependency manifest; stdlib-only; `cli.py` and every supervisor
   control-flow module untouched.
7. Live-workstation provenance: transcript parser shapes (assistant `message.id`+`usage`;
   `compact_boundary` `compactMetadata.preTokens/postTokens/cumulativeDroppedTokens/trigger`)
   probed keys-only against real installed-2.1.220 transcripts BEFORE implementation; the
   compact-boundary key set observed live matches the parser exactly.

## Known limitations (honest)

- subagentStatusLine payloads are docs-derived fixtures (matrix `claude.subagentStatusLine`,
  official-docs confidence); live interactive payload fixtures remain a Phase B/F harness
  deliverable (`hooks.live_behavior_fixtures` unchanged at `unknown`).
- SDK path is fixture-only while the SDK is absent-by-policy; live SDK ingestion activates only
  after an owner-authorized dependency admission (R040) — by design, not a gap.
- `tokenSamples` semantics deliberately uninterpreted (trend-only attribute) pending live
  fixtures — the directive forbids inventing an undocumented interpretation.
- No live wiring into Claude Code settings (status-line/hook installation is operator/Phase F
  surface); actuation and consumers stay OFF (Phase C+).

Result: **PASS (self-check)** — ready for independent G3/G4/G5 + DCV at the frozen identity.
