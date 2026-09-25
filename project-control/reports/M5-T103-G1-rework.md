# M5-T103 — G1 DELTA re-review, rework round 2 (data-contract-verifier "dc-t103", read-only)

> Transmission history: pinned at 592bbcff (delta = 6e5b831c, identity 6cf6c303), delivered as two SendMessage parts
> (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: /BitsPerComponent {1,2,4,8,16} matches ISO 32000-1 7.4.4.4 Table 8; the incremental bound keeps the
> round-1 newest-first/free-entry semantics; the six corpus files re-run in memory with outcomes identical to round 1.

---

M5-T103 G1 DELTA re-review (data-contract-verifier, read-only) — PART 1/2. Verdict is PASS; details below and in 2/2.

PIN: HEAD 592bbcff at start; frozen identity 6cf6c303. Delta = `git show 6e5b831c` (4 files). Round-1 "3fab26f6" was my transcription slip for 3fab28f6 — noted, thanks.

METHOD: read the full delta diff for both production files; re-verified each spec-facing change against ISO 32000-1 (web-corroborated); ran the 3 sheet suites via the shim (99 passed); re-ran all 6 corpus files in memory (sha256-checked). apply_predictor's new required kwarg `absolute_cap` has exactly ONE production caller (pdf_object_streams.py:675), which passes it — no broken caller.

DELTA VERIFICATION (change / spec / result):
1. /BitsPerComponent validated in {1,2,4,8,16} — §7.4.4.4 Table 8 — PASS. Exactly the spec's valid set ("Valid values are 1, 2, 4, 8, and 16; default 8"); a present-but-non-integer /BitsPerComponent (None) is also refused; default 8 stays valid.
2. Empty predicted stream returns empty output — PASS. apply_predictor returns b"" BEFORE deriving row_len from an attacker-chosen /Columns, so no geometry-sized buffer is allocated for empty data; functionally identical to unfiltering zero rows, and a downstream 0-row table is handled correctly by _parse_entries.
3. Row-length cap + whole-row alignment checked before unfiltering — PASS. `row_len > absolute_cap` (= MAX_INFLATED_STREAM_BYTES 8MB, threaded from the resolver) → typed "predictor" refusal, and `len(data) % (row_len+1) != 0` → refusal, BOTH before _png_unfilter allocates. Real xref rows (~4-11 bytes) unaffected; the reviewer's empty-inflate /Columns=50M case is now bounded. _png_unfilter itself is unchanged (Paeth / Up etc. still byte-correct).
(continued in 2/2)

---

M5-T103 G1 DELTA — PART 2/2 (merge guard, wording, corpus, verdict).

4. Object-count bound enforced incrementally during /Prev collection — PASS. The new sheet_objects.merge_stream_entries preserves the EXACT round-1 semantics I verified: first-seen (newest — chain is followed newest-first) wins; a free type-0 entry seen first suppresses a later in-use one; only types 1/2 enter entries_map. It adds two incremental caps — `len(entries_map) > MAX_PDF_OBJECTS` (same "object count bound" / "over N in-use objects" verdict as the RETAINED _materialize backstop) and `len(seen) > MAX_XREF_ENTRIES` (new "over N distinct cross-reference entries"). The _materialize backstop remains (still needed for the hybrid classic-merge path). Newest-first / free-entry semantics UNCHANGED. Note: the new seen-cap makes a pathological file (>131072 distinct object numbers but ≤4096 in-use) refuse where round-1 would have resolved — safe, fail-closed, addresses my round-1 F3, with 32× headroom over the in-use cap; no real / in-scope file is affected.
5. F1 wording — PASS. _MAX_FIELD_WIDTH comment + _read_w docstring now state it is the module's OWN safety bound and that §7.5.8.2 sets no /W maximum. Accurate.

CORPUS (re-run in memory, all 6, sha256 MATCH, run1==run2): outcomes IDENTICAL to round 1 — item1/2 REFUSAL 'decode parameters' (content), item3-6 REFUSAL 'malformed pdf' found '<<' (content). Critically, items 1-2's PNG-predicted xref streams still decode correctly through the reworked apply_predictor (they reach the content limit, not a predictor error) → the memory-guard rework caused NO real-file regression. None produces linework; the honesty caveat still holds.

TESTS: shim → 99 passed (was 84; the delta adds guard/predictor tests).

Round-1 verified behavior (entry types, /W + /Index defaults, hybrid precedence, objstm header, /Extends-safe, predictors, mandatory guard) is preserved; the delta is additive memory-hardening + the BPC spec-tightening + wording. No BLOCKING and no new advisory findings. F2/F4 are backlog per your routing.

M5-T103 G1 VERDICT: PASS

END-OF-REPORT
