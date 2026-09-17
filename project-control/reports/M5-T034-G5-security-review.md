# M5-T034 G5 security review (verbatim reviewer return; security-reviewer, read-only, pinned 22724f02)

Saved verbatim by the orchestrator per the report-preservation rule.

---

## G5 SECURITY REVIEW — M5-T034 — VERDICT: PASS

**Repo pinned at** `22724f02171826cac711270b67309327bb540e7c` (verified == HEAD). Diff reviewed: `git diff fd9c644c..ae478563`. Read-only static + logic review; test *execution* proof is CI's surface (thin-client, shapely-heavy) — code logic and test presence verified here.

### Verification of the six required properties

**(1) Wide-street determination can NEVER be browser/caller-supplied — PASS.**
`rule_evaluation.py:159-161` (WideStreetDeterminationProvider = `Callable[[str,str], "WideStreetDetermination | None"]`), `:_default_wide_street_determination` returns `None`, injected via `Depends(get_wide_street_determination_provider)` (`:200-202`). Called at `:324` as `wide_street_provider(normalized.canonical, correlation_id)` — both args are server-side (normalized BBL from the path param, server-generated uuid). A FastAPI parameter defaulted with `Depends()` is resolved by the dependency, never bound from query/body, so no request field reaches it. Return type is the concrete forward-referenced `WideStreetDetermination` (not `object`) — a provider can only ever supply a real typed determination or `None`. Trusted default is byte-identical to prior behavior.

**(2) Input bounds are a genuine DoS guard, before linework/buffer, non-finite-safe — PASS.**
`wide_street_buffer_engine.py`: `_check_segment_count` (`:816`) runs before the per-segment loop; inside the loop the cheap `_check_segment_vertex_counts` (reads raw `polyline.paths`, `:824`) runs BEFORE `_segment_linework`, and `_check_linework_extent` runs AFTER linework but BEFORE `linework.buffer(...)` (`:826-828`). `_check_lot_bounds` (`:754`) runs before any buffer/intersects use of the lot. All raise typed `InputBoundsError` (subclass of `WideStreetBufferEngineError`, `error_type="input_bounds_exceeded"`) with no partial compute. Non-finite bypass is closed: `_extent_within_bound` uses `all(abs(v) <= EXTENT_ABS_MAX_FT for v in bounds)` — `abs(±inf) <= 5e6` is False and any NaN comparison is False, so inf/NaN in `.bounds` are rejected before buffering. Tests at/beyond every bound plus CRS-gate-wins ordering present (`test_wide_street_buffer_engine.py:957-1066`).

**(3) No hostile-text echo — PASS.**
Notices/labels (`DRAFT_LABEL_NOTICE`, `ROUTED_TO_NOT_USED_NOTICE`, `FALLBACK_DIRECTION_NOTICE`, determination `reason` strings) are module constants or server-constructed prose interpolating only typed fields (counts, `decision_state` from a fixed vocab, `exc.error_type`/`exc.message` built from server geometry data, FAR floats from the rule's own params). The D-052 provenance quintuple with free-text (`original_labels`, `classification_reasons`, `interpreted_bounds_summaries`) lives ONLY in `_wide_street_summary` → `PropertyRuleEvaluation.wide_street_determination`, which is DELIBERATELY excluded from `as_dict()` (`integration.py:158-182`) and thus never serialized to the response. Endpoint logs (`rule_evaluation.py:220/241/259/299/337/357`) emit only typed fields (code, error_type, location, stage, correlation_id); the determination and its provenance are never logged.

**(4) No new external hosts/network in tests — PASS.**
`https://example.invalid/dcm-page` (RFC-6761 reserved, non-resolving) appears only as an in-memory `DcmTransport(url=..., body=<constructed JSON>)` fed to `parse_segment_geometry_page` (`test_wide_street_wiring.py:146-152`, `test_wide_street_buffer_engine.py:518-522`). No `requests`/`httpx`/`urlopen`/`socket` imports or fetches; the URL is stored as a provenance field only. `epsg.io/2263` appears once as a citation-string comment. Inert.

**(5) Fail-safe direction (uncertainty never grants the higher FAR) — PASS.**
Rule JSON confirms wide > standard for all four districts (R6 3.0>2.2; R7-1/R7-2 4.0>3.44; R8 7.2>6.02). `select_far_row_value` returns the wide (higher) value ONLY for `FAR_ROW_WIDE_STREET` (affirmative WITHIN), standard for `FAR_ROW_STANDARD`, else `None`. Every uncertainty path in `determine_wide_street_far` (empty decisions, any non-{wide,narrow} `decision_state`, named-street-override pending, any `WideStreetBufferEngineError`, non-computed buffer status) returns `FAR_ROW_NONE` + `professional_review_required`. `integration.select_conditional_far_row` escalates coverage via `cov.most_severe(..., PROFESSIONAL_REVIEW_REQUIRED)` and sets `governing_far=None` when `coverage_hint==PRR or governing is None`. Routing keyed off `decision_state`, never `routed_to` (G3 A4). The rule's own DSL still returns only the conservative value; the higher value is byte-checked from the rule's `wide_street_far_by_district` param, never invented.

**(6) No secrets — PASS.** Diff scan of `services/api/app` + `tests` for secret/key/token/password/BEGIN/service_role patterns returned nothing; provider default is `None`.

### Findings (all non-blocking, defense-in-depth for the future request path)

1. **LOW — `wide_street_buffer_engine.py:641,754`**: lot-polygon vertex count is not bounded before shapely construction (`_lot_shapely` builds the geometry; `_check_lot_bounds` checks extent/finiteness only, after construction). Acceptable now: the lot is server-derived MapPLUTO and is never buffered (only `.intersects`), so no O(vertices) buffer work rides on it. Remediation (optional follow-up): add a cheap lot vertex-count ceiling mirroring `_check_segment_vertex_counts` before `_lot_shapely`.

2. **LOW — `wide_street_buffer_engine.py:613`**: `MAX_WIDE_SEGMENTS` (512) bounds segment count and `MAX_VERTICES_PER_PATH` (5000) bounds per-path vertices, but the number of *paths per polyline* is unbounded, so `_segment_linework` can build an arbitrarily large `MultiLineString` (many paths) before `.buffer`. Acceptable now: segments are server-derived from a single DCM parse and count-capped; real centerline segments carry ~1 path. Remediation (optional follow-up): cap total vertices (or path count) per segment, not just per path.

### Notes
- No explicit NaN/inf unit test exists, but the `all(abs(v) <= ...)` guard provably rejects both; not a defect.
- Modularity: `wide_street_wiring.py` 500 SLOC (under warn). `wide_street_buffer_engine.py` 890 and `integration.py` 843 sit above the 750 justify threshold but under the 1000 hard cap; both are pre-existing cohesive domain modules and the additions stay on-responsibility (bounds guard; conditional-FAR fold). Not a security finding — CI `modularity_check` governs.

**VERDICT: PASS.** Findings 1–2 are LOW defense-in-depth items suitable for a follow-up task, not gate blockers.
