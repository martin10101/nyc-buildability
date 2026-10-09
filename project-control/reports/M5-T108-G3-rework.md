# M5-T108 — G3 DELTA re-review, rework round 2 (code-reviewer "cr-t108", read-only)

> Transmission history: pinned at 8273c688 (delta = 5bc472e9, identity 2873d915), delivered as three SendMessage parts
> (1/3..3/3) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: each of the six changes correct, valid-input behaviour unchanged, the matrix consistent; A1/A3/A4/A5
> stay PKT-H items.

---

M5-T108 G3 DELTA re-review (rework r2): PASS — report in 3 parts.

PIN: HEAD 8273c6881677d9ec83f1e03bc5c63af534180df7. Delta reviewed = `git show 5bc472e9`. READ-ONLY.

SCOPE (verified):
- Delta touches exactly the 5 allowed files (report + dxf_import.py + dxf_import_api.py + both test files); no forbidden path; dxf_reader.py, main.py, config.py, requirements untouched.
- `git log 5bc472e9..HEAD` for the 4 T108 code files is EMPTY — no later commit re-touched them, so HEAD's T108 files == the delta. Zero new deps; route stays unmounted + include_in_schema=False; persists nothing.

OBSERVED at HEAD (cwd services/api unless noted):
- `ruff check .` (full tree): All checks passed!
- `pytest tests/drawings/test_dxf_import.py tests/drawings/test_dxf_import_api.py -q`: 57 passed (was 41; +16 new tests).
- repo root `tools/modularity_check.py --check`: exit 0. dxf_import.py 559 lines / dxf_import_api.py 432 — both under WARN 600; neither flagged.

ONE OBSERVED NOTE — NOT a T108 defect, NOT blocking: `pytest tests/drawings` (whole dir) hits 3 collection errors, all from a SyntaxError at app/documents/units.py:276 (`def _match_unit[UnitT: enum.Enum](` — PEP 695 generics require Python 3.12; this local sandbox is 3.11.9). It is transitively imported by M5-T103's sheet_reader.py (a forbidden path for T108), NOT by any T108 module — which is exactly why both T108 suites collect and pass. A local 3.11-vs-repo-3.12 artifact that will not reproduce in CI (3.12); the CI api job at 3.12 is authoritative. Pre-existing sibling code, untouched by this delta.

The delta's 6 changes (all requested): (1) _measured_is_finite guard → typed coordinate_out_of_range; (2) _guard_finite_response pre-render allow_nan guard on both 200 routes; (3) _select_ring seam; (4) isinstance disclosure counts (my A2); (5) degenerate <3-vertex closed rings disclosed (my A6); (6) reader-refusal-detail + disclosed_unknown/skipped_sections escaping tests (G4 A2 / A6).

Correctness + no-behavior-change + matrix + A1/A3/A4/A5 status in part 2.

---

M5-T108 G3 DELTA — correctness of each change (all verified in source):

1. coordinate_out_of_range (dxf_import.py:236 _measured_is_finite; :330 in list_candidates). A huge-but-finite ring (1e300 coords) overflows the shoelace area to inf while coordinates stay finite; the guard refuses typed BEFORE a non-finite value can reach the body. The overflow test is genuine (area = 1e300*2e300 = inf). Maps via the existing _refusal_response else-branch to (422, validation_error), field=building_outline. Reddened by test_mutation_overflow_finiteness_guard (patch guard→True → candidate.area is non-finite).

2. _guard_finite_response (dxf_import_api.py:192; called at both 200 returns). Defense-in-depth mirroring proposal_validation: json.dumps(..., allow_nan=False) → on ValueError returns typed (500, internal_error) WITH correlation id, never a bare Starlette 500. Load-bearing and reddened: test_mutation_pre_render_finiteness_guard neuters BOTH guards → bare 500, no X-Correlation-ID; test_non_finite_body_becomes_typed_500 proves the guard converts it to typed 500 + id.

3. _select_ring (dxf_import.py:456). Behavior-PRESERVING refactor: returns rings[index][1], byte-identical to the prior `rings[assignment.building_outline][1]` (index in range is already validated). rings[index][0]==index holds (dense candidate indexing). Reddened at BOTH service and route by always-ring-0 and largest-ring mutants (building_outline=1 must pick ring B, not the larger ring A).

4. isinstance disclosure counts (dxf_import.py:322-344) — my A2 closed. Imports LinePrimitive/FacePrimitive/TextPrimitive and uses isinstance; a reader rename now fails loudly at import instead of silently reporting 0. Exercised by a real LINE/3DFACE/TEXT fixture.

5. degenerate_closed_rings (dxf_import.py:335) — my A6 closed. A closed polyline with <3 vertices (excluded from candidates, not open) is now disclosed instead of being invisible in both counts.

6. Escaping tests (G4 A2 / A6): reader-refusal detail + disclosed_unknown/skipped_sections now proven escaped; the escaping code was already present — tests were the gap.

NO BEHAVIOR CHANGE FOR VALID INPUT — confirmed: _select_ring is identical indexing; the finiteness guards never trip on in-range NYC 2263 coords; the disclosure change only ADDS a key and the LINE/FACE/TEXT counts were already correct (names matched). All happy-path tests (candidates_200, draft_200, discrepancy, no-persistence) still pass.

MATRIX CONSISTENCY — confirmed: coordinate_out_of_range→(422,validation_error); pre-render guard→(500,internal_error). Both are pre-existing matrix members; the matrix test now asserts the (500,internal_error) pair. No new/unlisted emissions.

MODULARITY — pass (559/432 lines, focused helpers, exit 0).

A1/A3/A4/A5 status in part 3.

---

M5-T108 G3 DELTA — prior advisories status + verdict (part 3 of 3).

A1/A3/A4/A5 remain PKT-H / robustness items, unchanged by this delta (verified none regressed, none silently altered):
- A1 (rate-limiter _hits not memory-bounded, dxf_import_api.py:137-163) — untouched; still the standing PKT-H item (bound memory + extract a shared limiter).
- A3 (malformed-param /draft skips the limiter, :~403-408) — ordering unchanged.
- A4 (256 KiB body/read ceiling reuses proposal_validation.MAX_BODY_BYTES, :98) — unchanged; revisit for real DXF at mount. Note: the new test_upload_exactly_at_ceiling_accepted_plus_one_refused now proves the ceiling is strict '>' (exactly MAX_BODY_BYTES reaches the reader; +1 → 413), which is a welcome hardening around A4 but does not change the value.
- A5 (SECTION sniff scans only raw[:4096], dxf_import.py:~264) — unchanged.

All four stay as previously reported; none blocks acceptance of an unmounted internal packet.

VERDICT SUMMARY: the rework is a clean, consolidated, in-scope change that closes G4 F1 (user-assigned ring proven by mutants at service and route), G5 MEDIUM 1 (overflow → typed refusal + a reddening-tested pre-render 500 guard), and my G3 A2/A6 advisories, plus the G4 A1/A2/A3 test-coverage gaps. Every new guard has a reddening consuming-namespace mutant; valid-input behavior is unchanged; the typed-error model and (status,state) matrix stay consistent; scope, dependencies, unmounted posture, and no-persistence are all intact. The only non-green signal is a local Python 3.11-vs-3.12 collection error in a sibling M5-T103 file, unrelated to T108 and CI-authoritative at 3.12.

M5-T108 G3 VERDICT: PASS

END-OF-REPORT
