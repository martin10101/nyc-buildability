# GATE REPORT — G1 Code Review — M5-T006 (derive.py hardening)

_Reviewer-returned content, preserved verbatim (transport entity-decoding only). Reviewer: code-reviewer (independent, read-only, producer ≠ reviewer)._

**Verdict: PASS**

**Reviewed identity:** branch `task/M5-T006-derive-hardening` @ `817815cc9f8205fba152d3e4b684b0b036ab56f0`; worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t006`.

## Identity & scope
- `git rev-parse HEAD` == 817815cc (matches); worktree clean. `git diff --name-only 817815cc^ 817815cc` = exactly 3 files: `derive.py`, `test_scenario_derive.py`, `M5-T006-producer-report.md`. **Contract-free CONFIRMED** — no builder/models/constants/contract/__init__/packages/lockfile edits.

## Reproduced tests
- `python -m pytest tests/scenario -q` → **124 passed in 0.55s** (Python 3.11.9). Independent probe: 73/73 checks incl. a byte-level DERIVED-path comparison against the parent (M5-T005) via `git show 817815cc^`.

## Finding-by-finding
**LOW-1 strict-JSON-safety — VERIFIED.** `_json_safe_cap` (derive.py:172-187) applied only inside `_not_derivable` (:245); DERIVED path still emits `cap_raw` verbatim (:475, identical to parent :381). Malformed caps (NaN/±Inf/−5/−0.5/10**400) direct → derivable=False, canonical_cap_sq_ft None, "MALFORMED CAP" reason, json.dumps(allow_nan=False) SUCCEEDS with no NaN/Inf/negative. No false positives (0, "n/a", None transported verbatim). **No DERIVED-path regression:** 9 positive-finite cases byte-identical (json.dumps) to parent; int stays int. Parent counter-check: parent transported NaN verbatim and json.dumps(allow_nan=False) RAISED — fix closes a real defect, additive.

**LOW-2 no-alias + honest docstring — VERIFIED.** `_copy_assumption` (:199-210) now `copy.deepcopy`s key/type/value/unit/rationale. Unapplied nested-mutable value: `out["value"] is not input["value"]`, value-equal, mutating derived doesn't reach input (doc == snapshot). Same for APPLIED factor rationale. Docstring's "NEVER aliases the input" now literally true.

**LOW-3 bounded echo — VERIFIED.** All three echo sites bounded: scenario_kind (:316), factor value (:367) via `_bounded_echo` (120-char cap + "...(truncated)"), unapplied-key aggregate (:467) via `_bounded_key_list_echo` (per-key + 12-key count bound + "(+N more … truncated)"). 100k-char kind/value + 20,000-key list each keep reasons <2000 chars with a marker; full key set stays in structured `unapplied_assumptions`.

## Other checks
Deterministic (byte-identical on hardened paths); never emits 'verified' (incoming capped to conditional); cap VALUE never recomputed on DERIVED path (`cap_raw` verbatim, separate `cap_float` for arithmetic); modularity `failures 0` (derive.py 490 lines, not flagged); AI-boundary/provenance intact.

## Non-blocking observations (no action)
- A `bool` cap on a fail-closed outcome passes `_json_safe_cap` verbatim (true/false); JSON-safe, non-numeric, no contract violation.
- A non-number container cap is nulled with only the base not_derivable reason (no MALFORMED CAP line, gated on `_is_number`); acceptable — base reason explains the absent cap, output strict-JSON-safe.

**Recommendation: PASS** — all three G5 LOW findings closed, additively, no regression to accepted M5-T005 behavior (DERIVED path byte-identical to parent), contract-free, deterministic, strict-JSON-safe.
