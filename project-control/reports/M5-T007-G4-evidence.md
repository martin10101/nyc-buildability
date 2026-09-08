# M5-T007 — G4 Integration/Regression & Evidence Reproduction (independent)

- **Gate:** G4 (integration/regression, evidence reproduction)
- **Verdict:** PASS
- **Recorded reviewer label:** code-reviewer (rostered independent reviewer; ≠ producer). The integration/regression evidence below was reproduced by the independent **ci-evidence-verifier** and independently corroborated by the **code-reviewer** (G1) and **qa-engineer** (G3), who each ran the full scenario suite → 173 passed, 0 regression. Recorded under the rostered `code-reviewer` label per the task roster + M5-T006 precedent.
- **Reviewed SHA:** `1f938f4a7b174c0338c0ecdb2ef0c6b14bdba436` (parent `8f1b049d`)

## Claims reproduced (each observed value matches)
| Claim | Observed | Match |
|---|---|---|
| HEAD == 1f938f4a | `1f938f4a7b174c0338c0ecdb2ef0c6b14bdba436` | YES |
| parent == 8f1b049d | `8f1b049dae8cfc066b78b9f1185e4bee8d93f7b1` | YES |
| Exactly 4 files changed | 4 files, +1947, 0 deletions | YES |
| ranking.py NEW (673) | `A services/api/app/scenario/ranking.py` | YES |
| __init__.py +10 | `M …/__init__.py \| 10 +` | YES |
| test file NEW (638) | `A …/test_scenario_ranking.py` | YES |
| producer report NEW (626) | `A project-control/reports/M5-T007-producer-report.md` | YES |
| NO forbidden path | only the 4 files; derive/builder/models/constants/contract/packages/contracts/** absent | YES |
| ranking file 49 items | `49 passed in 0.11s` | YES |
| scenario suite 173 | `173 passed in 0.69s` | YES |
| 124 pre-existing pass (173−49) | `124 passed` | YES |
| determinism byte-identical across set orders | `byte-identical (insertion order): True`; allow_nan=False no raise; len 14220 | YES |

## Notes (benign)
- Environment is Python 3.11.9 / pytest 8.4.2. The scenario module has no PEP 695 syntax and collects/passes cleanly on 3.11.9, so 49/173/124 counts fully reproduced regardless of interpreter version.
- `pytest services/api -q` (broad) interrupts with 15 collection errors, ALL `SyntaxError` at `app/documents/units.py:276` (PEP 695 generics requiring Python ≥3.12). Confirmed identical line/error on the PARENT commit 8f1b049d → pre-existing, environment-driven (3.11 sandbox), entirely in the unrelated `app.documents.*` tree; none involve `app.scenario`. This change introduces no new failure; 173 = 124 + 49 confirmed by two runs.

No file/git/control-plane state modified (read-only).
