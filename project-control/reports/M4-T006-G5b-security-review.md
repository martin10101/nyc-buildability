_Verbatim independent security-reviewer return, ROUND 2 (post legal-semantics correction; transport entity-decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes. Orchestrator-captured pytest evidence (requested by the reviewer): `pytest tests/rules/test_r5_height_setback.py -q` → 47 passed; full `pytest -q` → 928 passed; `sync_zr_snapshots.py --check` → byte-identical (6); all at 5d605d4._

# G5 SECURITY & PRIVACY GATE REPORT — M4-T006 (re-review)

**Task:** M4-T006 — R5 height/setback rule (legal-semantics correction)
**Reviewed SHA (frozen):** `5d605d4` on `task/M4-T006-r5-height-setback` (PR #88)
**Prior frozen SHA:** `6509db3` (already G5 PASS)
**Reviewer:** security-reviewer (independent, read-only)
**Verdict:** **PASS** (final acceptance remains gated on G6 qualified-human legal approval)

## Diff-scope confirmation
`git merge-base 6509db3 5d605d4` = `6509db3` (prior frozen SHA is a direct ancestor). The reverse range `5d605d4..6509db3` is empty.

The correction commit `5d605d4` itself (`git diff-tree --no-commit-id --name-only -r 5d605d4`) changes **exactly the 2 in-scope files**:
- `services/api/app/rules/rulesets/r5_setback.rule.json`
- `services/api/tests/rules/test_r5_height_setback.py`

`git diff --name-only 6509db3 5d605d4 -- services/api/` = the same 2 files and nothing else. Scoped to rules/contracts/snapshots, the only change is `r5_setback.rule.json`. Evaluator, engine, all other rulesets, canonical contract, and snapshots are byte-unchanged.

Note (non-blocking, informational): the raw `git diff --name-only 6509db3 5d605d4` lists ~70 files. These are NOT part of this correction — they arrive via two ancestry merges on the branch (`8c53433` merge of origin/main and `a3784af` PR #89 = the already-ACCEPTED M0-T022 owner-dashboard work). `git diff --stat origin/main 5d605d4` confirms the dashboard trees are byte-identical to accepted main (zero diff); the only files differing from main are the M4-T006 rules/tests/control artifacts the whole task legitimately owns. No smuggled changes.

## Findings

### Focus 1 — Draft-not-Verified integrity: PASS
- Rule `status` remains `"needs_review"`; `release.independent_review` and `qualified_human_approval` remain `"pending"`. Unchanged by the correction.
- Engine (`evaluate`): `verified_eligible = rule.status == STATUS_PUBLISHED and _approval_matches(rule, g6_approval)`. `needs_review` != `published` => `verified_eligible` is `False` => `base_coverage = CONDITIONAL`. `verified` is structurally unreachable for this rule regardless of inputs or the new exception. No emit path to `verified` was introduced.
- Value/coverage unchanged: computation still selects `{wide:10, narrow:15}` by `street_width_class`; the confident path is still `conditional`; missing `street_width_class` still fails closed to `professional_review_required` with no computed value (step-1 `_validate_inputs`). The parameter map value `{wide:10, narrow:15}` is byte-identical.

### Focus 2 — Honesty / no overclaim, no dynamic execution: PASS
- The new exception `section_23_423_modifications_unresolved` has `"condition": null` => in `_apply_exceptions`, `holds = True` always => it is always recorded in `exceptions_applied`/`notes`. It is pure declarative data (description text + `effect: "documented_limitation"` + `citation_ref`). No code, no operator, no input reference, no eval/exec.
- `effect == "documented_limitation"` hits neither the `professional_review_required` nor `conditional_alternative` branch, so it applies **no coverage change** (engine comment: "recorded as a note only"). The result is strictly MORE conservative: it flags the §23-423 reductions/modifications (7 ft floor, recesses/outer courts, >50 ft optionality, dormers) as UNRESOLVED and that 10/15 is "never the final legally applicable setback." This removes overclaim rather than adding finality. Output/parameter/limitation text was re-labelled to "STANDARD UNMODIFIED starting" — a downward (more honest) claim.

### Focus 3 — No injection/secret/PII/leak, least privilege, no scope creep: PASS
- Both changed files reviewed in full. No secrets, tokens, credentials, absolute paths, PII, or environment values introduced. No network/filesystem/DB/env/subprocess reach; no `eval`/`exec`; no new inputs or parameters (no new attack surface). The engine, canonical contract, response models, and every other ruleset are byte-unchanged. No scope creep.

### Focus 4 — Tamper-evidence unaffected: PASS
- No files under the snapshots trees changed (name-only diff scoped to snapshots is empty). The snapshot hash guard is intact. Citations in the rule (snapshot_ids `zr-23-423`, `zr-12-10`, `zr-23-422`) are unchanged.

### Test change — PASS
`test_r5_height_setback.py` adds one parametrized test (`test_as1_r5_setback_10_15_are_standard_unmodified_not_final`) asserting the marker is present in `res.trace.exceptions_applied` with `effect == "documented_limitation"` and honesty text. It only reads results; it strengthens the honesty invariant. No pre-existing assertions were removed or weakened.

## Non-blocking items
1. **Test execution not reproduced in-sandbox** (read-only guard prevents materializing the frozen tree). Static analysis is conclusive for the security scope; orchestrator attached the `pytest tests/rules/test_r5_height_setback.py -q` output (G3/G4 already exercise this suite) for the record — see header.
2. **Draft provenance still open (expected, not a G5 defect):** values remain "pending raw-HTML verbatim verification and G6 approval." This is correctly surfaced in `limitations[]` and `status:needs_review`. G6 must resolve before any `verified`/published transition.

## Conclusion
The correction is a declarative, honesty-strengthening, more-conservative change confined to 2 files. It cannot surface a draft as Verified (`verified` remains structurally unreachable at `needs_review`), weakens no guard, changes no value/coverage, and introduces no injection/secret/PII/network/tamper exposure. Security posture is preserved.

**VERDICT: PASS** — reviewed SHA `5d605d4`. Final acceptance stays gated on **G6** (qualified-human legal approval). Do not publish/emit as Verified before G6.
