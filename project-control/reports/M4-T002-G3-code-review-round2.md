# M4-T002 — G3 code-review verbatim return, ROUND 2 (post-rebase hardening DELTA)

_Verbatim independent code-reviewer return (transport decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

- **Gate ID:** G3 (independent code review)
- **Task ID:** M4-T002 (rules-engine ↔ property-analysis integration, service layer)
- **Reviewer:** code-reviewer (independent, read-only)
- **Producer:** lead orchestrator
- **Result:** PASS (0 blocking, 1 INFO carry-forward)
- **Scope of this re-gate:** the DELTA `b892975..ff33ad2 -- services/` only. Round-1 G3 PASSed at f25dbff/609efe9; the branch was rebased onto M4-T003-corrected main (origin/main f5ab631) and three G5 follow-ups (LOW-1, LOW-2, INFO-4) were applied.
- **Frozen SHA / worktree:** worktree `.claude/worktrees/M4-T002-integration`; `git status --short` empty. HEAD `82512e3` is docs-only (`git diff ff33ad2 82512e3 --name-only` = exactly `project-control/reports/M4-RULES-FUTURE-HARDENING.md`); reviewed code == `ff33ad2`. Python 3.11, ruff clean, pytest 694 passed.

## Commands executed (read-only)
1. `git diff b892975 ff33ad2 -- services/` → touches only integration.py + the test file; no profile/spatial/contract/endpoint/UI/migration/RLS surface.
2. `python -m ruff check app tests` → **All checks passed!**
3. `python -m pytest tests/rules/test_rules_integration.py -q` → **35 passed** (0.42s).
4. `python -m pytest -q` (full `services/api`) → **694 passed** (5.82s); no regression.
5. `grep verified_status_present services/**` → only the HARD-3 test asserting its removal; **zero production references**.
6. Empirical probe of `_positive_number` / `_as_list`.

## Confirmations against the required checklist

**`_as_list(value)` — correct, no data loss, all four sites covered.** Returns `list(value) if isinstance(value, list | tuple) else []`. Empirically preserves lists/tuples as a new shallow copy (same semantics as the previous `list(x or [])`), narrows malformed inputs (`999`, dict, `None`, `"ab"`) to `[]`. All four previously-raising LOW-1 sites route through it. Bonus: fixes a latent bug where old `list("ab" or [])` split a stray string into `['a','b']`; now `[]`.

**`_positive_number` — correct.** `math` imported. bool/non-numeric rejected first, then `math.isfinite(value) and value > 0` inside a `try` catching `OverflowError`. Empirically `10**309`→False (OverflowError caught), `inf/-inf/nan/0/-1.0/True/"5"/None`→False, `1.5`→True.

**Removal of `verified_status_present` — clean.** Gone from the dataclass field list and `as_dict()`. No production reference. Dataclass field ordering still valid: `coverage_source` is the sole defaulted field and is last; no non-default field follows a default. 694 tests exercise `as_dict`/`export`.

**No contract/endpoint/UI change; never-Verified guard and export() path unchanged.** The diff does not touch `assert_not_verified`, `export()`, the fail-safe branches, or the confident-path evaluator call. Draft-never-Verified and provenance-fail-closed are byte-identical to round-1-reviewed code.

**Tests HARD-1..HARD-4 — meaningful; HARD-1/2/3 regression-meaningful.**
- HARD-1: `pairs=999`/`review_reasons=5`/`notes=7`/`provenance_refs=3` → no raise, `FAILSAFE_INCONSISTENT_CONFIDENT`, coercion to `[]`. Pre-hardening `list(5)` raises TypeError → **fails pre-hardening, passes post**.
- HARD-2: `inf` on both geometry area and confident pair → district `"R5"`, `lot_area_sq_ft is None`, coverage PRR, `"inf" not in json.dumps(...)` + `allow_nan=False`. Pre-hardening admitted `inf` → these **fail pre-hardening**.
- HARD-2b (NaN/-1.0/0.0): honestly labeled "already rejected" — valid forward pin, not overstated.
- HARD-3: `not hasattr` + absence in `as_dict()`/`export()` — fails pre-removal, passes post.
- HARD-4: strict-JSON invariant on a normal confident result; reinforcing.

## Findings (severity-ranked)
- **INFO-1 (carry-forward, non-blocking) — `integration.py` `assert_not_verified`.** Still iterates `data.get("evaluations") or []`; a downstream caller passing a foreign payload whose `evaluations` is a truthy non-iterable would raise `TypeError` there. *Outside* the four LOW-1 spatial-container sites (this delta's scope) and unreachable from the internal producer (always a list). Consistent with the G5 note that a robust guard is stronger for arbitrary foreign payloads. Worth folding into the pre-endpoint-exposure hardening task; not a defect in this delta.

## Defects / required rework
None blocking. LOW-1, LOW-2, and INFO-4 are correctly and completely remediated.

## Reviewer conclusion
A tight, correct hardening of exactly the three tracked findings, with no contract, endpoint, provenance, or never-Verified behavior change. `_as_list` preserves legitimate lists and cannot drop real data; all four raising sites covered. `_positive_number` admits only finite positives. The vestigial field is fully removed with a valid dataclass and no dangling references. New tests assert the specific fix behavior and (HARD-1/2/3) are genuinely regression-meaningful. Ruff clean; 35/35 integration and 694/694 full suite pass; reviewed code frozen at ff33ad2.

**VERDICT: PASS**
