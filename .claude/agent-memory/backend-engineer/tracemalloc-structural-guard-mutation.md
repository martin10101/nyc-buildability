---
name: tracemalloc-structural-guard-mutation
description: Proving allocation-order / check-location memory guards load-bearing (tracemalloc + consuming-namespace function monkeypatch), and the SLOC-decoupling helper pattern used in the sheet-reader PDF resolver
metadata:
  type: feedback
---

For a memory-DoS guard whose fix is a STRUCTURAL change (allocation order, or moving a bound
check earlier) rather than a constant value, a constant-rebind mutation cannot prove the guard
is load-bearing.

**How to apply:** write the regression test to run the crafted file under `tracemalloc.start()`
and assert `peak < CEILING` (state the ceiling). Then write a sibling "load-bearing" test that
monkeypatches the CONSUMING-namespace function to a test-local reimplementation of the PRE-FIX
order and asserts `peak > CEILING` (it reddens). Calibrate CEILING with a throwaway probe that
prints fix-peak vs mutation-peak, then set it between them with wide margins (in
`services/api/app/drawings`: predictor empty-inflate fix ~45 KB vs pre-fix ~50 MB; /Prev-chain
object-count fix ~1.1 MB vs pre-fix ~11 MB; ceiling 4 MB works for both). tracemalloc peaks are
deterministic enough across 3.11/3.12 that relative fix-vs-mutation gaps hold.

**Consuming-namespace monkeypatch:** patch the name where it is LOOKED UP at call time. The
resolver `pdf_object_streams` does `apply_predictor(...)` / `merge_stream_entries(...)` as its own
module globals (imported from `sheet_objects`), so `monkeypatch.setattr(pdf_object_streams,
"apply_predictor", _old)` bites even though the def lives in `sheet_objects`. Cross-phase seed
carry: wrap `sheet_reader.resolve_object_table` to return `ResolvedTable(..., decoded_bytes=0)`.

**SLOC-decoupling helper pattern:** when the higher module is near its 600-SLOC cap (WARN at 600
in `tools/modularity_check.py`), put a new shared helper in the LOWER decode module
(`sheet_objects`) taking PLAIN-INT bounds (not the resolver's `_ResolverLimits`, which would need
a back-import and create a cycle). This keeps imports acyclic AND gives the clean monkeypatch
seam above. See `merge_stream_entries` / `apply_predictor(absolute_cap=...)`.

Related: [[in-process-mutant-technique]], [[env-producer-sandbox-no-exec]].
