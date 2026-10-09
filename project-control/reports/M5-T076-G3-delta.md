# M5-T076 — G3 delta re-attestation (code-reviewer, read-only)

> Transmission history: returned complete in ONE message (END-OF-REPORT present). Saved
> verbatim by the orchestrator (transport entity-decoding only). This delta follows the
> full G3 FAIL review in M5-T076-G3.md; the two together are the G3 record — the FAIL
> report carries the findings, this delta carries the per-required-item verification at
> the corrected head and the PASS.

**M5-T076 — G3 delta re-attestation at `ccff99e9c581743bfa3eff4bfd44ec11abe197b6`**

Head verified (`git rev-parse HEAD` matches). Engine bound re-verified by blob, not by diff absence: `git rev-parse HEAD:services/api/app/scenario/max_envelope.py` = `f0abf88479d078d8ec7e88d4c2b1942fd69c040d`, identical to the pre-T076 parent. Re-ran both self-checks myself from `services/api`: **55 passed** (2.97 s) and `ruff check .` → All checks passed. `modularity_check --check` → failures 0, warnings 22, new module now 328 lines and still unwarned.

**Per required item**

- **F1 — VERIFIED.** `max_envelope_api.py:357-382`: provider resolution and the threadpool hop are both inside `try/except Exception` → `logger.error(... stage=derive_lot_geometry ...)` + `_internal_error_500`. Re-ran my original repro (provider raising `ValueError`): now `500 / state=internal_error / X-Correlation-ID present` — previously a bare `Internal Server Error` with no header. `test_500_when_the_lot_geometry_provider_raises_unexpectedly` covers it.
- **F2 — VERIFIED.** `_should_derive_lot_geometry` (`:162-180`) now derives only when the key is absent, `None`, or an empty list; every other type returns `False` and stays on the 422 path. `test_malformed_segments_refuse_identically_with_and_without_a_bbl` parametrizes `"abc"`, `42`, `{"id": "L-S"}`, `True` — covering the bool case I did not raise.
- **F3 — VERIFIED.** Both suites now load the recorded packs via `_MPG_FIXTURES`. `test_recorded_single_lot_derives_but_is_honestly_unfittable` (route) is the derived-but-unfittable path I flagged; `test_recorded_holed_lot_excludes_every_hole_vertex` asserts the exact numbers my probe produced (320 exterior segments, 143 hole vertices, `endpoints == exterior_vertices`, `not (endpoints & hole_vertices)`) with the `polygon` vs `polygon[0]` mutant named. Fixture-conditional AS-2 is disclosed in `M5-T076-evidence-map.json` under an `[ORCH-CORRECTED per M5-T076-G3 F6/F3]` tag.
- **F4 — VERIFIED.** New `GEOMETRY_OVER_CAP` outcome; `_exterior_ring_segments` returns `(segments, reason)` with `_RING_DEGENERATE`/`_RING_OVER_CAP` kept apart, and the over-cap detail now states the official data is not at fault. `test_over_cap_and_unusable_geometry_never_conflate_the_two_causes` and `test_recorded_multipolygon_is_over_cap_never_invalid_official_data` pin it on real MPG07.
- **F5 — VERIFIED.** `production_lot_geometry_provider()` (`:311-325`) constructs and caches the client at resolution time and the returned closure constructs nothing; the DB-039(i) doctrine comment cites the sibling `_effective_registry`. The route resolves it on the event loop with a matching comment. `test_production_provider_builds_its_client_on_resolution_not_per_call` covers it.
- **F7 — VERIFIED.** `test_module_never_imports_the_display_only_outline_connector` parses the module's own source with `ast` and asserts `mappluto_lot_outline` appears in no import while the 2263 connector does — a direct isolation proof rather than the coordinate-magnitude inference.

**One new concern introduced by the rework (non-blocking).** The three spellings of "no geometry supplied" no longer behave alike on the *failure* path. With a BBL and a failing provider: absent → 200 `lot_geometry_unsupported`; `[]` → 200 `lot_geometry_unsupported`; **`null` → 422 `validation_error` on `lot.lot_line_segments`**, because `_build_lot_context` rejects `None` when derivation leaves it in place. The new docstring explicitly treats absent/`None`/empty-list as equivalent, and `test_absent_or_null_segments_with_a_bbl_still_derive` exercises only the success path, so the suite is green over the gap. This is fail-closed and not a regression (`null` without a BBL is 422 today too), so I am not blocking on it — but either normalize `None` to `[]` when derivation fails, or drop `None` from the derivable set so the docstring matches behavior.

**G3 DELTA VERDICT: PASS**

END-OF-REPORT
