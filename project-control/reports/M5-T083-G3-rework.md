# M5-T083 — G3 re-review after the rework (code-reviewer "cr-drw", read-only)

> Transmission history: requested by SendMessage after the G5 FAIL rework (5467318e, cherry-pick of
> wt-m5t083 b07a4aaa); pinned at 10def4ef with the three code blobs verified byte-identical; delivered as
> two SendMessage parts (1/2, 2/2) ending with END-OF-REPORT; no truncation. Joined verbatim by the
> orchestrator (transport wrapper tags removed only). The reviewer's first joint T083/T086 G3 (PASS)
> stays in M5-T083-G3.md unchanged.

---

M5-T083 G3 RE-REVIEW (rework). Read-only; HEAD verified 10def4ef; blobs match (sheet_reader 63a992ca, sheet_primitives a3659c55, test b60f7e1c). Rework 5467318e = exactly the 4 allowed paths. Part 1/2.

PRIOR FINDINGS — ALL RESOLVED (verified, not just claimed):
- F1 (was BLOCKING at G5) single-curve transient allocation: FIXED. `flatten_cubic` now takes a hard `budget` and returns bool, refusing to grow `out` past budget at the top of every recursive call (sheet_primitives.py:116-117). `_curveto` threads `remaining = MAX_PATH_POINTS - point_count` (sheet_reader.py:736-745) and refuses "path points" when incomplete. EMPIRICALLY CONFIRMED in isolation: never-flat 1e14-coord curve with budget 1000 -> completed=False, len(out)=1000 exactly (was ~2^24). The full leaf list is never materialized. Recursion depth still capped at 24; total calls bounded ~2*budget.
- F2 (my prior ADVISORY) q/Q text state: FIXED. `q` saves and `Q` restores `(ctm, font_size, leading)` via `_gs_stack` (sheet_reader.py:796,802) per ISO Table 52; forms inherit caller text state (`_place_form` passes font_size/leading, :1070-1071) and form-local changes stay isolated in the form's own `_StreamRun`.
- F3 (my prior NIT) mid-path cm curve start: FIXED. current point + subpath start stored in DEVICE space; `_curveto` uses stored `p0` (:724); `v`'s first control is the current device point via `ctrl1_is_current` (:725,847).

NEW MECHANISMS — CORRECT:
- Per-page isolation: output lists reset only at depth 0 (:532-535); op_count/point_count/decoded_bytes/form_cache stay DOCUMENT-WIDE (:481-484). Already-built SheetPage tuples are unaffected by the next page's reset.
- Form decode memoization: `decode_form` caches decoded bytes per (num,gen) (:497-510); charge happens once per ref key. Re-placements still re-interpret (op/point budgets charged each time), so a place-many form-bomb stays bounded by MAX_CONTENT_OPERATORS.
- Decoded-bytes budget: `charge_decoded` accumulates vs MAX_TOTAL_DECODED_BYTES=128MB, wired into both `_decode_stream` return paths and `_decode_contents`; counts decompressed size (right amplification bound).
- Top-level backstop: `read_sheet` wraps `_read_sheet` in try/except -> typed refusal carrying only the exception TYPE (:350-353) — "refusal is a VALUE" now holds unconditionally.
- Non-finite gating: `_map`, the post-flatten scan (:746-748), and `_map_via` refuse inf/nan after CTM math.
- `_open_after_close` (:690): a segment op after h/re/close begins a new subpath at the current device point (ISO Table 59) instead of refusing.
- `_preview` truncates attacker operator tokens to 64 chars (:190,818).

Continued in part 2.

---

M5-T083 G3 RE-REVIEW (rework). Part 2/2.

NO REGRESSION of the ISO 32000-1 semantics verified in the first pass: CTM premultiply concat = m×CTM (sheet_primitives.py:36), apply_matrix row-vector, c/v/y control-point mapping (c full, v first-ctrl=current, y dup endpoint), re = moveto+3 lineto+close, form_ctm = form_matrix×CTM, form Resources inherited when absent, image matrix = current CTM with dims from dict keys and raw_data never touched. q/Q CTM restore intact (the text-state fields are additive to the same save/restore). `_finish` still refuses dangling operands / unclosed BT / unbalanced q.

SCOPE / GATE CLAIMS (all re-verified at HEAD 10def4ef):
- Exactly the 4 allowed paths changed; app/documents byte-untouched (`git diff --stat f9bfd54d HEAD -- services/api/app/documents` EMPTY); nothing outside app/drawings imports the profiles (full-repo grep clean); `__init__.py` untouched.
- Imports: stdlib `math`/`zlib` + `app.documents.extraction.*` + `app.drawings.sheet_primitives` only. Zero new dependencies.
- `python -m ruff check app/drawings tests/drawings/test_sheet_reader.py` -> All checks passed.
- Modularity `--check` -> failures 0; sheet_reader.py warning-only (JUSTIFY band).
- Tests: 37 passed via the provided outside-repo 3.11 shim (23 prior + 14 rework), 0 skipped. Producer mutation record shows all 5 required mutants caught (budget-threading, page-output-share, memoization, cubic_flat and->or, immediate-parent-only cycle). I re-verified the budget mutant's mechanism directly.

MODULARITY RULING (Q3): sheet_reader.py is now 962 SLOC (JUSTIFY band, warning-only, CI failures 0). The cohesion justification is ACCEPTABLE for THIS task: the packet grants only two production files, the geometry algebra is already extracted to sheet_primitives, and the remainder is one cohesive content-interpretation state machine boxed by the allowed_paths. HOWEVER — ADVISORY (non-blocking): at 962/1000 there are only 38 SLOC of headroom to the HARD cap. A decomposition (object-graph/stream-decode vs the `_StreamRun` interpreter into a third production module) is effectively REQUIRED before ANY further growth, and needs a future packet that grants that third path. Do not add more to this file under the current 2-file grant.

RESIDUAL NOTE (non-blocking, not a defect): not every attacker-derived token is `_preview`-truncated (e.g. a long PdfName echoed in some `/{name}` xobject-refusal details), but the primary unbounded vector — the operator word — is fixed, and PDF name lengths are bounded by the strict lexer. No action required.

No BLOCKING findings. The G5 F1 blocking item and my prior F2/F3 are resolved with correct, tested mechanisms; no semantics regressed; scope and gates clean.

M5-T083 G3 VERDICT (rework): PASS

END-OF-REPORT
