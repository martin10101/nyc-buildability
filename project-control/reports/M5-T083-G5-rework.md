# M5-T083 — G5 security re-ruling after the rework (security-reviewer "sec-parse", read-only)

> Transmission history: requested by SendMessage after the reviewer's own G5 FAIL (F1 BLOCKING); rework
> 5467318e (cherry-pick of wt-m5t083 b07a4aaa); pinned at 10def4ef with the three code blobs verified
> byte-identical; delivered as two SendMessage parts (1/2, 2/2) ending with END-OF-REPORT; no
> truncation. Joined verbatim by the orchestrator (transport wrapper tags removed only). The original
> joint T083/T086 G5 report (T083 FAIL) stays in M5-T083-G5.md unchanged.

---

M5-T083 G5 RE-RULING (rework) — part 1/2. Read-only. PIN VERIFIED: HEAD 10def4ef; blobs byte-identical (sheet_reader.py 63a992ca, sheet_primitives.py a3659c55, test b60f7e1c). Scope clean: `git diff 7acb3359..HEAD` touches ZERO files under app/documents (byte-untouched); only new import is `is_finite_point` from the sibling module (no new third-party dep, no route wiring). Re-ran my original F1/F2/F3/F5/F6 repros + fuzz against the pinned code via an outside-repo in-memory shim.

F1 CLOSED (was HIGH/BLOCKING). flatten_cubic now takes a hard `budget` and stops the moment `len(out) >= budget` (sheet_primitives.py:116-129); _curveto threads `remaining = MAX_PATH_POINTS - point_count` and refuses `path points` when the curve did not complete within it. Repro: my adversarial single `c` op with ~1e60 control coords at DEFAULT depth 24 on a fresh page → refusal `path points`, tracemalloc peak 53.6 MiB (was ~1.9 GB). A single curve's transient is now bounded to the documented MAX_PATH_POINTS (500k pts) rather than 2**24. Regression check: a normal curve still flattens (9 points, accepted). Because point_count is document-wide, `remaining` shrinks across the whole read — the flatten budget is NOT reset per page/form.

F2 CLOSED (was MEDIUM). Two mitigations, both verified:
- Form decode memoized per (number,generation) via _SheetInterpreter.decode_form/form_cache: 200 `Do /F` of one FlateDecode form → decompressobj called exactly 1 time (was K). Repeated placements are cache hits, no re-decode, no re-charge.
- Document-wide decoded-bytes budget: charge_decoded adds every stream/contents decode to interp.decoded_bytes and refuses `decoded bytes budget` past MAX_TOTAL_DECODED_BYTES (128 MiB). Verified by rebinding the cap to 100 → refusal `decoded bytes budget`.
Cache is bounded: keys ≤ MAX_PDF_OBJECTS (4096), and every cached byte was first charged against the 128 MiB budget (decode_form caches only a non-refusal _decode_stream result), so total cache ≤ 128 MiB — no unbounded memo growth. The earlier ~1.6 TB re-decode amplification is gone; total decompression across the document is hard-capped at 128 MiB.

(F3/F4/F5/F6 + new-path checks + verdict in part 2)

---

M5-T083 G5 RE-RULING (rework) — part 2/2.

F3 CLOSED (was MEDIUM). _SheetInterpreter.interpret now resets the per-page output lists (polylines/text_runs/images = []) at depth 0 before running, while op_count/point_count/decoded_bytes stay document-wide. Repro: 2-page doc, page0 draws one line, page1 another → page0.polylines len 1, page1.polylines len 1 (was 2), and page1's polyline is its OWN geometry (20,20)-(30,30), not page0's. Cross-page leak gone; total primitives still bounded by the document point budget, so the old O(pages×primitives) cumulative-tuple memory is also gone.

F4 CLOSED (was LOW). read_sheet wraps _read_sheet in try/except returning _refuse("unexpected error", "unexpected <Type> during read") — detail is the exception TYPE only, never attacker content. 4000 fuzz mutations → 0 escaping exceptions. `except Exception` (not BaseException) does not swallow KeyboardInterrupt/SystemExit; MemoryError/RecursionError convert to a refusal (fail-closed, the safe direction) — no security bypass is masked.

F5 CLOSED (was LOW). _preview() truncates attacker-derived operator tokens to 64 chars + "...(truncated)" in the unsupported-operator detail. Repro: 100000-char operator → refusal detail length 139 (was 100061). Residual (LOW, pre-existing, NOT blocking): a few details still embed an XObject /name untruncated, but names are lexer-bounded to 64 KB (not the 8 MiB stream size), so no attacker-unbounded detail remains.

F6 CLOSED (was LOW). _map / _map_via and a post-flatten finiteness loop refuse non-finite results with `non-finite coordinate`, covering mapped points, flattened midpoints, and text origins. Repro: eight `cm` ops with scale 1e40 then a line → refusal `non-finite coordinate` (was accepted with (nan,nan)/(inf,inf) output).

NEW-UNBOUNDED-PATH CHECKS (all clean): (1) No budget is reset per page or per form — the three counters are document-wide (only output lists reset at depth 0); the per-curve flatten budget = MAX_PATH_POINTS − document point_count. (2) form_cache cannot grow without bound (≤4096 keys; total cached bytes ≤ the 128 MiB charged decode budget). (3) The backstop does not over-swallow. Additional probe: a Form that DRAWS, placed 100×, → 100 polylines, bounded by the op/point budgets (re-interpret is charged). The FlateDecode decompression-bomb path is unchanged and still refuses at the 8 MiB per-stream cap before charging.

VERDICT: all of F1–F6 closed with evidence, no new unbounded path, scope clean (app/documents untouched, no dep/route change).

M5-T083 G5 VERDICT (rework): PASS
END-OF-REPORT
