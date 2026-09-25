# M5-T109 producer report — D-087 PKT-D: CAD export service + UNMOUNTED export route + PDF-writer DB-075(a) fix

Producer: backend-engineer. Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t109` (branch
`task/M5-T109-export-service`). Claim seam / parent: `110894295ec97c1d7cb87deb3421a628b526b66b`.

## Scope delivered (allowed paths only)

- `services/api/app/cad/export_service.py` — NEW pure export service (format dispatch, caps before
  the writers, one reconciled redacted refusal, mandatory filename-safety token, GLB single-prism
  dedupe, honesty labels). Replaces the seed placeholder.
- `services/api/app/api/v1/export_api.py` — NEW UNMOUNTED, flag-gated `POST /api/v1/export` route
  (bounded body, per-caller rate limit, off-event-loop cancellable job + per-request deadline,
  per-format media types, server correlation id, typed refusals). Replaces the seed placeholder.
- `services/api/tests/cad/test_export_service.py` — NEW (36 tests). Replaces the seed placeholder.
- `services/api/tests/cad/test_export_api.py` — NEW (20 tests). Replaces the seed placeholder.
- `services/api/app/cad/pdf_sheet_writer.py` — DB-075(a) ONLY: broadened `_coerce_vertex` `float()`
  catch to `(ValueError, TypeError)` -> typed `non_numeric_coordinate` refusal; docstring note.
- `services/api/tests/cad/test_pdf_sheet_writer.py` — DB-075(a) test ONLY (appended 6 test cases:
  hostile-`__float__` typed refusal x4 params + a narrow-catch reddening mutant + reuse of the
  existing golden test).

## Per-acceptance-scenario evidence

- **AS-1 (service dispatch + caps before writers).** `test_each_format_dispatches_to_its_writer`
  (dxf -> `render_site_plan_dxf`, pdf -> `render_site_plan_pdf`, glb -> `write_glb`; per-format
  media type + extension). Caps BEFORE normalization/writer:
  `test_geometry_over_the_tightest_cap_refuses_before_normalization` (PDF cap 1024, over-cap ring
  with NON-numeric vertices refuses `ring_cap_exceeded` — the RAW length check fires before any
  coercion, DB-057(d)); `test_dxf_uses_its_own_looser_ring_cap` (tightest-per-format);
  `test_floors_over_cap_refuse` (floors<=2000); `test_over_long_caller_text_refuses_before_the_writer`;
  `test_claim_word_in_caller_text_refuses_before_the_writer`. Each bound has a reddening mutation
  (table below).
- **AS-2 (one reconciled, redacted refusal).** `test_glb_raise_and_pdf_return_map_to_the_same_shape`
  (GLB RAISE + PDF RETURNED refusal -> identical `{reject_code, detail}` keys);
  `test_reconciled_refusal_never_echoes_a_hostile_coordinate` (GLB writer echoes the offending
  coordinate in its own message; the reconciled detail does not); `test_dxf_writer_raise_is_reconciled`;
  route-level `test_422_typed_refusal_through_the_real_route` (DB-075(b)) +
  `test_422_bad_geometry_is_reconciled_and_redacted`.
- **AS-3 (filename safety, MANDATORY).** Table below. `test_hostile_caller_value_cannot_break_the_header`
  (quote/`;`/CR-LF/non-ASCII), `test_token_is_the_allowlist_only`, `test_token_length_is_capped`,
  `test_empty_token_falls_back_to_server_default` (DB-065(a)),
  `test_content_disposition_carries_both_ascii_and_rfc5987_forms`, and the MANDATORY mutation
  `test_filename_token_mutation_reddens`. Route: `test_filename_falls_back_to_correlation_id_when_token_empties`.
- **AS-4 (route, unmounted).** `test_route_is_unmounted_in_the_real_app` (absent from real app routes
  AND OpenAPI); `test_flag_off_is_a_generic_404` (no correlation id, no body hint);
  `test_200_returns_a_file_per_format` (per-format media type + `Content-Disposition` + `X-Correlation-ID`
  + `nosniff`); `test_413_oversized_body`; `test_422_malformed_body`/`test_422_nan_is_refused`;
  `test_429_per_caller_rate_limit`; `test_503_per_request_deadline` (off-event-loop
  `run_in_threadpool` under `asyncio.wait_for`, DB-061(i)); `test_500_on_an_unexpected_internal_defect`
  (no `str(exc)` leak); `test_correlation_id_on_every_non_disabled_response`. Typed refusals are JSON,
  never a partial file (asserted `content-type: application/json` on the 422).
- **AS-5 (provenance + honesty + caps).** `test_source_labels_are_honest`
  (proposed -> "Proposed - not a city record"; generated_option -> "Generated building option");
  `test_unsupported_source_is_refused` (approved/permitted/maximum_allowed/as_of_right refused);
  `test_output_is_deterministic_no_clock` (all three formats byte-stable);
  `test_generated_at_is_load_bearing_in_the_pdf_title_block`; GLB coincident-cap dedupe
  `test_glb_is_a_single_extrusion_dedupe` (a 1-floor and a 3-floor stack with equal total height give
  byte-identical GLB — per-floor interface caps are not emitted, DB-054(m)) + provenance disclosure.
- **AS-6 (writer fix + byte identity).** `test_hostile_float_vertex_is_a_typed_refusal_never_raises`
  (numbers.Real with `__float__` raising ValueError AND TypeError -> `non_numeric_coordinate`);
  `test_narrow_overflow_only_catch_reddens_on_a_hostile_float` (pre-fix narrow catch RAISES);
  `test_golden_sha256` (unchanged golden c38360f9…); `test_cad_owner_samples.py` passes UNCHANGED
  (10 tests); zero new dependencies (stdlib + shapely/numpy/pydantic/fastapi already admitted);
  `app/main.py` untouched; modularity_check exit 0.

## Filename-safety test table (AS-3, plan §2 MANDATORY)

| Hostile caller input (bbl/generated_at) | What must not survive | Result |
|---|---|---|
| `1"; DROP TABLE` | `"`, `;`, space | token `1DROPTABLE`; filename matches `^site-plan-[A-Za-z0-9._-]+\.dxf$`; cd has exactly the 2 structural quotes + 2 structural `;` |
| `1-0045\r\nSet-Cookie: x` | CR, LF, `:`, space | no `\r`/`\n` in cd; "Set-Cookiex" letters+hyphen survive (harmless plain filename text, cannot split a header) |
| `1-0045\u00e9\u4e2d` (non-ASCII) | é, 中 | dropped; RFC 5987 `filename*=UTF-8''` form present; neither char in cd |
| `1-0045; filename=evil` | `;`, `=`, space | dropped -> `filenameevil` plain text; no extra header parameter injected |
| `!!!` / `...` / `---` (allowlists to nothing) | whole token | `build_filename_token` returns None -> caller-free server default (route uses the correlation id), DB-065(a) |
| MANDATORY mutation: raw value passed straight into the token | — | mutant leaks `"` into the filename (guard proven load-bearing) |

