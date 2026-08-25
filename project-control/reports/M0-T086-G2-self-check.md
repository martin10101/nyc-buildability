# M0-T086 — G2 producer self-check

Producer: orchestrator. Date: 2026-08-25. Reviewed identity = the task checkpoint commit
(allowed_paths manifest: fixtures dir, capability_probe.py, its test, supervisor-freeze rule,
two M0-T086 reports).

## Deliverables vs objective
- Live-workstation reconciliation: `M0-T086-capability-baseline.md` §1 (worktrees, 156 branches
  with explained divergences, dirty primary checkout untouched, PR #241 hold, MCP state).
- Component map + reuse register: `M0-T086-reuse-register.md` (58 modules → REUSE/EXTEND/GAP per
  phase; host-restart autostart machinery discovered as REUSE for Phase D).
- Capability probes as deterministic fixtures: `capability_probe_live_2026-08-25.json` (live,
  deterministic body — two runs byte-identical) + `capability_matrix_v1.json` (20 entries;
  measured-live / official-docs / session-evidence / policy confidence labels; explicit unknowns).
- Probe tooling: `tools/agent_supervisor/capability_probe.py` (read-only allowlist; failures →
  unknown; PATHEXT-resolution fix for npm shims) + `tools/test_agent_supervisor_capability_probe.py`.
- Freeze amendment: `.claude/rules/supervisor-freeze.md` D-024 recognition block (authorized by
  D-024 §1; nothing else changed).
- Acceptance pack AS-1..AS-6 in the task record.

## Verification runs (exact outcomes)
- `python -m pytest tools/test_agent_supervisor_capability_probe.py -q` → **16 passed** (6.4s).
- `python -m pytest tools/test_agent_supervisor_*.py -q` (freeze §4 suite baseline) →
  **1870 passed, 2 skipped, 0 failed** (328s). Baseline ≥1165/0 re-established with margin.
- `python -m ruff check` on both new files → clean.
- `python tools/validate_directive_compliance.py --check` → EXIT=0.
- Determinism: two consecutive `build_record()` bodies identical (test + manual run).
- No-quota grep: `grep -iE "token (quota|limit|budget)|countdown|conserve tokens"` over the new
  probe/test/fixture files → no matches (R045).
- No control-behavior change: commit diff limited to fixtures/probe/test/rule/reports/ledger
  records (AS-6); no supervisor control-flow module, graph file, or hook changed.

## Known limitations (disclosed)
- Interactive behaviors (prompt-erasure semantics, live payload shapes) are `unknown` in the
  probe body by design — documented from official docs in the matrix; live harness = Phase B/F.
- `--init-only` classified `not-detected-in-help` (weaker than unsupported; help text may omit).
- Docs facts fetched 2026-08-25 describe current published docs; installed-behavior fixtures
  remain the authority wherever the two ever disagree (none found for probed items).

Result: PASS — ready for independent G3/G4/G5 + DCV at the frozen checkpoint identity.
Supervisor-freeze qualifying evidence: **D-024-R099** (cited here, in the task packet, and in the
commit message).
