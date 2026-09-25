# M5-T108 — G5 DELTA re-review, rework round 2 (security-reviewer "sec-t108", read-only)

> Transmission history: pinned at 8273c688 (delta = 5bc472e9, identity 2873d915), delivered as two SendMessage parts
> (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: MEDIUM 1 closed at both the service and the render boundary (no bare 500, no leak). An optional
> note (the pre-render guard omits the sibling's .encode step; not reachable) and LOW 2/LOW 3 are routed.

---

M5-T108 G5 DELTA re-review (READ-ONLY) — Part 1/2. HEAD 8273c688.

Identity verified: reviewed_sha in reports/M5-T108.json = 5bc472e9 (the delta you named). The working-tree blobs match the delta's output blobs (dxf_import.py 124ad72b, dxf_import_api.py eacb56b8), are clean, and 5bc472e9 is their latest touch — so my probes reflect the frozen submission (content_manifest 2873d915 is the manifest digest, not a git object, which is why it doesn't resolve as a commit). Only the 5 allowed files changed; dxf_reader.py untouched; zero new deps (the new imports come from the already-imported dxf_reader).

MEDIUM 1 — CLOSED. Two independent layers, both verified by re-running the 1e300 probe + variants with raise_server_exceptions=True (a bare 500 would RAISE):

Layer 1 (service): _measured_is_finite + the check in list_candidates returns a typed ImportRefusal(reason="coordinate_out_of_range", field="building_outline"); _refusal_response maps it to 422 validation_error (a matrix member) with a correlation id and a bounded, drawing-text-free message. Verified:
- 1e300 quad → 422 (cid) [was 500 in round 1]
- 1e308-per-axis → 422 (cid)
- mixed huge/small ring → 422 (cid)
- nan-producing ring (+inf/−inf shoelace) → 422 (cid) — math.isfinite catches nan too
- service list_candidates directly → ImportRefusal coordinate_out_of_range
- normal ring → 200 (no regression)

Layer 2 (route, defense-in-depth): _guard_finite_response (dxf_import_api.py:192-208) pre-serializes each 200 body with json.dumps(ensure_ascii=False, allow_nan=False) — the same allow_nan setting Starlette renders with — and on ValueError returns the typed _error(500,"internal_error",…) WITH X-Correlation-ID. Verified P8: with the service guard monkeypatched off, a non-finite candidates body → 500 internal_error WITH correlation id, and raise=True did NOT raise (the guard's log line fired) — so no bare Starlette 500 remains even if Layer 1 is bypassed. Applied to BOTH 200 endpoints. /draft was and stays safe (huge ring → 422, field proposed_massing.outline.vertices[0]).

---

M5-T108 G5 DELTA — Part 2/2.

No-leak check on the new guards: _guard_finite_response logs correlation_id only and returns a generic "unexpected internal error" (no body/drawing text); the coordinate_out_of_range detail is fixed text + the candidate index (an int), bounded by _bounded_message. Correlation-id-only logging is preserved. No new information exposure.

Optional (non-blocking) hardening note: _guard_finite_response omits the .encode("utf-8") step the sibling proposal_validation.py includes, so IN ISOLATION it does not catch a lone-surrogate body that Starlette's render (which does .encode) would reject (verified: guard returns None; Starlette render raises UnicodeEncodeError). I checked reachability — it is NOT reachable through the route: query params decode with UTF-8 errors="replace" (author=%ED%A0%80 / low-surrogate / truncated multibyte all decode to U+FFFD → status 200, no surrogate, no 500), and all drawing text is ASCII-only (the reader refuses non-ASCII). So no residual finding; adding .encode("utf-8") would only make Layer 2 fully mirror the sibling. Optional.

Other delta changes reviewed, no security regression: the _select_ring seam (G4 F1) is functionally identical to rings[index][1]; disclosure counts moved from fragile type(p).__name__ strings to isinstance against the reader classes (an improvement) plus a new degenerate_closed_rings disclosure; reader-refusal-detail escaping and exact-ceiling coverage are test additions.

LOW 2 (POST-only 404 indistinguishability once mounted) and LOW 3 (rate-limiter idle-key eviction + proxy-collapse identity) remain PKT-H items, as agreed — not in this delta's scope and not reachable while unmounted.

Baseline (cwd services/api): ruff clean on the 4 target files; pytest tests/drawings/test_dxf_import.py test_dxf_import_api.py → 57 passed (was 41); python tools/modularity_check.py --check → exit 0; dxf_import.py 559 SLOC, dxf_import_api.py 432 SLOC (both under the 600 WARN band).

MEDIUM 1 is closed at both the service and the render boundary — no bare 500, no leak; no critical/high/medium findings remain.

M5-T108 G5 VERDICT: PASS
END-OF-REPORT
