# M5-T033 producer report — deployed `spatial_intersection_absent` root cause (D-059-R004)

Task: M5-T033 · Directive refs: D-059 (D-059-R004), D-066 (ALL) · Producer: backend-engineer
Revision pass (rework within allowed paths). This report is the verbatim producer return; the
control CLI, gates, and acceptance are the orchestrator's (ADR-005).

## 1. One causal account (reproduced code behavior; runtime cause UNCONFIRMED)

The deployed uniform `spatial_intersection_absent` is produced by the rule-evaluation route's
DEFAULT server-side spatial provider returning `None` for every BBL. A `None` substrate makes the
evaluator fail-safe to `spatial_intersection_absent` / `professional_review_required` with no
district and no value (`services/api/app/rules/integration.py` RI-S3, `FAILSAFE_SPATIAL_ABSENT`
at line 81 — corroborated in source). Below are **two reproduced, NON-EXHAUSTIVE candidate
branches** that each yield `None` for every BBL with an identical response body. They are the two I
reproduced deterministically in tests, **not** a closed enumeration of every way the substrate can be
absent — the enabled path also fail-safes to `None` on data-sufficiency and substrate-composition
failures (see the note after Branch B):

- **Branch A — flag disabled (deploy-config regression).** `LIVE_SPATIAL_PROVIDER_ENABLED` absent /
  empty / non-true → `default_live_substrate()` returns `None` with **zero** connector calls and
  **no** provider fail-safe log line. Uniform across every BBL, and fast (no network I/O).
- **Branch B — flag enabled + a SHARED connector/network failure.** With the flag on, if the same
  upstream fault hits every parcel's connector call (e.g. DNS/connection error, open circuit
  breaker), `build_live_substrate()` lands in its fail-safe `except` and returns `None` — also
  uniform, and can also be fast — but it **did** make connector calls and logs exactly one typed
  `connector_error` line per parcel.

**Not exhaustive — other enabled-path causes yield the same absent body.** Even with the flag on and
connectors reachable, `build_live_substrate()` also returns `None` on **data-sufficiency** and
**substrate-composition** failures: an empty/insufficient ZTLDB assignment yields a typed
`no_candidate_districts` fail-safe; a transfer-limited district page yields `district_page_partial`;
and the M2-T013 engine may still decline to compose a confident single-district substrate from
otherwise-successful connector data. These are neither a disabled flag nor necessarily a
connector/network fault, they emit their own typed events, and — like Branches A and B — they are
distinguished only by correlated typed evidence, never by the absent response body.

Because every one of these branches returns the same response body (`spatial_intersection_absent`),
the response body alone **cannot** distinguish them. The 2026-09-17 live capture
(`project-control/reports/M5-T033-live-capture.md`: uniform absent across both D-059 parcels AND a
known-good control `1008350041`, each ~0.6–0.7 s) is **consistent with branch A, with branch B, and
with the other enabled-path causes above**. Uniformity and latency are **suggestive, not decisive**.
I do **not** claim a confirmed deployed cause, completion, or branch selection from response
uniformity or latency.

**Decisive discriminators (read at the runtime boundary, owner-visible only):** (1) the dashboard
reading of `LIVE_SPATIAL_PROVIDER_ENABLED`, and (2) the correlated typed `connector_error` log
(present only in branch B; match its `correlation_id` to the response `X-Correlation-ID`).

**M4-T020 / B4 does NOT fix this.** The live provider has its own flag and failure conditions and
does not use the wide-street/street-centerline module (stated in checklist §6b and D-059-R004).

## 2. The single remaining owner confirmation — both readings

The one remaining step is the owner dashboard read of `LIVE_SPATIAL_PROVIDER_ENABLED` on
`nycdf-api → Environment`, for the SAME deployment the capture ran against (backend commit
`f0e7d82f`; re-capture first if redeployed since). Exact expected readings (checklist §6b table):

