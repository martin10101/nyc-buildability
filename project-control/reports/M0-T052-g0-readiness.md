# M0-T052 — G0 readiness (administrative)

Recorded by the orchestrator 2026-08-08, at main `de2e647`.

- **Qualifying evidence (supervisor-freeze §2/§3):** B-018 — reproduced stranded-START_CLAUDE
  crash window from the first live supervised run; cited verbatim in the task objective and
  required in the fix commit message. Owner order: D-010 source-024 (R237–R241; capture on
  PR #191 with the M0-T052 applicability restamp).
- **Root cause (narrow, verified read-only):** `CYCLE_ENTRY_STATES` (loop.py:118) omits
  `START_CLAUDE`; a kill between the `preflight_pass → START_CLAUDE` journal commit and the
  child launch strands the journal; `recover_boot` records SAFE_CHECKPOINT but transitions
  nothing; no production driver fires the S7 exits. Loop already: skips the duplicate
  preflight transition (`entry == PREFLIGHT` guard, loop.py:1606), transitions
  `START_CLAUDE → CLAUDE_RUNNING` on real process start (loop.py:1637), and dispatch stays
  gated by operator `start` + SAFE_CHECKPOINT classification + single-instance lock + child
  accounting + Job-Object kill-on-close.
- **Scope:** `tools/agent_supervisor/loop.py` (entry-state set) + supervisor tests only.
  Disjoint from M2-T015's scope (services/api, docs, contracts) — R241 honored; the running
  supervised unit is never interrupted (a merged fix takes effect at the next `start`).
- **Tests demanded by the packet:** crash-window regression (dispatch-once from a stranded
  START_CLAUDE journal with a fake executable), fail-closed negative (non-SAFE recovery still
  refuses), full-suite freeze-baseline re-establishment (M0-T039; 0 failures).
- **Gates:** G0 (this), G2, G3 + G5 (freeze §4 standard gates; tree-hash change expected and
  re-baselined), DCV rows R237/R239/R240/R241 at accept.
- **Holds honored:** no redesign (R240); M0-T047 age gate untouched; limited-auto untouched.

READY.
