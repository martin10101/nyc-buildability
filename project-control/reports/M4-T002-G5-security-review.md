# M4-T002 — G5 security-reviewer verbatim return (frozen SHA 609efe9)

VERDICT: PASS (non-blocking hardening LOW-1/LOW-2/INFO-3/INFO-4; recommended before future endpoint exposure)

---

# Gate Report — G5 Security & Privacy

- **Gate ID:** G5 (security & privacy)
- **Task ID:** M4-T002 (rules-engine ↔ property-analysis integration, service layer)
- **Reviewer:** security-reviewer (independent, read-only)
- **Producer:** orchestrator (lead-only)
- **Result:** PASS (with non-blocking hardening recommendations for the future endpoint-exposure task)
- **Clean worktree / frozen SHA:** worktree @ `609efe917ebfcedc3e0512bab5c4ed2b82e445b0`; base range `883fee0..609efe9`.

## Scope confirmation
`git diff --name-status 883fee0..609efe9` = exactly three ADDED paths, zero modifications: integration.py (555), test_rules_integration.py (511), M4-T002-producer-report.md (149). No auth/RLS/migration/storage/endpoint/worker/contract/config surface. app/profile/** and app/spatial/** unmodified. Purely additive, in-process; no HTTP/DB/storage/upload/secret/network sink.

## Commands run (read-only)
1. git rev-parse HEAD → 609efe9…; diff = 3 files all `A`.
2. pytest tests/rules/test_rules_integration.py -q → 23 passed in 0.31s.
3. pytest -q (full api) → 649 passed in 5.11s (no regression).
4. grep for eval(/exec(/__import__/importlib/open(/os./sys./subprocess/requests/httpx/urllib/socket/environ/getenv/logging/print(/.write(/pickle/yaml.load/format( on integration.py → NO matches. Imports: stdlib dataclasses/typing + internal app.rules only.
5. Untrusted-input probe (13 hostile profiles via python stdin, no repo write):
```
[OK]    baseline confident R5: coverage='conditional' fail_safe=False n_evals=1
[RAISE] pairs=999 (truthy non-iterable): TypeError: 'int' object is not iterable
[RAISE] review_reasons=5 (non-iterable): TypeError
[RAISE] notes=5 (non-iterable): TypeError
[RAISE] provenance_refs=5 (non-iterable): TypeError
[OK]    area=+inf: coverage='conditional' -> outputs max_residential_floor_area_sq_ft: inf
[OK]    area=nan: coverage='professional_review_required' (NaN -> missing-critical, safe)
[OK]    pair entries non-dict [1,2,3]: professional_review_required fail_safe=True n_evals=0
[OK]    extra unknown keys: coverage='conditional' (ignored, safe)
[RAISE] non-dict profile (list): AttributeError: 'list' object has no attribute 'get'
[OK]    empty profile {}: professional_review_required fail_safe=True
[OK]    spatial not dict: professional_review_required fail_safe=True
[OK]    bbl hostile type list: professional_review_required fail_safe=True
[OK]    hostile district "R5'; DROP TABLE t;--": coverage='not_applicable' (inert data, no injection)
```

## DRAFT-NOT-VERIFIED property — HOLDS under six independent barriers
- A — Registry can hold only drafts: DSL loader assert_agent_authorable rejects any status beyond needs_review; R5 rule is needs_review.
- B — No G6 approval ever passed: integration calls registry.evaluate WITHOUT g6_approval (defaults None); evaluator sets verified only for published rule WITH matching G6Approval.
- C — most_severe is downgrade-only: verified is lowest severity; returns highest severity present.
- D — Empty-list guard load-bearing: `if applicable_coverages:` guards the most_severe()→verified default; empty routes to not_applicable.
- E — Fail-closed guard on whole payload: assert_not_verified checks top-level + every trace + family_coverage; runs at construction (:539) and in export() (:158).
- F — Field vs text: guard tests only coverage_status FIELDS; disclaimer text ("Verified") is under not_verified_disclaimer, never a status. Confirmed by RI-S7 + recursive _iter_coverage_values sweep.

## Provenance fail-closed — holds
Computed values enter only via trace = result.export(); RuleResult.export() raises ProvenanceError if a citation lacks resolvable content_digest_sha256. Integration never reads result.outputs/result.trace directly. zoning_district/lot_area are inputs (read-only from profile), surfaced in input_provenance.

## Untrusted-input — no eval/exec/dynamic-import/format injection; hostile district string treated as data → not_applicable, no computation. NaN/-inf/non-dict pair/missing/extra keys/empty/absent spatial/hostile bbl all fail safe.

## Least privilege / supply chain — clean
No new dependency/network/secret/filesystem-write/env. app.rules gains NO runtime dependency on app.spatial (constants duplicated with a real green drift guard). Registry/snapshot reads are read-only.

## Info leak / logging — none. No logging/print/stderr; payload carries only public zoning/geometry facts + provenance refs; bbl is public.

## Broader checklist — cross-tenant/secrets/storage/SSRF/prompt-injection/log-redaction all N/A for this in-process no-endpoint slice.

## Findings by severity
CRITICAL/HIGH/MEDIUM: none.
- **LOW-1** — Unhandled TypeError on malformed spatial container sub-fields (fail-safe deviation). integration.py:199-203 (_base_pairs `for pair in (spatial.get("pairs") or [])`), :224-225 (review_reasons/notes list()), :281 (provenance_refs), via _preserve_uncertainty at :405. A truthy non-iterable scalar (e.g. {"pairs":999}) raises TypeError propagating out of evaluate_property — contradicts the "malformed dicts fail safe" claim. Impact: robustness only; no leak; fails closed (no wrong/Verified answer); not attacker-reachable in this no-endpoint slice (trusted in-process producer always emits lists). Remediation: isinstance-list coercion in _base_pairs/_preserve_uncertainty/_input_provenance + a test.
- **LOW-2** — Positive-infinity lot_area propagates to inf output. _positive_number admits float("inf") (value>0); yields max_residential_floor_area_sq_ft: inf. NaN/-inf correctly rejected. Impact: data-quality only (draft/conditional, no crash); inf not valid strict JSON. Remediation: require math.isfinite in _positive_number.
- **INFO-3** — Non-dict profile arg raises AttributeError (caller-contract violation vs dict type hint). Optional early isinstance guard.
- **INFO-4** — Vestigial field verified_status_present (:126, serialized :151) never set True/read; harmless dead field. Remove or wire.
Defense-in-depth (no action): (a) `if applicable_coverages:` guard present + backstopped by :539 assert; (b) fail-safe returns hardcode non-verified + re-checked by export(); (c) assert_not_verified checks each trace's direct coverage_status (complete for this payload; recursive would be stronger for arbitrary foreign payloads).

## Conclusion
Draft-never-Verified holds under six barriers + fail-closed guards + export() re-check. Provenance fail-closed; no injection/new dependency/network/secret/filesystem/env/app.spatial-coupling/logging. Scope = 3 allowed additive files, no regression (649 passed). Only LOW/INFO robustness items, no security/privacy impact in this in-process no-endpoint slice; non-blocking here but SHOULD be tracked and fixed before the future property-analysis endpoint/UI exposure — specifically LOW-1 (isinstance-list guards) and LOW-2 (math.isfinite).

VERDICT: PASS