- **Reading = absent / empty / any non-true value → DISABLED (fail-safe default).** Every BBL
  (including the control `1008350041`) returns `spatial_intersection_absent` /
  `professional_review_required` fast, with no district and **no `connector_error` log line**. This
  is one code-contract-consistent candidate for the captured signature — **not ranked above** a
  shared connector/network failure. Fix: set it to `1`, save, let Render restart, run the probes.
- **Reading = `1` / `true` / `yes` / `on` → ENABLED.** A successful connector request is **not by
  itself** a real district — the live path still returns `spatial_intersection_absent` when the data
  is not valid/sufficient (empty official assignment, transfer-limited page) or the engine cannot
  confidently compose a single-district substrate. A real district appears only when connectors
  succeed AND return sufficient data AND the engine composes a confident substrate; a failing parcel
  returns `spatial_intersection_absent` AND emits a typed `connector_error` line. If **all** parcels
  (incl. the control) are still uniformly absent while this reads true, the **disabled-flag branch
  is excluded for the observed runtime**; the remaining cause is **not established from absence
  alone** — confirm it only from correlated typed evidence, never inferred from the uniform absence.

Preserved caveats (unchanged): the historical cause stays UNCONFIRMED until the captured deployment
(`f0e7d82f`) is paired with its own env reading; reading the current flag does not retroactively
rule the flag in/out as the historical cause; and **absence of a connector-error log does NOT by
itself prove flag-off** (it can be missing for several distinct reasons).

## 3. Acceptance-scenario mapping (AS-1 .. AS-7)

- **AS-1 (flag-unset → uniform absent for every BBL).** Provider:
  `tests/spatial/test_live_provider.py::test_m5t033_flag_off_absent_for_every_bbl_zero_calls_no_log`
  (parametrized on both D-059 BBLs), `::test_s1_default_off_returns_none_without_any_connector_call`.
  Route end-to-end: `tests/api/test_rule_evaluation_api.py::test_m5t033_flag_off_uniform_absent_zero_connector_calls`,
  `::test_m2t020_s1_flag_off_default_seam_matches_absent_substrate_byte_for_byte`. Evaluator:
  `tests/rules/test_rules_integration.py::test_m5t033_absent_substrate_uniform_spatial_intersection_absent`
  (both D-059 BBLs), `::test_ri_s3_absent_spatial_intersection_fails_safe`.
- **AS-2 (flag-on + injected connector failure → typed per-parcel fail-safe, distinct signature).**
  Provider: `test_live_provider.py::test_m5t033_flag_on_connector_failure_absent_but_calls_and_logs`
  (both BBLs), `::test_s3_any_connector_failure_yields_absent_substrate`. Route:
  `test_rule_evaluation_api.py::test_m5t033_flag_on_connector_failure_same_reason_but_connector_consulted`,
  `::test_m2t020_s3_live_connector_failure_is_absent_substrate_fail_safe`. Distinctness proven by
  recorded connector calls + exactly one payload-only `connector_error` log line (never the canary
  text).
- **AS-3 (both D-059 parcels exercised; no test claims the live cause is confirmed).** Parcels
  `3052960043` and `3022647515` are parametrized at the provider and evaluator levels; the counter-
  example `::test_m5t033_shared_connector_failure_is_uniform_absent_flag_on` exercises them + the
  control. Every M5-T033 test asserts code behavior only; §1/§5 here separate reproduced behavior
  from the pending owner check.
- **AS-4 (report states one causal account; owner check is the single remaining confirmation; no
  claim M4-T020/B4 alone fixes it).** §1 + §2 above; the "M4-T020/B4 does not fix it" statement is
  in checklist §6b and §1 here.
- **AS-5 (checklist names both flags with fail-safe defaults, setting location, post-restart
  probe; existing content preserved).** §6a names `LIVE_SPATIAL_PROVIDER_ENABLED` and
  `INTERNAL_SCENARIO_ENABLED` (absent = disabled), where to set them, and §6b post-restart probes.
  This revision changed only §6b wording; §0–§10 and all prior content preserved.
