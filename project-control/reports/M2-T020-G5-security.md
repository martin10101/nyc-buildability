# G5 Security Gate Report - M2-T020

- Reviewed SHA (frozen HEAD): bc106d8d; candidate content commit f12e828c; branch candidate/D-024-mrl-option-b
- Reviewer: security-reviewer (independent, read-only)
- Verdict: PASS (no critical/high/medium findings; two low/informational for the production-enablement follow-up)

## Reproduction (all green)
46 passed (new suites), 43 passed (accepted spatial suite, no regression); ruff clean; modularity failures 0; import-cycle: only rule_evaluation.py imports live_provider - no cycle; commit touches 5 files only, no requirements/pyproject/lock - no new dependency.

## Surfaces (all PASS)
1. Enable flag: server-side env only (live_provider.py:70-78), closed true-token set; route accepts only the bbl path param - no request influence path; absent/unknown -> disabled.
2. Outbound/SSRF: hardcoded (layer, field) constants; query value from server-side official ZTLDB assignment, never the request; connectors build URLs from pinned roots with layer/field allowlists, character allowlist + quote-doubling, where-clause reproducibility guard, quote(safe='') encoding; BBL normalize-validated at route AND inside each connector (defense in depth).
3. Error handling: fail-safe boundary returns None on any exception; logs event + type(exc).__name__ + correlation_id, never str(exc) (M1-T002 G5 F5 policy); exception canary absent from BOTH log and response body (tested); fail-safe 200, never 500; X-Correlation-ID end-to-end.
4. Resource exhaustion: one bounded page per district (result_record_count=2000, offset 0); exceeded_transfer_limit fail-safes and stops; district count bounded by deduped server-side ZTLDB data (not requester-inflatable); per-call retry cap 3 + timeout 30s.
5. Dependencies: stdlib + existing repo modules only; no manifest file touched.
6. Provenance/injection: external data flows only through typed models into the accepted M2-T013 engine; LotIntersectionRecord returned unmodified; district values re-validated by character allowlist before querying; document schema-validated before send; review/conflict/uncertain classes pass through un-collapsed.
7. Default-off: flag unset returns None before any fetcher touch; zero connector calls asserted; byte-for-byte parity; endpoint additionally gated by INTERNAL_RULE_EVAL_ENABLED (doubly gated off in production).

## Low/informational (non-blocking)
- L1: no shared per-analysis AnalysisBudget threaded across the composed calls (each independently bounded; total work bounded + not attacker-controllable); wire a global budget + tighter timeouts at production enablement; query_features(metadata=None) re-fetches metadata per district (efficiency note).
- L2: production enablement of LIVE_SPATIAL_PROVIDER_ENABLED must pair with the open auth work (M0-T007/T008); default-OFF + internal flag keeps this safe today.

Recommended gate result: PASS at reviewed SHA bc106d8d.
