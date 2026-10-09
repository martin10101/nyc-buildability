# M5-T107 — G5 DELTA re-review, rework round 2 (security-reviewer "sec-t107", read-only)

> Transmission history: pinned at bf504772 (delta = 2c52ac6d, identity a367f548), delivered as two SendMessage parts
> (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: F-1 (blocking) closed and probe-verified on every coordinate path; F-2..F-4 closed. A new LOW
> residual (the context refusal.message is truncated but not HTML-escaped; the connector only emits fixed strings there) is
> routed at the accept seam.

---

M5-T107 G5 DELTA RE-REVIEW (read-only, sec-3d) — PART 1/2

PIN: HEAD bf504772 (matches expected). Frozen identity a367f548. Delta = exactly `git show 2c52ac6d` (cherry-pick of wt-m5t107 2bcc3c42): scene_assembler.py, scene_api.py, 3 test files, report r2 — connector production files unchanged. Both source files BYTE-IDENTICAL 2c52ac6d→HEAD (empty diff). Method: clean-diff read of the delta + in-memory hostile probes (TestClient flag-on in-process, connector fakes, no network) from services/api, Py3.11. Green at HEAD: ruff clean (both files); pytest test_scene_assembler + test_scene_api + test_building_footprints_arcgis = 193 passed (was 180). Zero new deps (only new imports are HEIGHT_REFERENCE/HEIGHT_UNIT_BASIS from the connector). scene_assembler.py 594 SLOC (< 600 warn); modularity_check flags only unrelated tools/* files.

F-1 (was BLOCKING) — CLOSED. scene_assembler.py:243-251 _coerce_coordinate now wraps float() in try/except OverflowError → returns None → the existing typed unparseable_coordinate refusal. Every coordinate path funnels through this one function (lot_ring, proposed_massing outline, levels, generated_option candidate — all via parse_ring), so the single guard covers them all. Probes:
- _coerce_coordinate(10**400) → None; (-10**400) → None.
- route huge-int LOT vertex → 422 validation_error (was 500).
- route huge-int OUTLINE vertex → 422 (was 500).
- connector numeric params: _validate_inputs(10**400 site_ground) → typed DisallowedRequestError (via _finite's own OverflowError guard, confirmed in building_footprints_geometry.py); _check_page_size(10**400) → typed DisallowedRequestError.
Note (not a regression): huge-int height_ft → 200 (the massing model keeps it an int; NO untyped 500). Range-acceptance of an absurd height is massing-domain (M5-T106, massing_model.py — forbidden path here), not a route-safety failure; the route contract "no untyped 500 from caller input" holds.

F-2 (ADVISORY) — CLOSED. New _escape_untrusted_mapping (scene_assembler.py:383-391) escapes both KEYS and string VALUES; gaps→_escape_untrusted_mapping, drift_signals + geometry_findings → per-item _escape_untrusted. Probe with a hostile attribute key "<img … onerror=…>", value "<b>", gap.raw "'<script>…'", finding "<svg onload=…>", drift "unknown_attribute:'<script>…'": ALL returned HTML-entity-encoded (&lt;/&gt;/&#x27;), NO raw '<' or '>' remains in any field. Docstring + the untrusted_source_text_escaped disclosure corrected to name exactly these fields (now true).

(continues 2/2)

---

M5-T107 G5 DELTA — PART 2/2 — F-3/F-4, new-in-delta, residual, VERDICT

F-3 (ADVISORY) — CLOSED. SCENE_RATE_LIMIT_MAX_KEYS=4096 ceiling added; _rate_limit_allows pops a caller's key when its window empties, and a new caller at the ceiling triggers _evict_empty_keys then fail-closed refusal. Probe (MAX_KEYS tightened to 10): 50 distinct hosts → dict bounded to 10, 40 refused (fail-closed); after the window expires a newcomer IS admitted and the dict shrinks to 1 — memory-bounded AND not a permanent lockout.

F-4 (ADVISORY) — CLOSED. Module + SCENE_MAX_SECONDS docstrings now state the truth: the awaited job is cancelled and a typed 504 returns with no partial scene, but the worker THREAD cannot be force-killed and runs to completion, bounded by the connector's own wall-clock deadline + interactive single-attempt + byte/vertex caps. Accurate.

NEW-IN-DELTA verified (no regression):
- non-dict context → typed 422 field=context; context=None/absent → honest not_requested (200). Probes: "oops"→422, 123→422, None→200.
- ground_status_is_authoritative disclosure added (informational; correct — base_z_grounded can be true while ground is zero/unverified).
- HEIGHT_PROVENANCE threads the connector's pinned HEIGHT_UNIT_BASIS + HEIGHT_REFERENCE constants into the layer (pinned strings, not upstream text — safe).

RESIDUAL (NEW, LOW / ADVISORY, non-blocking): refusal.message is emitted via _bounded (truncate only, NOT html-escaped) in _context_refusal_block (scene_assembler.py ~426). NOT exploitable today: the connector only ever puts FIXED strings in .message (verified — UpstreamError message is a fixed string at building_footprints_arcgis.py:665; the upstream ArcGIS code/message go to `detail`, which the scene refusal block does not emit; the block's other fields are pinned enum / connector-built URL / sha256 / rfc3339 / server correlation-id). It is a defense-in-depth inconsistency only: every other connector-sourced string is now escaped at the assembler boundary, but refusal.message relies on connector discipline. Recommend escaping it too (or a comment pinning the "message is always fixed" contract). Does NOT block.

SCOPE/HEALTH: delta touched exactly the allowed source + tests + report; connector production files untouched; byte-stable to HEAD; ruff clean; 193 passed; zero new deps; sizes/modularity fine.

SUMMARY: all four prior findings (F-1 blocking, F-2/F-3/F-4 advisory) CLOSED and probe-verified. One new LOW/ADVISORY residual (refusal.message escaping), non-blocking. No BLOCKING finding remains.

M5-T107 G5 VERDICT: PASS

END-OF-REPORT