- **AS-6 (ruff + documented python checks; api CI green at seam).** See §4. ruff PASS, modularity 0
  failures (local); rules pytest = exit-2 collection failure (invocation-environment; §4); the
  authoritative api-suite PASS is the api CI job on the pushed head (orchestrator seam).
- **AS-7 (orchestrator-captured at the seam).** The audited D-066-R003 per-unit wall-time / context-
  token comparison vs M5-T032 and the Codex D-066-R002 graph accuracy/usefulness statement are
  recorded by the orchestrator at the seam, not self-measured here. See §6.

## 4. Validation results (exact)

- `python -m ruff check services/api` → **PASS** ("All checks passed!"), producer-run locally
  (api CI job's first step).
- `python tools/modularity_check.py --check` → **0 failures**, 18 pre-existing warnings, none in the
  edited files (`live_provider.py`, `rule_evaluation.py`, `integration.py`). Producer-run locally;
  consistent with the supervisor's modularity pass (recorded as a supervisor result).
- `python tools/validate_directive_compliance.py --check` → **PASS**, recorded as a **supervisor
  result** (the supervisor loop runs the validator each unit; not re-run here).
- `python -m pytest services/api/tests/rules -q` → **exit 2, 15 collection errors**
  (`ModuleNotFoundError: No module named 'app'`). RETAINED as-is: the documented command runs from
  the worktree root, so the `app` package under `services/api` is not importable; this is an
  invocation-environment artifact (thin client), not a test defect. The authoritative rules-suite
  PASS is the api CI job (runs from `services/api`) — left to the orchestrator seam.
- `python -m pytest services/api/tests/spatial -q` and
  `python -m pytest services/api/tests/api/test_rule_evaluation_api.py -q` share the same
  from-root `No module named 'app'` collection limitation locally; their authoritative PASS is the
  api CI job at the pushed head (orchestrator seam). Not run to green locally per thin-client policy.

## 5. Explicit unresolved runtime confirmation

The live runtime cause remains **UNCONFIRMED**. Every M5-T033 test proves reproduced code behavior
only; none asserts the deployed cause. Runtime confirmation requires the owner dashboard reading of
`LIVE_SPATIAL_PROVIDER_ENABLED` (owner-visible only) for the captured deployment `f0e7d82f`, plus —
if the flag reads true — the correlated typed `connector_error` logs. No confirmed deployed cause is
claimed from response uniformity or latency.

## 6. Code-graph usefulness (D-066)

The navigation block (D-066-R001) was **useful for navigation**: it pointed to the dependency and
consumer set for `live_provider.py` and named `integration.py:81` as the definition of
`FAILSAFE_SPATIAL_ABSENT`. The specific claims I relied on were corroborated in actual source
(`integration.py:81` defines `FAILSAFE_SPATIAL_ABSENT`; `rule_evaluation.py` imports
`default_live_substrate`; the two named test modules import the provider). Beyond those spot
checks, the graph's overall **accuracy is UNVERIFIED** here (node/edge totals not independently
audited); the authoritative D-066-R002 statement on graph accuracy/usefulness is the Codex
reviewer's, recorded at the orchestrator seam.

**This revision review's graph statement (recorded per D-066):** the navigation block was **useful
navigation guidance**; its **accuracy is unverified from this packet** — only the spot-checked
node/edge claims above were corroborated in source, and node/edge totals were not independently
audited here.

## 7. The two corrected production comments (behavior-neutral)

Comment-only edits; no code path, signature, token set, or contract changed (ruff PASS, modularity 0
failures confirm no structural change):

1. `services/api/app/spatial/live_provider.py` (env-var declaration comment). The old text asserted
   the flag was "unset by default on every deployed service" — a runtime/deployment claim the module
   cannot make (the value is environment-scoped and owner-visible only; the owner may set it). New
   text states the CODE default only (absent/empty/unknown → DISABLED) and explicitly does not assert
   what any deployed service currently carries. Verified against `live_spatial_provider_enabled()`.
