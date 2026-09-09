# M5-T008 — G4 Integration/Regression & Evidence Reproduction (independent)

- **Gate:** G4 (integration/regression, evidence reproduction)
- **Verdict:** PASS
- **Recorded reviewer label:** code-reviewer (rostered independent reviewer; ≠ producer). The integration/regression evidence below was reproduced by the independent **ci-evidence-verifier** and independently corroborated by the **code-reviewer** (G1) and **qa-engineer** (G3), who each ran the full scenario suite → 222 passed, 0 regression. Recorded under the rostered `code-reviewer` label per the task roster + M5-T007 precedent.
- **Reviewed SHA:** `24780f2683dafd41b895fa2d1668814a19a6b3e4` (parent `1915336e`)

## Claims reproduced (each observed value matches)
| Claim | Observed | Match |
|---|---|---|
| HEAD == 24780f26 | `24780f2683dafd41b895fa2d1668814a19a6b3e4` | YES |
| parent == 1915336e | `1915336e51bed126fc47ab46a8ade1e764f8fb58` | YES |
| Exactly 4 files changed | A producer-report, M __init__.py, A sensitivity.py, A test file; +1271, 0 deletions | YES |
| NO forbidden path | derive.py/ranking.py/builder.py/models.py/constants.py/contract.py/packages/contracts/** absent | YES |
| sensitivity file 49 items | `49 passed in 0.11s` | YES |
| scenario suite 222 | `222 passed in 0.79s` | YES |
| 173 pre-existing pass (222−49) | 173, 0 regression | YES |
| determinism byte-identical across value orders | forward==reversed==shuffled, identical SHA 9af533e14000f1b7 (len 15262) | YES |

## Notes (benign)
- Environment Python 3.11.9 / pytest 8.4.2. Scenario modules have no PEP 695; collect/pass cleanly.
- `pytest services/api -q` (broad) → 15 collection errors, ALL PEP 695 `SyntaxError` in `app/documents/*` requiring Python ≥3.12; `git diff 1915336e..24780f26 -- services/api/app/documents services/api/tests/documents` is EMPTY → pre-existing, unrelated to this change.

No file/git/control-plane state modified (read-only).