The token is `[A-Za-z0-9._-]`-allowlisted, length-capped at 80, derived from the validated bbl +
deterministic generated_at; raw caller text never reaches a header value; both ASCII `filename` and
RFC 6266/5987 `filename*` are emitted.

## Refusal-reconciliation table (AS-2; DB-059(e),(h))

| Writer | Mechanism | Example code | Reconciled to |
|---|---|---|---|
| DXF (`render_site_plan_dxf`) | RAISES `DxfWriterError` (`.code`) | `coordinate_out_of_range`, `floor_cap_exceeded`, `forbidden_character` | `ExportRefusal(code, server-built detail)` |
| PDF (`render_site_plan_pdf`) | RETURNS `SitePlanRefusal` (`.reject_code`) | `invalid_ring`, `oversize_input`, `non_numeric_coordinate` | `ExportRefusal(reject_code, server-built detail)` |
| GLB (`write_glb`) | RAISES `GlbWriterError` (`.code`) | `coordinate_out_of_range`, `degenerate_triangle` | `ExportRefusal(code, server-built detail)` |
| Service pre-writer | RETURNS `ExportRefusal` directly | `unsupported_format/source`, `ring_cap_exceeded`, `floor_cap_exceeded`, `text_too_long`, `claim_class_word`, `missing_building_geometry`, `invalid_geometry` | itself |

