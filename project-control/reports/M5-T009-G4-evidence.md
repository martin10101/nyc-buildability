# M5-T009 — G4 Integration/Regression & Evidence Reproduction (independent)

- **Gate:** G4 (integration/regression, evidence reproduction) — **Verdict:** PASS
- **Recorded reviewer label:** code-reviewer (rostered; ≠ producer). Reproduced by the independent
  **ci-evidence-verifier** and corroborated by code-reviewer (G1) + qa-engineer (G3), who each ran the full
  suite → 252 passed. Recorded under the rostered `code-reviewer` label (ci-evidence-verifier not rostered),
  per M5-T007/T008 precedent. Reviewed SHA `3b298474` (parent `bacb24a7`).

## Claims reproduced (each matches)
| Claim | Observed | Match |
|---|---|---|
| HEAD == 3b298474 / parent bacb24a7 | confirmed | YES |
| Exactly 5 files changed | A report, A _json_safety.py, M ranking.py, M sensitivity.py, A test_json_safety.py | YES |
| No forbidden path (derive/__init__/builder/models/constants/contract, packages/contracts/**) | scoped diff EMPTY | YES |
| Frozen oracle test files UNCHANGED | `diff bacb24a7..3b298474 -- test_scenario_{ranking,sensitivity}.py` EMPTY | YES |
| scenario suite 252 | `252 passed` | YES |
| test_json_safety.py 30 | `30 passed` | YES |
| frozen ranking+sensitivity 98 | `98 passed` | YES |
| 0 regression (252 = 222 + 30) | confirmed | YES |
| determinism byte-identical across reorderings | RANK fwd==rev==shuffled True; SENS fwd==rev True; json.dumps(allow_nan=False) never raised | YES |
| modularity_check --check | failures 0; no warning in app/scenario/ | YES |

## Net SLOC (honest)
`numstat`: _json_safety.py +318; ranking.py net −126; sensitivity.py net −115 → **net +77** (NOT a reduction).
Consumers shrink −241 combined; the shared module (+318) adds the NEW L2 iterative-traversal/cycle-detection +
docstrings. Producer report frames this honestly (de-dup offset by L1/L2 correctness additions) — no claim
contradicted. Pre-existing app/documents/* PEP 695 collection errors (Python 3.11) are unrelated (documents/
diff EMPTY vs parent). Read-only; no state modified.
