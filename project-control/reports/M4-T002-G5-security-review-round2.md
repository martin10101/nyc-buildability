# M4-T002 — G5 security-reviewer verbatim return, ROUND 2 (post-rebase hardening)

_Verbatim independent security-reviewer return (transport decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

- **Gate ID:** G5 (security & privacy)
- **Task ID:** M4-T002 (rules-engine ↔ property-analysis integration, service layer)
- **Reviewer:** security-reviewer (independent, read-only)
- **Round:** 2 (re-gate after rebase onto M4-T003-corrected main + three G5 follow-ups)
- **Frozen reviewed SHA:** code at `ff33ad2`; worktree HEAD `82512e3` (docs-only commit adding `M4-RULES-FUTURE-HARDENING.md` on top — code byte-identical, verified: `git diff ff33ad2 82512e3` = one ADDED report file, zero code).
- **Result:** PASS

## Scope confirmation
`git diff --name-status origin/main HEAD -- services/` = exactly two ADDED paths, zero modifications to existing code: `services/api/app/rules/integration.py` (571 lines) and `services/api/tests/rules/test_rules_integration.py`. `evaluator.py` and `registry.py` are **byte-identical to origin/main** — the corrected/hardened evaluator is inherited from the already-gated M4-T003 wave, not re-touched here. No `packages/` or contract change. No auth/RLS/migration/storage/endpoint/worker/config surface. Purely additive, in-process, no HTTP/DB/storage/upload/secret/network sink.

Hardening delta `git diff b892975 ff33ad2 -- services/` matches the described follow-ups exactly: adds `import math`, adds `_as_list()`, rewrites `_positive_number()`, swaps the four container sites to `_as_list()`, removes `verified_status_present` from the dataclass and `as_dict()`, plus five new tests.

## Commands run (read-only)
1. `python -m ruff check app tests` → **All checks passed!**
2. `python -m pytest tests/rules/test_rules_integration.py -q` → **35 passed in 1.19s**
3. `python -m pytest -q` (full api) → **694 passed in 17.06s** (no regression; round-1 was 649).
4. Independent hostile probes (one-liners; see per-item evidence below).

## Per-item verification

### LOW-1 (malformed container fail-safe) — CONFIRMED-FIXED
`_as_list()` coerces via `list(value) if isinstance(value, list | tuple) else []`, applied at all four round-1 raise sites: `_base_pairs`, `_preserve_uncertainty` review_reasons/notes, `_input_provenance` provenance_refs.
Repro — spatial section with `pairs=999, review_reasons=5, notes=7, provenance_refs=3`:
```
no-raise fail_safe= True reason= inconsistent_confident_geometry cov= professional_review_required
rr= [] notes= [] prov= []
json_ok= True   (json.dumps(export, allow_nan=False) succeeds)
```
Round-1 these raised `TypeError`; now they fail safe with no value and stay strict-JSON serializable.

### LOW-2 (non-finite lot area) — CONFIRMED-FIXED
`_positive_number()` now requires `math.isfinite(value) and value > 0` inside a `try/except OverflowError`.
```
inf False | -inf False | nan False | neg False | zero False | bigint(10**309) False | bool False | ok(10000.0) True | okint(500) True
```
End-to-end with `+inf` and with `10**309` on both `lot_geometry.area_sq_ft` AND the confident base pair's `lot_area_sq_ft`:
```
district= R5 area= None src= None cov= professional_review_required   json_ok= True
```
District still confidently derived, the non-finite/overflow area rejected at derivation (no fabricated `inf` output), payload strict-JSON safe.

### INFO-4 (vestigial `verified_status_present`) — CONFIRMED-FIXED
Removed from the dataclass and from `as_dict()`. Repo-wide grep of `services/api` returns **only** the removal-assertion test. No production or downstream reference remains.

## New-issue probes
- **Does `_as_list` silently drop a legitimate list?** No. Preserves exactly `list`/`tuple` (what the trusted producer emits) and narrows only genuinely malformed foreign types. Stricter than round-1's `list(x or [])` (which would have iterated a set/dict/generator) — a fail-safe improvement.
- **Does removing the field break a downstream key contract?** No. No consumer reads `verified_status_present`; `tests/app` has no reference.

## Never-Verified invariant against the corrected evaluator — HOLDS
- Barrier B (no G6): `registry.evaluate(...)` passes **no** `g6_approval`; the corrected evaluator can only stamp `verified` for a published rule with a matching G6Approval — impossible here (R5 is `needs_review`).
- Barriers A/C/D/E/F re-verified: `assert_not_verified` checks top-level status + every evaluator trace + `family_coverage`; runs at construction and inside `export()`. The corrected evaluator's new fail-closed behavior (non-finite outputs, invalid `as_of_date`) only strengthens this.
- **Provenance fail-closed** holds: computed values enter only via `result.export()`, which raises on any citation lacking a resolvable `content_digest_sha256`.

## FH-1 / FH-2 remain deferred (not silently "fixed")
`evaluator.py` (`_valid_iso_date`, FH-1) and `registry.py` (`effective_rules`, FH-2) are byte-identical to the gated origin/main — no naive calendar guard or family-wide overlap guard was slipped in. Both stay documented future-hardening items, correctly scoped as prerequisites for the future public endpoint.

## Least privilege / supply chain / drift — clean
integration.py imports only stdlib (`math`, `dataclasses`, `typing`) + internal `app.rules`. No `app.spatial` import; the four spatial constants stay duplicated and are held identical by the RI-S8 drift guard. No new dependency/network/secret/filesystem-write/env; no logging/print. No packages/contracts change.

## Findings by severity
CRITICAL/HIGH/MEDIUM: none. LOW/INFO newly introduced: none. All three round-1 follow-ups (LOW-1, LOW-2, INFO-4) CONFIRMED-FIXED. Round-1 INFO-3 (non-dict `profile` arg → AttributeError) is unchanged and remains an accepted caller-contract note, not attacker-reachable in this in-process no-endpoint slice. (Carry-forward INFO also raised by G3: `assert_not_verified` iterates `evaluations or []` — a foreign non-iterable payload would raise there; outside this delta's four spatial sites, unreachable from the internal producer; recorded as FH-3.)

## Conclusion
The three previously-non-blocking G5 follow-ups are correctly and completely implemented at `ff33ad2`; no fail-open or regression was introduced by the rebase or the hardening. The never-Verified (six barriers), provenance-fail-closed, and fail-safe invariants all still hold against the corrected evaluator. Scope is two additive files over the gated corrected main; ruff clean; 35 integration + 694 full tests pass.

**VERDICT: PASS**

_Reviewer note: the read-only guard intermittently blocked some multi-line inline `python -c` probes and all file writes; equivalent coverage was obtained via one-liner reproductions plus the executed test suite, so no BLOCKED condition applies._
