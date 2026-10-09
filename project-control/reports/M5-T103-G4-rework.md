# M5-T103 — G4 DELTA re-review, rework round 2 (qa-engineer "qa-t103", read-only)

> Transmission history: pinned at 592bbcff (delta = 6e5b831c, identity 6cf6c303), delivered as two SendMessage parts
> (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: round-1 gaps W1/W9/W10 now caught; NW1-NW3 caught with deterministic peaks; NW4 (no fixture at
> cap or cap+1) is a LOW advisory routed at the accept seam.

---

M5-T103 G4 DELTA re-review (independent, read-only, in-memory mutation) — part 1 of 2.

PIN: HEAD 592bbcff. Delta = `git show 6e5b831c` (cherry-pick 277456af; sheet_objects.py, pdf_object_streams.py, +15 tests, report). Method: local py3.11 bare-package shim.

REGRESSION: full shim 99 passed (was 84). Git-verified BYTE-UNCHANGED since round 1: the 62-case split-equivalence golden, test_sheet_reader.py, and app/documents/extraction — those suites pass unchanged. apply_predictor's new absolute_cap arg has exactly ONE caller (pdf_object_streams._decode_stream:675, correct) — no broken caller.

ROUND-1 GAPS — all now CLOSED and non-vacuous (re-ran my own mutations against the new tests):
- A1/W10 cross-phase budget carry: my independent zero-seed mutation now REDDENS test_cross_phase_budget_carry (was MISSED). The budget window (700; resolver charge 211 + content 600) is calibrated so only the carried seed trips it; a load-bearing twin is present too.
- A2/W1 zero-width /W type default: mutating the `if w0 else 1` default 1->0 now REDDENS test_zero_width_type_and_field3_defaults (new /W [0 4 0] fixture, also covers the field-3 default). The misleading comment is fixed.
- A3/W9 _preview: patching _preview->identity now reddens 4/4 echo tests (was 2/8) — the resolver's OWN /Filter echo and a 2nd XObject echo are now pinned; the remaining XObject sites route through the same helper.
- A4: test_reads_raw_no_filter_xref_stream added (true filt-is-None branch); the "uncompressed" misnomer renamed to test_reads_flate_xref_stream.
- A5: the broken-offset test now asserts feature == "object identity".
- Minor: test_decode_budget_charge_refuses_before_incrementing (DB-064(d) no-overshoot: asserts used stays 6 on refusal); in-test green baselines added to the ratio / objstm-count / N / budget guard tests.

New guards (NW1-NW4) + verdict follow in part 2.

---

M5-T103 G4 DELTA — part 2 of 2 (new guards + verdict).

NEW GUARDS — 4 weakenings aimed at G5 F1/F2; measured peaks (tracemalloc):
- NW1 predictor allocation-before-check (restore round-1 order): NON-VACUOUS. Fix peaks 0.045 MB, IDENTICAL across 3 runs; the round-1 order (working buffer sized by /Columns=50M BEFORE the empty/bound check) peaks 50.0 MB. The 4 MB ceiling sits between with a wide margin. CAUGHT by test_predictor_empty_inflate_is_memory_bounded + its load-bearing twin.
- NW2 object-count check-after-collection (round-1 _merge_no_bound): NON-VACUOUS. Fix peaks ~0.8-1.07 MB across 3 runs; the whole-chain merge peaks 11.2 MB (33 hops x 2000). 4 MB ceiling between. CAUGHT by test_object_count_bound_is_memory_bounded + twin. The incremental bound trips at entries_map > 4096 (MAX_PDF_OBJECTS) DURING collection, capping memory.
- NW3 drop the empty-data early return: CAUGHT. Direct calls confirm empty -> b"" but non-empty + big /Columns -> "predictor" refuse; removing `if not data: return data` flips the empty case to a refusal, which test_predictor_empty_data_returns_without_geometry (asserts == b"") pins. bpc set {1,2,4,8,16} and oversized-row are also tested.
- NW4 off-by-one on the caps: MISSED (LOW-severity ADVISORY). The predictor boundary is exactly row_len > cap (row100/cap100 passes, /cap99 refuses) but the test overshoots (cap 5, row 100); the object-count chain overshoots 4096 by ~62000. No fixture sits at cap or cap±1, so a `>`->`>=` slip is unpinned. Fail-closed direction and immaterial magnitude on MB/4096 memory caps — not blocking.

DETERMINISM: both new memory tests' fix-peaks are stable across 3 runs and far under their 4 MB ceilings, while the mutation peaks (50 MB / 11.2 MB) are far over — no CI flake risk.

ASSESSMENT: all three of my round-1 ADVISORY gaps (A1/A2/A3) are closed with non-vacuous, load-bearing tests; A4/A5/minor closed; the two new G5 memory guards (predictor working-buffer bound; incremental object-count bound) have non-vacuous, deterministic memory regression tests whose in-process mutations redden. Only NW4 (cap boundary off-by-one) remains — LOW-severity ADVISORY, safe direction. No BLOCKING findings.

M5-T103 G4 VERDICT: PASS
END-OF-REPORT
