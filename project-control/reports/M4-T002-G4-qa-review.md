# M4-T002 — G4 qa-engineer verbatim return (frozen SHA 609efe9)

VERDICT: PASS (with blocking TEST-ONLY corrections C1-C3; production code unchanged/correct)

---

# Gate Report

- **Gate ID:** G4 (integration-and-regression QA)
- **Task ID:** M4-T002 (rules-engine ↔ property-analysis integration)
- **Reviewer:** qa-engineer (independent; read-only)
- **Producer:** lead orchestrator (lead-only, owner directive 2026-07-21)
- **Result:** PASS (with blocking test-addition corrections C1–C3; production code unchanged)
- **Clean environment/worktree used:** frozen worktree `.claude/worktrees/M4-T002-integration` at SHA `609efe917ebfcedc3e0512bab5c4ed2b82e445b0`, branch `task/M4-T002-integration`, base main `f2939d6`. Python 3.11.9, pytest 8.4.2, ruff, jsonschema, shapely 2.0.7.

## Steps independently executed
```
$ python -m pytest tests/rules/test_rules_integration.py -v  =>  23 passed in 0.36s
$ python -m pytest -q                                         =>  649 passed in 4.42s  (626 baseline + 23; NO regression)
$ python -m ruff check app tests                              =>  All checks passed!
```
Additional read-only checks: hash-diff of `services/api/app/spatial`, `app/profile`, `packages/contracts` between the frozen worktree and main = IDENTICAL; `app/rules` differs only by the added `integration.py` (every pre-existing engine source byte-identical). Determinism source audit: no datetime/random/time/uuid/perf_counter/monotonic in app/rules (only "time" in comments); ordering via sorted(statuses) + sorted(glob).

## RI-S1..RI-S8 coverage map
| RI | Verdict |
|---|---|
| S1 confident R5 conditional + trace + citations | PASS (strong) |
| S2 uncertainty preserved, no district/value | PASS (strong) |
| S3 fail-safe on missing evidence | PASS |
| S4 honest draft status + disclaimer | PASS |
| S5 determinism byte-identical | PASS (strong) |
| S6 coverage honesty not_applicable/unsupported | PASS |
| S7 never-Verified proof | PASS (strong) |
| S8 CI green + no profile/spatial/contract change | PASS (strong) |

## Fixture fidelity
Faithful — green tests genuinely imply real-profile correctness. Fixtures built from REAL app.spatial dataclasses serialized via _spatial_section exactly as wave_integration._spatial_intersection_section (as_dict() minus coverage_audits + provenance_refs). Every field the integration reads is produced by the real as_dict(); RI-S8 drift guard pins the four constants; real registry + real ZR 23-21 snapshot so citations resolve for real. No drift risk beyond the guarded duplication.

## Coverage-gap hunt (throwaway scratch probes; NOT added to repo) — every probed behaviour is CORRECT, no defect
| Probe | State | Observed | Assessment |
|---|---|---|---|
| gap1 | 2x interior_confident on single_district_confident | fail-safe inconsistent_confident_geometry, no district/value | correct; defensive path untested |
| gap2 | commercial-overlay (non-base) pair + confident R5 base | district=R5, conditional, far=1.5, overlay excluded from base_district_candidates (['R5']) | correct; realistic; ONLY case exercising the _base_pairs family filter — no repo fixture has a non-base pair |
| gap3 | confident district but lot_area missing (geometry absent + non-positive pair area) | district=R5, lot_area=None, coverage=professional_review_required, evaluations[0].outputs=={}, completeness=missing_critical | correct; exercises evaluator missing-critical via the confident branch, untested in repo |
| gap4 | minor_portion=True on confident base pair | surfaced in base_district_candidates | correct; untested |
| gap5 | R5A and R5B | far=1.5/floor=15000, conditional | correct; packet-named variants untested (only R5/R5D covered) |
| gap6 | empty pairs on single_district_confident | fail-safe inconsistent_confident_geometry, no district | correct; untested |
| obs-ext | 1 interior + 1 exterior_confident base pair (REACHABLE — engine retains exterior pairs, doesn't count them in the confident guard) | determination correct (R5, conditional, far=1.5); base_district_candidates lists non-overlapping R6 with pair_class="exterior_confident", share_point=0.0 | not a defect; disclosure-fidelity observation for downstream consumers |

## Required rework (blocking corrections — TEST-ONLY; no production change)
- **C1 (overlay pair):** add confident R5 base pair + commercial-overlay (family != base_zoning) pair → assert district=R5, far computed, overlay excluded from base_district_candidates. Only test exercising the _base_pairs family filter with a real non-base pair.
- **C2 (confident district, missing lot_area):** confident R5 but no positive lot area (geometry absent + non-positive pair area) → assert coverage=professional_review_required, zoning_district="R5", evaluations[0].outputs=={}, completeness missing_critical, fail_safe False. Exercises evaluator missing-critical via confident branch.
- **C3 (R5A/R5B variants):** assert R5A and R5B → FAR 1.5 (packet-named).
Recommended (non-blocking): gap1 (2x interior → fail safe), gap4 (minor_portion pass-through), gap6 (empty pairs → fail safe), and assert base_district_candidates entries carry pair_class so a consumer can filter exterior_confident/share_point==0 neighbours (obs-ext).

## Findings summary
No defects. No regression (649 passed). Provenance fail-closed; never-Verified fail-closed at three layers; determinism structural; read-only/in-process, no security concern. Human-walkthrough N/A (service-layer only). Blocking items are TEST additions C1-C3; production code already correct and must not change.

VERDICT: PASS