`detail` is built server-side from the fixed `reject_code` + format ONLY; the writers' own messages
(which interpolate the caller name/coordinate) are discarded — the `reject_code` is always a fixed
enum token, never caller text. Redaction proven by `test_reconciled_refusal_never_echoes_a_hostile_coordinate`
and `test_422_typed_refusal_through_the_real_route` ("luxury"/"HOSTILE_MARKER" absent from details).

## Mutation table (each guard reddens; in-process, consuming namespace)

| Guard | Mutation | Real | Mutant |
|---|---|---|---|
| service ring cap | `monkeypatch.setitem(_FORMAT_RING_CAP, "pdf", 10_000_000)` | `ring_cap_exceeded` | different code (PDF writer's own `oversize_input`) |
| floor cap | `monkeypatch.setattr(es, "MAX_FLOORS", *100)` (GLB path, no writer floor cap) | `ExportRefusal(floor_cap_exceeded)` | `ExportResult` (file produced) |
| text length cap | `monkeypatch.setattr(es, "MAX_TEXT_CHARS", 1e9)` (DXF; annotation is fixed labels) | `ExportRefusal(text_too_long)` | `ExportResult` |
| claim-word screen | `monkeypatch.setattr(es, "contains_claim_word", lambda *t: None)` (DXF) | `ExportRefusal(claim_class_word)` | `ExportResult` |
| filename token allowlist | `monkeypatch.setattr(es, "build_filename_token", raw)` | filename has no `"` | filename leaks the raw `"` |
| PDF `_coerce_vertex` DB-075 catch | restore pre-fix OverflowError-only catch | typed `non_numeric_coordinate` | RAISES ValueError (never-raise contract broken) |

## Commands (cwd + verbatim tails)

```
# cwd services/api — ruff on my files (api CI first step)
$ python -m ruff check app/cad/export_service.py app/api/v1/export_api.py app/cad/pdf_sheet_writer.py \
    tests/cad/test_export_service.py tests/cad/test_export_api.py tests/cad/test_pdf_sheet_writer.py
All checks passed!

# cwd services/api — full cad suite
$ python -m pytest tests/cad -q
FAILED tests/cad/test_glb_writer.py::test_as5_not_wired_into_the_app - Assert...
1 failed, 428 passed in 5.45s          # the ONE failure is the forbidden unwired-assertion (see Deviations)

# cwd services/api — my new tests + owner samples unchanged
$ python -m pytest tests/cad/test_export_service.py tests/cad/test_export_api.py tests/cad/test_cad_owner_samples.py -q
66 passed in 2.67s

# cwd repo root — modularity
$ python tools/modularity_check.py --check
selected 497 files; failures 0; warnings 27            # exit 0; export_service.py/export_api.py not flagged
```

Sandbox: Python 3.11.9, ruff 0.13.0, pytest 8.4.2 — all runnable locally [OBSERVED]. Code kept
3.11-compatible; CI runs 3.12 (authoritative).

## Deviations

1. **One known-red consumer routed to the orchestrator (forbidden file).**
   `tests/cad/test_glb_writer.py::test_as5_not_wired_into_the_app` asserts NO `app/**` file contains
   the substring `glb_writer` (it was written when the writer was standalone). PKT-D's whole purpose
   is to WIRE the writers, so `export_service.py` now imports `glb_writer` — the assertion is now
   false by design and cannot be satisfied without removing the wiring. `test_glb_writer.py` is a
   FORBIDDEN path for this packet, so I did not edit it. **Required orchestrator action:** update that
   one test to reflect that PKT-D (`app/cad/export_service.py`) now legitimately imports `glb_writer`
   (e.g. allow `app/cad/export_service.py` as the expected importer, or drop the assertion). The DXF
   and PDF writers have NO equivalent grep-based unwired test, so only this one is affected.
2. **No in-repo per-caller route rate limiter existed to reuse.** The packet/plan say "reuse the
   repo's existing rate-limit mechanism — see lot_geometry.py / properties.py", but those `rate_limited`
   states are UPSTREAM-connector 429/503 handling (SODA/ArcGIS retry budgets), not an in-route
   per-caller limiter. I added a minimal stdlib in-process sliding-window limiter in `export_api.py`
   (`_RateLimiter`; per client-host key, monotonic clock, window/limit read live, bounded key set).
   Zero new dependencies. This is the DB-061(i) route-level limiter that the plan says was still
   REQUIRED at the wiring seam.
3. **`ruff check .` (whole services/api) still reports 4 E501s** — all in OTHER packets' seed
   placeholder docstrings (`app/api/v1/scene_api.py`, `app/api/v1/dxf_import_api.py`,
   `app/scenario/scene_assembler.py`, `app/drawings/dxf_import.py`), which are forbidden/out-of-scope
   for me and will be replaced by M5-T107/M5-T108. My six files are clean (`All checks passed!`).
4. **DXF/GLB writers embed their own FIXED provenance; only PDF embeds `generated_at`.** The
   byte-frozen DXF and GLB writers take no `generated_at`/`address`/`bbl`; they stamp fixed
   "PROPOSED - NOT A CITY RECORD" / "GENERATED BUILDING OPTION" (DXF) and "Proposed - not a city
   record" (GLB `asset.generator`/`extras`). The caller `generated_at` is therefore recorded in the
   service `provenance` dict and used deterministically in the filename token; it reaches embedded
   file bytes only via the PDF title block. Deterministic-no-clock holds for all three formats.
5. **GLB massing = a single base->roof extrusion (DB-054(m) satisfied by construction).** Per-floor
   bands are NOT emitted as stacked prisms, so there are no coincident interface caps to dedupe; the
   choice is disclosed in `provenance["glb_massing"]`. Caps are fan-triangulated from the first
   footprint vertex; a self-intersecting/highly concave footprint may yield a degenerate cap, which
   the GLB writer refuses (`degenerate_triangle`, reconciled). A robust polygon triangulator lives in
   `app/scenario/massing_model.py` (forbidden here / owned by M5-T106/T107).

## Backlog-rider disposition

- **DB-057(d)** raw-length cap before normalization — DONE (`_raw_ring_length` before any coercion;
  proven with non-numeric over-cap vertices).
- **DB-059(e),(h)** reconcile GLB-raise/PDF-return + redact — DONE (`_reconcile`; no caller text in
  any refusal).
- **DB-054(m)** GLB coincident-cap dedupe/disclose — DONE (single extrusion + disclosure).
- **DB-061(i)** off-event-loop cancellable job + per-request deadline + per-caller rate limit — DONE.
- **DB-072(d)** single-word internal-separator claim variants still pass (inherent to the shared
  collapse-to-space key; not a regression) — the service reuses the accepted shared screen unchanged;
  NOTED, not fixed in-packet. **DB-072(e)** NFKC/confusable folding + concatenation screening: caller
  text stays ASCII-screened per field; not relaxed here. **DB-072(g)/DB-059(h)** export-seam redaction
  — DONE.
- **DB-075(a)** `_coerce_vertex` broadened catch + hostile-`__float__` test — DONE. **DB-075(b)**
  end-to-end typed refusal through the real route — DONE (`test_422_typed_refusal_through_the_real_route`).
  **DB-075(c)** verify ISO 32000-1 §7.3.4.2 escaping citation: NOT independently verified here (no
  standard access on the thin client); the citation stays `[recalled - verify]` in `pdf_sheet_writer`;
  routed to G3. **DB-075(d)** 120-char cap applies to the raw field value not the composed title-block
  line — unchanged/NOTED. **DB-075(e)** the owner-sample suite is 10 tests (not 11) — CONFIRMED
  (`test_cad_owner_samples.py`: 10 passed).
- **DB-065(a)** filename token empty/only-`.`/`-` -> server default — DONE (fallback to correlation id).

## Discoveries (D-069; for the orchestrator to record)

- **DISC-1 (blocking-for-the-wave, routed above):** `test_glb_writer.py::test_as5_not_wired_into_the_app`
  must be updated at this wiring seam (forbidden path for the producer). One-line fix by the orchestrator.
- **DISC-2 (watch):** there is no shared in-route per-caller rate-limiter primitive; PKT-D's
  `_RateLimiter` is the first. If PKT-E (scene route) and PKT-F (import route) each need one, consider
  promoting a shared limiter module rather than three copies (each stdlib, per DB-061(i)).
- **DISC-3 (watch):** the export service embeds `generated_at` only via the PDF writer; if DXF/GLB
  downloads must carry the caller `generated_at`/scenario id in-file, that needs a (byte-frozen)
  writer change in a later packet, not the export service.

END-OF-REPORT
