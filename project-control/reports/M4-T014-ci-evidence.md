# M4-T014 CI evidence capture (orchestrator; reviewers verify this stored artifact)

**Executable authority run:** CI run **34740497612** on head **`6fc8a878`**, branch
`candidate/D-024-mrl-option-b`. Conclusion **success — 18/18 jobs green** (zero non-success),
captured 2026-09-13 ~07:45 UTC via `gh run view 34740497612`. The `api (ruff + pytest)` job is the
executable authority for the rules suite.

**Material identity:** the M4-T014 material landed at `c8d94f38`; the commits between it and the
run head (`7226db90`, `a085454b`, `0f71681b`, `6fc8a878`) are control-plane records and
`docs/ARCHITECT_REVIEW_QUESTIONS.md` edits only — `git diff c8d94f38..6fc8a878 -- services/api
docs/research/zr-snapshots` is EMPTY, so the run covers the exact frozen M4-T014 source state.

**Run lineage:** the runs on `c8d94f38` (34740092267) and `0f71681b` (34740265570-era CI) were
CANCELLED by the peer session's shared-checkout pushes (branch cancel-in-progress; the peer was
appending owner ZR research to the questions doc). The surviving run on `6fc8a878` is complete
and fully green; no run on this material ever FAILED.

**Orchestrator local reproduction at capture (recorded in the ledger progress log):**
- `python -m pytest services/api/tests/rules` → **458 passed** (includes the 90 new
  `test_r3_r4_height.py` cases; zero existing test broken)
- `python tools/modularity_check.py --check` → EXIT 0
- `python services/api/scripts/sync_zr_snapshots.py --check` → EXIT 0
  ("runtime-bundled ZR snapshots are byte-identical to the canonical source (10 file(s))")

**ADDENDUM (post-rework confirmation run):** CI run **34741407310** on head **`e49ac4bd`** (the
rework-round-1 submission head, whose tree contains the corrected snapshot notes at material
commit `346f8535`) concluded **success — all jobs green** (verified via `gh run view` 2026-09-13
~08:00 UTC). This directly re-proves the executable authority at the corrected identity, on top
of G4's independent 458-test reproduction against the corrected snapshot bytes.
