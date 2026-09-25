# M5-T108 — G4 DELTA re-review, rework round 2 (qa-engineer "qa-t108", read-only)

> Transmission history: pinned at 8273c688 (delta = 5bc472e9, identity 2873d915), delivered as two SendMessage parts
> (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: the round-1 survivors (#8-#11) are now caught; four new mutants against the new guards all caught;
> 57 passed three times; the reader/roundtrip suites unchanged.

---

M5-T108 G4 DELTA re-review (qa-engineer, READ-ONLY, in-memory mutation) — PART 1/2

PIN: HEAD = 8273c6881677d9ec83f1e03bc5c63af534180df7 (satisfies "8273c688 or later"). Delta inspected = `git show 5bc472e9` (5 files: the 2 modules + 2 test suites + report; dxf_reader.py and the reader/roundtrip test files NOT touched — verified via --name-only). New seams present on disk: `_select_ring`, `_guard_finite_response`, `_measured_is_finite`.

Baseline: from services/api, the 2 import suites now = 57 passed (was 41); + reader/roundtrip = 118. Reproduced.

METHOD: same as before — each mutation applied PERSISTENTLY to the consuming namespace (not the producer's own test-scoped monkeypatch), then the full 57-test suite run in a fresh process. This independently proves the OTHER tests catch a real regression, not just the in-suite `test_mutation_*`.

MY ORIGINAL FAIL/ADVISORY MUTANTS — all now CAUGHT (were SURVIVED at r1):

| Mutant (consuming namespace) | r1 | r2 | Caught by |
|---|---|---|---|
| `svc._select_ring → rings[0][1]` (always ring 0) | SURVIVED | CAUGHT | test_draft_uses_the_user_assigned_ring (svc+route) |
| `svc._select_ring → largest-area ring` | SURVIVED | CAUGHT | same (ring A is the LARGER, so largest-ring reddens too) |
| `svc._resolve_scale` drops finite/positive guard | SURVIVED | CAUGHT | test_known_dimension_scale_guard_refuses_bad_values |
| `svc._refusal_from_read` skips escaping | SURVIVED | CAUGHT | test_reader_refusal_detail_with_control_char_is_escaped |

F1 (my BLOCKING) is closed: the new `_select_ring` seam is a real seam, and the fixture is well-chosen — `_RING_A` is the LARGER ring at index 0 while the user assigns index 1, so a single test reddens BOTH always-ring-0 and largest-ring regressions. A1/A2/A3 advisories all closed with dedicated refusal/escaping/boundary tests.

Continued in part 2 (new-guard mutants + determinism + verdict).

---

M5-T108 G4 DELTA re-review — PART 2/2

NEW MUTANTS against the reworked guards (all CAUGHT):

| Mutant (consuming namespace) | Guard | Caught by |
|---|---|---|
| `svc._measured_is_finite → True` (drop isfinite guard) | G5 MEDIUM 1 | test_overflow_coordinates_typed_4xx_never_500 (+ service test) |
| `mod._guard_finite_response → None` (drop pre-render guard) | G5 MEDIUM 1 defense-in-depth | test_non_finite_body_becomes_typed_500_with_correlation_id |
| `mod._read_body_within_ceiling` off-by-one (reject exactly-at-limit) | A3 ceiling edge | test_upload_exactly_at_ceiling_accepted_plus_one_refused |
| `svc.LinePrimitive → bogus class` (isinstance disclosure count breaks) | G3 A2 | test_disclosure_counts_line_face_text_by_isinstance |

That is 4 new independent mutants (≥3 requested), each reddening a distinct new guard. Note the pre-render guard is genuinely constrained: it only fires when a non-finite value reaches the body, and the suite proves this by disabling the SERVICE finiteness guard first, then depending on the route's pre-render guard to make a typed (500, internal_error) WITH a correlation id — my `_guard_finite_response→None` mutant makes that test see a bare Starlette 500 (no correlation id) → CAUGHT.

DETERMINISM: 3x full runs of the 2 import suites → 57 passed each (5.0/4.6/4.2s). No deadline/rate-limit wall-clock flakiness.

FORBIDDEN FILES: `tests/drawings/test_dxf_reader.py tests/drawings/test_dxf_roundtrip.py` → 61 passed, and the delta touched neither them nor dxf_reader.py (confirmed).

NON-VACUITY / DISPLACED-VALUE: every new guard test asserts the displaced value or exact (status,state) pair — e.g. the ring-selection test asserts the outline's first vertex equals ring B's `[990000.0, 200000.0]` (not "some error"); the scale-guard asserts `reason == "unsupported_units"` across 7 bad inputs; the overflow test asserts `coordinate_out_of_range`.

All 9 of my persistent mutations are caught, the r1 BLOCKING F1 and all three advisories are closed, and no regressions in the forbidden suites.

M5-T108 G4 VERDICT: PASS

END-OF-REPORT
