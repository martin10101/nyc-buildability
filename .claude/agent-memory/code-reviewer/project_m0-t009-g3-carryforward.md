---
name: m0-t009-g3-carryforward
description: M0-T009 contracts v1 G3 PASS (2026-07-15); low residuals (Python-vs-ECMA regex $ newline edge, calendar-invalid dates, invariant hard-codes fact sections) to recheck when a JS validator or new fact_value section lands
metadata:
  type: project
---

M0-T009 (canonical contracts v1) G3 reviewed 2026-07-15: **PASS** at `522d3b2`. All M0-T004 carry-forward defects D1-D5 verified closed ([[m0-t004-g3-carryforward]] is now fully discharged). Reviewer independently executed the validator in both engine modes plus adversarial mutation tests in a temp copy.

Low residuals to recheck later:
1. Python `re` `$` accepts a trailing `\n` in all anchored patterns (bbl/bin/zip/date/date_time in `common.schema.json`); ECMA-262 validators would reject → cross-engine divergence if a JS validator is ever added (frontend). Recheck when any non-Python contract validation lands, and confirm M1 connector normalization strips trailing whitespace.
2. Date patterns accept `2026-99-99`; calendar validity is a backend obligation — check M1/M2 normalization code enforces it.
3. `profile_provenance_invariant()` in `.github/scripts/validate_contracts.py` hard-codes `lot_facts`/`existing_building_facts`; any schema revision adding `fact_value` elsewhere must extend it in the same commit.
4. No valid borough-5 boundary fixture exists (invalid boundary fixtures only).

**Why:** these were low severity (fixtures/CI all pass; grounded in docs/research/M0-T002 which I verified line-by-line), so PASS without rework; they become real defects at the milestones named above.
**How to apply:** when reviewing M1 connectors, M2 zoning enums, or any packages/contracts change, check these four first. Useful fact: reviewer sandbox CAN run read-only python; simulate jsonschema absence with a sys.meta_path import blocker; test validator mutations in a `mktemp -d` copy, never the worktree.
