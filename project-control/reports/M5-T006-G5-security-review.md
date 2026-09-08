# G5 SECURITY/ROBUSTNESS GATE — M5-T006 (derive.py hardening)

_Reviewer-returned content, preserved verbatim (transport entity-decoding only). Reviewer: security-reviewer (independent, read-only, producer ≠ reviewer)._

**Result: PASS** (three filed LOW findings correctly closed, no regression; one NEW pre-existing LOW finding SEC-L1 recorded for follow-up).

**Reviewed identity:** frozen worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t006`, HEAD `817815cc9f8205fba152d3e4b684b0b036ab56f0`, clean. Producer commit touches only the 3 allowed_paths files; no forbidden path.

## Acceptance scenarios — all reproduced PASS at the frozen SHA
- AS-1 strict-JSON-safe malformed cap: PASS (direct). AS-2 DERIVED-path unchanged: PASS (full-output goldens byte-identical; `cap_raw` verbatim derive.py:475). AS-3 no-alias: PASS. AS-4 bounded echo: PASS for string/count (see SEC-L1 for huge-integer sub-case). AS-5 cap value + never-Verified: PASS (14 factor classes, 3 `verified` casings). AS-6 determinism + regression: PASS — `pytest tests/scenario -q` → **124 passed in 0.55s**, order-independent.

## Independently executed
`git rev-parse HEAD`/`status`; `git diff 6a0d1ef8 HEAD -- derive.py` (additive, DERIVED unchanged); `git diff --stat b0d39ad6 HEAD` (3 allowed_paths files only); purity grep (imports copy/math/typing/.constants only; no eval/exec/open/os/sys/subprocess/socket/requests/urllib/httpx/pickle/environ/getenv); `pytest` 124 passed; adversarial sweeps (16 malformed caps direct+factor, no-alias, huge echoes, huge-int crash probe, 14-class factor sweep, never-Verified casings, determinism).

## Findings closed (as filed)
- **LOW-1:** every NaN/±Inf/negative/10**400/list/dict cap → canonical_cap_sq_ft null + "MALFORMED CAP"; finite non-negative transported verbatim; json.dumps(allow_nan=False) never raised; no NaN/Inf/negative anywhere. `_json_safe_cap` uses float() (OverflowError-guarded), not repr.
- **LOW-2:** `_copy_assumption` deepcopies all five fields; derived nested value/rationale `is not` input; mutating derived never reaches document; docstring truthful.
- **LOW-3:** 100k-char kind/value/key + 50k keys → every reason <2000 chars with truncation marker; full key set in structured data. (String/count inputs.)

## SEC-L1 (LOW, NEW, pre-existing, NON-BLOCKING) — huge-integer echo crash
`_bounded_echo`/`_bounded_key_list_echo` truncate the RESULT of repr()/str(), but the render is evaluated BEFORE truncation; on Python 3.11+ `repr()`/`str()` of an int with >4300 decimal digits raises `ValueError: Exceeds the limit (4300 digits)`. Three sites crash on `value/scenario_kind/key = 10**5000`: derive.py:367 (factor value), :316 (scenario_kind, no-cap path), :159 via `_bounded_key_list_echo` (unapplied key). The float-overflow huge-int class (10**400) is correctly handled (typed invalid_assumption) — only the >4300-digit sub-class crashes (why the suite is green: tests use 10**400).
- **Severity LOW:** genuine unhandled crash (single-request DoS) BUT (a) **pre-existing** — identical repr/str echoes in the accepted M5-T005 base, M5-T006 introduces NO regression; (b) **not reachable via build_scenario** (direct-call-only); (c) no data leak/cross-tenant/privilege/injection.
- Docstring note: post-hardening derive.py:24-30 ("no crash … length-bounded") is slightly over-broad for this case (same truthful-docstring lesson as LOW-2).
- **Remediation (recommended fast-follow, NOT blocking):** `_safe_render(value)` wrapping repr()/str() in try/except ValueError → `f"<{type(value).__name__} unrenderable>"`, then `_bounded_echo(...)`; apply at the 3 sites, tighten the docstring, add a 10**5000 test.

## Required rework: NONE for this gate
M5-T006's chartered scope (close LOW-1/2/3 as filed, no regression) is met. SEC-L1 is pre-existing, out-of-scope, non-pipeline-reachable → recommend an independent follow-up hardening task before further optimization builds on derive.py.

**VERDICT: PASS** (with SEC-L1 recorded as a recommended fast-follow).
