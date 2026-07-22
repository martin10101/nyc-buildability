# M4-T004 — G5 (security & privacy) verbatim return

_Verbatim independent security-reviewer return (transport decoding only). Orchestrator-recorded._

**Task:** M4-T004 — pre-endpoint fail-closed safeguards. **Frozen SHA:** `3e45524`. **Reviewer:** security-reviewer (read-only). **Verdict: PASS.**

## Scope (additive-only, verified)
Diff `58432cf..3e45524` touches only `evaluator.py/integration.py/registry.py`, synthetic fixtures + snapshot under `tests/rules/fixtures/m4t004*/`, `test_rules_fh_safeguards.py`, and this task's control-plane files. `models.py`, `coverage.py`, `lifecycle.py`, `dsl.py`, `snapshots.py`, `operations.py` byte-identical. No contract/lock/manifest/script/real-rule change. Only new `app/` import is stdlib `datetime` (FH-1). No new network/secret/env/filesystem/privilege. Fixtures all labeled SYNTHETIC (district SYNTH, extracted_draft, limitations require official capture + G6).

## Commands (from services/api)
`ruff check app tests` → All checks passed. `pytest tests/rules/ -q` → 152 passed. `pytest -q` → 742 passed.

## FH-1 — impossible-date fail-closed
Independently verified: 2024-02-30, 2024-04-31, 2024-11-31, 2025-02-29, 2023-02-29, 2024-13-01, 2024-00-10, 2024-01-00, 0000-01-01 → False; leap 2024-02-29/2000-02-29 → True; None/20240101/['2024-01-01']/3.14 → False. Via datetime.date in try/except ValueError; no exception escapes. Through the evaluator, impossible as_of_date → professional_review_required, in_effect False, empty outputs, strict-JSON intact.

## FH-3 — foreign-payload robustness (never-Verified not weakened)
Non-list evaluations (5, {'a':1}, 'verified', 0, 3.14, (1,2)) and non-dict family_coverage (5, 'verified', ['x'], 0) → no exception. Genuine verified STILL caught at top-level, in a trace nested in a list alongside junk siblings, and in family_coverage — all raise DraftVerifiedError. Disclaimer text "Verified" correctly not a status.

## FH-2 — strictly fail-closed conflict detection (never selects/ranks/merges)
- (a) Typed conflict keys {conflict, family, as_of_date, competing_output_names, competing_rules, note}; competing_rules carry only {rule_id, rule_version, effective_from, effective_to, output_names} — no outputs/determination/value field; a determination cannot leak. Coverage PRR; evaluations=[] (no value); district + input_provenance preserved.
- (b) Deterministic/load-order-independent: all permutations → byte-identical JSON (2-rule and synthesized 3-rule); competing IDs sorted.
- (c) Negative controls → None: different families (per-family detection), non-overlapping windows, mutually-exclusive applicability, complementary different-output rules.
- (d) Half-open [effective_from, effective_to): from INCLUSIVE, to EXCLUSIVE. Seam 2024-01-01 → exactly one governs → None; conflict only strictly inside overlap.
- (e) applicability_satisfied catches (KeyError, TypeError, ValueError, IndexError) → False; malformed predicate/node → False, never a false-positive conflict, never an escaping exception.
- (f) strict-JSON on conflict export holds. (g) never-Verified holds (conflict is PRR).

**Fail-open hunt:** passing impossible as_of_date through evaluate_property on the overlapping temporal registry → professional_review_required, fail_safe True, evaluations=[], no non-empty outputs (fail-closed). By inspection, if a lexical compare leaves ≤1 candidate, evaluate_property then calls registry.evaluate(as_of_date=impossible) and the evaluator's as_of_invalid guard returns PRR before any computation. No path where FH-2 picks/ranks a rule or emits a legal value.

## Real R5 unaffected
families() = ['residential_far'] (single rule); detect_conflicts → None with/without as_of_date; as_of_date threading additive (default None = prior behavior); regression FAR 1.5 / 15000 unchanged.

## Findings
CRITICAL/HIGH/MEDIUM: none. INFO-1 (non-blocking): detect_rule_conflicts gates temporal effectiveness via is_in_effect (lexical) rather than FH-1's _valid_iso_date; proven fail-closed on every reachable path — optional future tightening for the endpoint task. INFO-2: conflict result intentionally preserves district + provenance per FH-2 spec.

## VERDICT: PASS
