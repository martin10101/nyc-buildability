# M5-T033 G1 source review (verbatim reviewer return; data-contract-verifier, read-only, pinned 62dd97cb)

Saved verbatim by the orchestrator per the report-preservation rule.

---

# G1 GATE REPORT — M5-T033 (data-contract-verifier)

**Verdict: PASS**

Review pinned at HEAD `62dd97cb` (verified via `git rev-parse HEAD`). Material commit `00be16d3`. Read-only; no ledger/git-write commands run.

## Scope verified
Root-cause diagnosis of deployed uniform `spatial_intersection_absent` (D-059-R004) + deploy-checklist flag coverage. G1 dimension here is the typed-log / flag / fail-safe contract (not a new external connector), plus epistemic bounding of the live capture.

## Findings (all confirming; file:line)

1. **Typed log events faithful.** `connector_error`, `no_candidate_districts`, `district_page_partial` are all emitted exactly as the report/checklist describe — `live_provider.py:214` (`no_candidate_districts`), `:227` (`district_page_partial`), `:236` (`connector_error`, in the fail-safe `except Exception` boundary at `:232-237`). Report §1 Branches A/B and the "not exhaustive" note match source.

2. **`connector_error` log-line format matches the checklist quote byte-for-word.** `live_provider.py:185-190` emits `live_spatial_substrate fail_safe event=%s error_type=%s correlation_id=%s`; checklist `:308` quotes it verbatim. Payload-only (typed `error_type` via `type(exc).__name__`, never `str(exc)`) — confirmed, and tests assert the canary detail never leaks (`test_live_provider.py:480`, `:535`; `test_rule_evaluation_api.py:1019`).

3. **Flag token set correct.** `_TRUE_TOKENS = {"1","true","yes","on"}` (`live_provider.py:69`); absent/empty/unknown → `False` (`:78-80`); flag-off → `None` with zero connector calls (`default_live_substrate` `:245-249`). Checklist §6a `:258-259` states the same tokens and fail-safe default. Faithful.

4. **`FAILSAFE_SPATIAL_ABSENT` corroborated.** `integration.py:81` = `"spatial_intersection_absent"`, consumed at `:477` as `fail_safe_reason`. Navigation-block claim (`integration.py:81`) accurate.

5. **Correlation-id mapping accurate.** Route sets `X-Correlation-ID` (`rule_evaluation.py:115`); AS-2 route test asserts the recorded connector call carries the same id the response advertises (`test_rule_evaluation_api.py:1017-1018`). Checklist §6b `:310` "match `correlation_id` to `X-Correlation-ID`" is real.

6. **Production edits are behavior-neutral (comment-only).** `git show 00be16d3` on `live_provider.py` (6 lines) and `rule_evaluation.py` (15 lines) touches only comment text; no code path, signature, token set, or contract changed. Notably, comment-fix #1 *removed* the pre-existing overclaim "unset by default on every deployed service" — the module no longer asserts a deployed value. ruff PASS and modularity 0-failures (report §4) consistent.

7. **Checklist preserves prior content.** `git show --numstat` = **124 insertions / 0 deletions**; §6a/§6b are additive. Names both `LIVE_SPATIAL_PROVIDER_ENABLED` and `INTERNAL_SCENARIO_ENABLED`, fail-safe default (absent = disabled), where to set (`nycdf-api → Environment`), and post-restart probes (§6b `:339-364`). AS-5 satisfied.

8. **Scenario-flag citations accurate.** `config.py:34` `INTERNAL_SCENARIO_ENABLED_ENV_VAR`, `:60-66` `internal_scenario_enabled`; `scenario.py:160` route + `:174` guard. Checklist §6a item 2 matches source.

9. **Live capture correctly bounded — no residual overclaim.** Report keeps runtime cause UNCONFIRMED (§1, §5), treats uniformity/latency as "suggestive, not decisive," and §2 DISABLED reading is "not ranked above" a shared connector/network failure. Checklist §6b encodes the same discipline (decisive = flag reading + correlated typed log; suggestive = body uniformity/latency; absence-of-log ≠ flag-off, `:316-320`). AS-3/AS-4 satisfied. The counterexample test `test_m5t033_shared_connector_failure_is_uniform_absent_flag_on` (`test_live_provider.py:504-535`) *reproduces* uniform-absent-across-a-control with the flag ON — proving in code that uniformity cannot select flag-off. No M4-T020/B4 overclaim (report §1 `:49`; checklist `:366-368`). Three-round Codex bounding is reflected in the final state.

10. **Tests prove the two distinct signatures (AS-1/AS-2).** All named tests exist and assert the right facts: flag-off → uniform absent, zero calls, no log (`test_live_provider.py:442`; route `test_rule_evaluation_api.py:953-983`; evaluator both parcels `test_rules_integration.py:359-375`); flag-on + injected failure → same 200 body reason but recorded connector call + exactly one `connector_error` line (`test_live_provider.py:461`; route `:986-1019`). Both D-059 parcels (`3052960043`, `3022647515`) parametrized (`_D059_BBLS`, `test_live_provider.py:438`).

## Standing-licence check (consumers just outside the packet)
Both changed production modules are comment-only, so no consumer behavior changed; the depth-2 consumers named in the navigation block (`evidence.py`, `scenario.py`, `scenario_analysis.py`) consume the unchanged substrate-provider seam. New coverage spans all three levels of the failure chain (provider → route → evaluator). No coverage gap.

## Non-blocking observation (not a defect)
The immutable input artifact `M5-T033-live-capture.md:27` still quotes the *pre-correction* comment ("unset by default on every deployed service"). It is orchestrator INPUT evidence (timestamped capture, outside `allowed_paths`, explicitly labeled "not a conclusion"), and the producer's deliverables correctly do not adopt it — in fact comment-fix #1 removed that very wording from source. Acceptable provenance; noted only for the record.

## Items deferred to orchestrator seam (not G1-blocking)
AS-6 api CI green at pushed head, AS-7 D-066-R003 wall-time/token comparison and Codex D-066-R002 graph statement — captured in `M5-T033-orchestrator-seam-evidence.md` and `M5-T033-graph-comparison.md`; local pytest-from-root `No module named 'app'` is a documented thin-client invocation artifact, CI is the executable authority.

**G1 verdict: PASS.** Connector/typed-log/flag claims are faithful to source; the live capture is used as suggestive evidence only with the runtime cause held UNCONFIRMED pending the owner dashboard read; checklist §6b names both flags with fail-safe defaults, location, and post-restart probes, with all prior sections preserved.
