# M5-T103 — G3 DELTA re-review, rework round 2 (code-reviewer "cr-t103", read-only)

> Transmission history: pinned at 592bbcff (delta = 6e5b831c, identity 6cf6c303), delivered as two SendMessage parts
> (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: G5 F1 and A1 closed with red/green proof; verdict-equivalent for every in-bound input; the 62-case
> golden byte-identical. New LOW advisories ADV-1 (absolute tracemalloc ceilings) and ADV-2 (593 SLOC near the 600 warn
> threshold) are routed at the accept seam.

---

M5-T103 G3 DELTA re-review (read-only). PART 1/2.

PIN: HEAD 592bbcff5ac4e3c85fc252de37c385070fe1a34c.

DELTA SCOPE (verified): the complete round1(3fab28f6)->HEAD code delta is pdf_object_streams.py, sheet_objects.py, test_pdf_object_streams.py only. sheet_reader.py and sheet_interpreter.py are UNCHANGED from round 1 (already-passed review). 580d1125 touches only other tasks' docstrings (confirmed 6 unrelated files, +1 line each).

VERIFIED GREEN at HEAD 592bbcff:
- Shim run_sheet_all_tests.py: 99 passed, exit 0 (round 1 = 84; +15 round-2 tests). Includes the 62-case split-equivalence golden — still passing.
- ruff: All checks passed. modularity_check --check: exit 0, failures 0; NONE of the four modules in the warn list. SLOC pdf_object_streams 593 / sheet_objects 402 (both <600).
- Classic path UNTOUCHED: apply_predictor / inflate_guarded / merge_stream_entries are called ONLY by the resolver (grep-confirmed); classic content _decode_stream STILL refuses /DecodeParms (sheet_objects.py:151) — the refuse_decode_parms golden freeze is intact. So the golden is byte-identical.

G5 F1 (predictor working buffer, BLOCKING) — CLOSED. apply_predictor (sheet_objects.py:349-383) now (a) returns on empty data BEFORE deriving row_len; (b) whitelists /BitsPerComponent to {1,2,4,8,16}; (c) bounds row_len by absolute_cap (=per-stream inflated cap) BEFORE _png_unfilter allocates. Proven by 5 tests incl. a TWO-MUTANT load-bearing test: with the fix peak ~0.04 MB; restoring the round-1 allocation order (a /Columns-sized buffer on empty data) balloons peak >4 MB. No MemoryError — "never raises" holds.

A1 / G5 F2 (object-count memory amplification, my round-1 HIGH advisory) — CLOSED. New merge_stream_entries (sheet_objects.py:439-471) bounds entries_map<=MAX_PDF_OBJECTS(4096) and seen<=max_xref_entries(131072) INCREMENTALLY during /Prev collection, so chain-collection memory is a CONSTANT regardless of chain length. Same feature "object count bound" as round 1's post-collection check. Load-bearing mutant (merge with no incremental bound) proves the peak balloons past ceiling while still refusing with the same feature. This directly resolves the ~4.3M-entry amplification I flagged.

Part 2 (A4/A5/A6 + coverage + verdict-equivalence + new advisories + verdict) next.

---

M5-T103 G3 DELTA re-review. PART 2/2.

A4 (weak broken-offset test) — CLOSED, better than asked. The fixture now points object 3's entry at object 1's REAL header (a lying offset landing on a real-but-wrong object), so it actually exercises the (number,generation) identity check and asserts feature "object identity" / origin SHEET_PROFILE. (The round-1 fixture used a mid-file offset that hit a parse error — STRICT_READER — never the identity path; round 2 fixed both fixture and assertion.)

A5 — CLOSED (dead TIFF-test assignment removed). A6 — CLOSED: test_classic_prev_without_xrefstm_returns_strict_refusal asserts a classic table with trailer /Prev and no /XRefStm still returns the strict "incremental update chain" refusal (origin STRICT_READER) unchanged — the resolver defers (None).

G4/G1 coverage added and verified: cross-phase budget carry (two-sided load-bearing — seed carried => "decoded bytes budget" refusal; seed stripped => no such refusal); zero-width /W [0 4 0] type+field3 defaults; the TRUE no-/Filter raw decode branch (round-1's "uncompressed" test actually used Flate — renamed, real raw test added); the resolver's OWN /Filter echo _preview-truncated; a 2nd XObject echo site; a _DecodeBudget no-overshoot unit test. G1 F1: _MAX_FIELD_WIDTH now honestly documented as the module's own bound (ISO sets no /W max).

VERDICT-EQUIVALENCE (your key ask) — CONFIRMED. For every in-bound input the outcome and feature strings are identical to round 1: the merge is byte-identical within the caps, and the predictor adds only bounds checks that never fire on legitimate geometry (/Columns=7, bpc=8, row_len=7). The only behavior changes are on ADVERSARIAL inputs that round 1 mishandled — empty-inflate + huge /Columns (round 1: over-allocated/raised) and the wide-chain amplification — which now become typed "predictor" / "object count bound" refusals. 62-case golden byte-identical (99 passed). Imports acyclic (resolver imports merge_stream_entries from sheet_objects; no back-edge). A2/A3 (scan-only label) and A7 (stream-in-objstm) correctly deferred to the backlog — non-blocking.

NEW advisories (LOW, non-blocking):
- ADV-1: the two load-bearing tests assert absolute tracemalloc peaks (4 MB ceilings). Margins are wide (~4x both ways: fix ~0.04/1.1 MB, mutant ~50/11 MB) so flake is unlikely, but absolute-memory assertions are environment-sensitive (local 3.11 vs CI 3.12) — CI is the authority; watch for flake.
- ADV-2: pdf_object_streams.py at ~593 SLOC is near the 600 warn threshold; the next growth should split (e.g. peel the classic-table reader or the stream-decode composition into its own module).

All round-1 blocking/advisory findings in scope are resolved with red/green proof; no regression; golden byte-identical; verdict-equivalent for in-bound inputs.

M5-T103 G3 VERDICT: PASS

END-OF-REPORT