2. `services/api/app/api/v1/rule_evaluation.py` (default-provider seam comment). The old text (a) said
   the flag was "unset (the default everywhere, including CI)" and (b) that with the flag on "the
   accepted connectors + M2-T013 engine compose a real substrate" — conflating a successful connector
   request with valid, sufficient spatial data and successful substrate composition. New text (a)
   scopes the default claim to the code default / CI (not "everywhere"), and (b) distinguishes the
   three: a successful connector request is not by itself sufficient data, and composition can still
   yield `None` (empty assignment, transfer-limited page, connector error) — a real substrate results
   only when connectors succeed AND return sufficient data AND the engine composes a confident record.
   Verified against `build_live_substrate()` / `default_live_substrate()` behavior.

`services/api/app/rules/integration.py` is in allowed_paths but needed no change (its
`FAILSAFE_SPATIAL_ABSENT` comment/definition at line 81 is accurate).

## 8. Checklist changes (docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md §6b)

- Removed the unsupported "most likely" ranking from the DISABLED row — now one code-contract-
  consistent candidate, **not ranked above** a shared connector/network failure; the flag reading +
  typed logs (not the response signature) discriminate.
- ENABLED row: distinguished a successful connector request from valid/sufficient data and successful
  substrate composition; and for continued absence with the flag enabled, states the disabled-flag
  branch is excluded for the observed runtime while the remaining cause requires correlated typed
  evidence — removed the old "this is a connector/network problem" inference from absence.
- "Does NOT disprove an earlier disabled flag" paragraph (this pass): removed the claim that continued
  absence after enabling **establishes** a second, separate connector problem ("both can be true at
  once"). It now states only that the disabled-flag branch is excluded for the observed runtime, and
  that the remaining enabled-path cause — a connector/network failure OR a data-sufficiency OR a
  substrate-composition failure — is established solely from correlated typed evidence, never inferred
  from the uniform absence. The historical-deployment caveat (`f0e7d82f`) is preserved verbatim inside
  that same paragraph.
- Post-restart probe #1: same correction (no inferring a connector problem from an absent body) and
  tightened "connectors healthy" → "connectors succeed and return sufficient data".
- Preserved unchanged: the historical-deployment caveat (`f0e7d82f`), the "absence of a
  connector-error log does NOT prove flag-off" warning, §6a flag names/defaults, and all other
  sections.

## 9. Changed-file inventory (checkpoint reconciliation)

1. `docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md` — §6b wording corrections (this pass).
2. `services/api/app/spatial/live_provider.py` — production comment #1 (this pass).
3. `services/api/app/api/v1/rule_evaluation.py` — production comment #2 (this pass).
4. `services/api/tests/spatial/test_live_provider.py` — M5-T033 provider reproduction tests + framing.
5. `services/api/tests/api/test_rule_evaluation_api.py` — M5-T033 route reproduction tests + framing.
6. `services/api/tests/rules/test_rules_integration.py` — M5-T033 evaluator reproduction test
   (explicitly included in the inventory).
7. `project-control/reports/M5-T033-producer-report.md` — this report.

## 10. Orchestrator-seam items (not producer authority)

- api CI job green on the pushed head = authoritative api/rules-suite evidence (AS-6).
- D-066-R003 audited per-unit wall-time / context-token comparison vs M5-T032 (AS-7).
- Codex D-066-R002 graph accuracy/usefulness statement (AS-7).
- D-066-R003 capture and successful rules/API CI packaging — no out-of-scope packaging changed here.
- Next bounded evidence packet must expose: the complete changed test hunks and this report, plus the
  relevant `live_provider.py` / `rule_evaluation.py` / `integration.py` and live-capture excerpts that
  support the runtime and probe claims.
