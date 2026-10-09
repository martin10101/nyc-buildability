# M5-T103 — G5 DELTA re-review, rework round 2 (security-reviewer "sec-t103", read-only)

> Transmission history: pinned at 592bbcff (delta = 6e5b831c, identity 6cf6c303), delivered as two SendMessage parts
> (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: round-1 Finding 1 (BLOCKING) and Finding 2 closed and re-verified end to end (every variant refuses
> at about 45 KB peak; chain collection bounded independent of length); no new bypass. Finding 3 stays routed.

---

M5-T103 G5 DELTA re-review (part 1/2). Read-only. HEAD pinned 592bbcff (matches). Delta = git show 6e5b831c: 4 files (pdf_object_streams.py, sheet_objects.py, test_pdf_object_streams.py, producer report) — all in allowed_paths; no forbidden path; app/documents/extraction untouched. Caller check: apply_predictor has exactly ONE caller (pdf_object_streams.py:675, absolute_cap=limits.max_inflated); _png_unfilter only via apply_predictor; merge_stream_entries only via _collect_stream_entries:283. No unguarded caller.

FINDING 1 (was HIGH/BLOCKING) — CLOSED. Fix at sheet_objects.py:349-384: apply_predictor now (a) returns b"" for EMPTY data BEFORE deriving row_len (kills the empty-inflate trigger); (b) validates /BitsPerComponent in {1,2,4,8,16}; (c) refuses row_len > absolute_cap BEFORE _png_unfilter allocates; (d) re-checks row alignment. absolute_cap = MAX_INFLATED_STREAM_BYTES (8 MiB), a constant, not attacker-reachable.

Re-ran every attack variant end-to-end through resolve_object_table (cap 8 MiB):
- empty-inflate + /Columns 50,000,000 -> SheetRefusal, peak 44,698 B (was 50,004,634 B)
- empty-inflate + /Columns 5,000,000,000 -> SheetRefusal, peak 44,646 B
- non-empty(12 B) + /Columns 5e9 -> SheetRefusal "predictor", peak 44,797 B (row_len>cap path)
- no-/Filter /Length 0 + /Columns 5e9 -> SheetRefusal, peak 4,329 B
- bpc=16, row_len just over cap -> SheetRefusal "predictor", peak 44,818 B

All ~45 KB, all refuse, none approaches the cap. The columns*colors*bpc product is a cheap Python bigint (no allocation) before the row_len>cap refusal, so resolve_object_table no longer risks MemoryError — the "never raises" contract holds. A large bpp cannot negative-index (existing i>=bpp guards). Finding 1 verified closed.

Part 2 (Finding 2, new-bypass sweep, no-regression, verdict) follows.

---

M5-T103 G5 DELTA (part 2/2).

FINDING 2 (was MEDIUM) — CLOSED. New sheet_objects.merge_stream_entries (line 441), called per stream from _collect_stream_entries:283, bounds seen by MAX_XREF_ENTRIES (131072) and entries_map by MAX_PDF_OBJECTS (4096) INCREMENTALLY, refusing the moment either is crossed.
- Unit: 33x131072 free entries -> refuses at hop 1, seen=131073 (bounded), entries_map=0. 200000 type-1 -> refuses, entries_map=4097 (bounded).
- End-to-end /Prev chains through resolve_object_table: 33 hops (22 KB input) -> "object count bound", peak 0.92 MB; 66 hops (44 KB) -> same verdict, peak 0.79 MB. Peak is INDEPENDENT of chain length (pre-fix was ~11 MB and grew with hops). Verified closed.

NEW-BYPASS SWEEP (changed paths) — no new hole:
- Charge ordering: PNG unfilter output = rows*row_len < len(data) <= already-charged decoded; working buffers (previous/out) are <= cap and transient — no uncharged growth.
- absolute_cap is a module constant; no /DecodeParms value lets an attacker raise it.
- /Colors unbounded-above is caught by the same row_len>cap refusal.
- never-raises confirmed on all probes.

NO REGRESSION: full shim suite (classic test_sheet_reader + 62-case split-equivalence golden + resolver) -> 99 passed. apply_predictor/merge_stream_entries are resolver-only; the classic content path still refuses /DecodeParms, so the split golden is byte-unchanged. Resolver file alone: 44 passed (was 29).

Finding 3 (predictor CPU, LOW/ADVISORY) is not in this round; routed to the import-route backlog. Acceptable — bounded by the 128 MB budget and the route is unwired.

Both round-1 blocking findings are fixed and independently verified at HEAD 592bbcff.

M5-T103 G5 VERDICT: PASS

END-OF-REPORT
