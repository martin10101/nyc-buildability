# M5-T045 — CI evidence (orchestrator-captured)

Branch `candidate/D-024-mrl-option-b`.

## Head `21ee7379` — the FIRST head whose CI covers the T045 material

| run | workflow | conclusion |
|---|---|---|
| 35431367744 | CI (incl. web-e2e: vitest + Playwright vs recorded-official-fixture API) | **success** |
| 35431367763 | secret-scan | success |
| 35431367746 | context-budget | success |

The T045 material entered candidate as cherry-pick `28082288`; every commit between it
and `21ee7379` is control-plane/report-only for the T045 surface (the T047 submission
evidence — a DISJOINT peer). The T045 surface is byte-identical from `28082288` through
the submission head.

Orchestrator-reproduced documented commands at the material identity (wt-m5t045, all from
the packet-specified cwds): `python -m ruff check .` clean; focused condo suites 81
passed; the seam trio 58 passed; the full `tests/connectors tests/spatial tests/profile
tests/api` regression 1494 passed; `python tools/modularity_check.py --check` exit 0.

Run history context: the build spanned supervised runs 48–51 (DB-012 trips 15/17/18 —
each after substantive work; run 49's wave produced the scope finding that became the
recorded ORCH-SCOPE-DISPOSITION + DB-031; run 51 closed with a STOP_FOR_OWNER whose
question the recorded disposition already answered, at which point the orchestrator
harvested).
