# M5-T091 producer report: PDF site-plan sheet writer hardening (DB-053 a-d)

- Producer: backend-engineer (orchestrator-dispatched subagent). Worktree `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t091`, branch `task/M5-T091-pdf-writer-hardening`.
- Base / parent: `114e5e56e158d6f263e58a314c383ea62ee7eff4` (verified with `git rev-parse HEAD` before any edit; toplevel verified as wt-m5t091; status clean).
- Commit: ONE commit on top of the parent. Its sha goes in the hand-back message, because a report cannot contain its own commit's sha.
- Requested status: **awaiting_gate**. Not wired to anything: no route, no `main.py`, no `app/cad/__init__.py` change.
- Evidence tags: [OBSERVED] means I ran it in this session. [HARVEST] means it has to be run elsewhere, with the recipe given.

## IMPLEMENTATION

Files changed (exactly the allowed paths):
- `services/api/app/cad/pdf_sheet_writer.py`: 400 to 506 physical lines (about 408 SLOC; warning threshold is 600).
- `services/api/tests/cad/test_pdf_sheet_writer.py`: 19 to 180 collected tests.
- `project-control/reports/M5-T091-producer-report.md`: this file.

Module changes (line anchors refer to the committed file):
- (a) Malformed input returns a typed refusal and never raises.
  - `render_site_plan_pdf` refuses an argument that is not a `SitePlanInput` with `invalid_input` (:162).
  - `_validate_ring` (:260) requires the ring to be a real sequence. `_is_sequence` (:256) and `_TEXT_LIKE` (:218) exclude str, bytes, bytearray and memoryview. Anything else gets `invalid_ring`. The ring length is checked before any per-vertex work, and the original oversize detail text is kept.
  - New `_coerce_vertex` (:291) handles each vertex:
    - If the vertex is not a sequence, or does not have exactly 2 items, the result is `invalid_ring`.
    - If a coordinate is not a `numbers.Real`, or is a `bool`, the result is `non_numeric_coordinate`.
    - If `float()` overflows (an int too large for a float), the result is `oversize_input`.
    - The existing checks then run in their existing order: finite first, then the 1e8 magnitude bound.
- (b) Non-finite guard at the number formatter.
  - `_num` (:447, guard :453) raises the private carrier `_RenderRefused` (:138) holding `SitePlanRefusal("non_finite_value", ...)`.
  - `render_site_plan_pdf` wraps `_build_content` and `_assemble_pdf` and returns the carried refusal (:211). The carrier never escapes the public function.
- (c) Claim-class screen on caller text.
  - `CLAIM_CLASS_WORDS` is imported read-only from `app.cad.dxf_writer` (:54).
  - `_screen_caller_text` (:224) runs before ring validation and before anything is drawn (:164).
  - It checks `address`, `bbl`, `generated_at` and `generator_version`. A value that is not a str gets `invalid_text`.
  - Each value is matched (substring, case-insensitive) in two forms: as given, and in the ASCII-sanitised form the sheet would print. In both, runs of non-`[A-Z0-9]` characters are collapsed to one space (`_claim_key` :252, `_CLAIM_SEPARATOR_RUN` :221). This catches `AS_OF_RIGHT`, a double-spaced `MAXIMUM  ALLOWED`, a tab-separated variant, and so on.
  - The match set is a superset of the DXF writer's own `word in text.upper()` check.
  - A refusal detail names the field and the barred word. It never echoes the caller's text.
- (d) Escaper. There is no behaviour change here: it was already correct, and the gap was test coverage. Sanitising was pulled out into `_ascii_sanitise` (:442) so the escaper (:424) and the screen share one sanitising rule. The escaper is still the only path text takes into the content stream. Output bytes are identical (see AS-5).

Why I imported the word set instead of copying it (packet choice):
- There is one source of truth, so the two writers cannot drift apart.
- `dxf_writer` is accepted, uses only the standard library, and does not import `pdf_sheet_writer`, so there is no import cycle.
- The packet allows this read-only import.
- The pin is enforced in the tests. `test_claim_word_set_is_the_dxf_writers_pinned_set` (test:458) checks:
  - identity (`writer.CLAIM_CLASS_WORDS is dxf_writer.CLAIM_CLASS_WORDS`), so a silent private copy fails;
  - equality with a hardcoded literal tuple (test:428), so removing or editing a word in the DXF module also fails. This follows the T081/T085 G4 lesson: a by-value import alone would be tautological.
- Cost: the PDF writer now depends on the DXF writer module. A shared vocabulary module would be cleaner (see DISCOVERIES D1).

## Per-scenario evidence

**AS-1: malformed vertex** [OBSERVED]
- `test_malformed_vertex_is_a_typed_refusal_never_raises` (test:337) covers 19 malformed vertices, each placed in both the lot ring and the building ring (38 cases):
  - non-numeric: `"a"`, a numeric string `"1.5"`, `None`, `True`, `1j`, `[1.0]`, `Decimal`;
  - wrong arity: `()`, `(1.0,)`, `(1.0, 2.0, 3.0)`;
  - not a sequence: `5`, `None`, `1.5`, `"12"`, `b"\x01\x02"`, a set, a dict, `object()`;
  - an int beyond the float range: `10**400`.
- `test_malformed_lot_ring_container_is_a_typed_refusal` (test:348): None, int, float, str, bytes, object, dict, set, generator.
- `test_non_spec_argument_is_a_typed_refusal` (test:361).
- `test_non_string_caller_text_is_a_typed_refusal` (test:371).
- `test_any_hostile_field_value_returns_bytes_or_refusal` (test:388): 15 hostile values tried in each of the 6 fields; every call returns bytes or a refusal.
- Accepted behaviour kept: `test_list_rings_and_int_coordinates_still_render_identically` (test:354) shows list rings with int coordinates produce the golden bytes. The original `test_invalid_rings_are_typed_refusals` (test:217) and `test_too_many_vertices_refused` (test:223) are unchanged and green.
- Mutants M1a-M1d all go RED. Under M1a/M1b/M1d the failing cases fail by raising (`ValueError: could not convert string to float: 'a'`, `TypeError: object of type 'int' has no len()`, `TypeError: 'set' object is not subscriptable`, and so on) or by silently accepting a numeric string or bool (`assert False`).

**AS-2: finite guard** [OBSERVED]
- `test_number_formatter_refuses_non_finite` (test:399): `_num` refuses nan, inf and -inf with `non_finite_value`.
- `test_non_finite_drawing_number_is_a_typed_refusal_not_a_token` (test:407): `_TITLE_FONT_PT` or `_SHEET_W` is forced to nan/inf, so the value reaches `_num` inside both `_build_content` and `_assemble_pdf`. The call returns a refusal and no bytes.
- `test_number_formatter_unchanged_for_finite_values` (test:417): formatting of finite values (including -0.0 collapse and trimming) is pinned.
- Mutant M2 goes RED on 9 cases.

**AS-3: claim screen** [OBSERVED]
- `test_claim_word_in_caller_text_is_refused_nothing_emitted` (test:465): 11 hardcoded words across the 4 text fields (44 cases).
  - The reject code is `claim_class_word`.
  - The detail names the field and does not contain the caller's text.
  - A spy on `_build_content` (fixture test:445) records **zero** calls, so nothing was drawn.
- `test_claim_word_separator_variants_are_refused` (test:486): 6 variants, including `"AS \u017fOF RIGHT"`, which prints as `AS ?OF RIGHT`. That case proves the printed form is screened too.
- `test_clean_caller_text_still_renders` (test:494) covers near-misses such as `12 PERMIT ST` and `1 LEGACY PL`. It also shows the spy is live (1 call), so the zero-call assertions are not vacuous.
- The word-set pin is at test:458.
- Mutants M3a-M3d all go RED.

**AS-4: unbalanced parens** [OBSERVED]
- `test_unbalanced_parens_round_trip_through_writer_and_reader` (test:517) runs 10 unbalanced texts through both the address and BBL fields: `12 MAIN ST (REAR`, `12 MAIN ST REAR)`, `(`, `)`, `)(`, `((`, `a)b(c`, a trailing backslash, `\(`, `\)`.
- In every case the strict reader accepts the container and the content, and exactly one text run equals the input.
- The reader is the in-repo `app.documents.extraction` reader, used read-only through the existing sideload under 3.11.
- `test_paren_skipping_escaper_mutant_breaks_unbalanced_roundtrip` (test:542) is a committed in-process proof that the fixtures have teeth. It covers escapers that skip `(`, skip `)`, or skip both (the G4 "EB" survivor).
- The existing balanced-paren test (test:237) is unchanged.
- Mutants M4a-M4d all go RED.

**AS-5: scope** [OBSERVED]
- Golden **not** re-anchored: `_GOLDEN_SHA256` is still `c38360f9b803299c75dd837ec65de3e3a4dc046a11aa2bcb386fe74aa5312db2` (test:40), and `test_golden_sha256` passes. Output bytes for valid input do not change.
- All 19 original tests still pass.
- Zero new dependencies: new imports are the standard-library `numbers`, `re` and `collections.abc` plus the in-repo `app.cad.dxf_writer`. No lockfile or requirements change.
- Not wired: `grep` for `pdf_sheet_writer|SitePlanRefusal|render_site_plan_pdf` in `*.py` matches only the module, its test, `app/cad/__init__.py` (docstring mention) and `tests/cad/test_dxf_writer.py:355` (a comment).
- `git status --short` before the commit showed only the two code files plus this report.
- `python -m pytest tests/cad -q` (cwd services/api): `204 passed in 2.03s`, so the sibling DXF and GLB suites are unaffected by the new import.

## Mutation table [OBSERVED]

- Harness: `m5t091/harness.py` in the session scratchpad, outside the repo.
- How it works: it applies one textual mutation to the module source **in memory**, installs it as `app.cad.pdf_sheet_writer` with the real `__file__` (so the reader sideload still resolves), and runs the whole test file in-process.
- Every run reported `tests_bound_to_mutant: true` and `disk_source_unchanged: true`.
- cwd `services/api`, command `python <harness> <id>`.
- Baseline and restore: `M0-control` gives 180 passed / 0 failed. The final documented pytest run (below) is 180 passed.

| Mutant (named mutation) | Result | Failing tests (count) |
|---|---|---|
| M1a remove numeric-type guard in `_coerce_vertex` | RED 16 | malformed_vertex 14, hostile_field 2 |
| M1b remove vertex sequence guard | RED 18 | malformed_vertex 16, hostile_field 2 |
| M1c remove vertex arity check | RED 6 | malformed_vertex 6 |
| M1d remove ring-container guard | RED 8 | malformed_lot_ring_container 6, hostile_field 2 |
| M2 remove `_num` finite guard | RED 9 | number_formatter_refuses_non_finite 3, non_finite_drawing_number 6 |
| M3a screen disabled (`text_refusal = None`) | RED 66 | claim_word_in_caller_text 44, separator_variants 6, non_string_caller_text 16 |
| M3b screen the raw form only (drop printed form) | RED 1 | separator_variants 1 (the `\u017f` case) |
| M3c no separator normalisation (plain `upper()`) | RED 5 | separator_variants 5 |
| M3d screen the address only | RED 45 | claim_word_in_caller_text 33, non_string_caller_text 12 |
| M4a EB: drop paren escaping, keep backslash | RED 19 | unbalanced_round_trip 18, golden 1 |
| M4b escaper skips a lone `(` | RED 28 | unbalanced_round_trip 20 (+8 existing reader/golden tests) |
| M4c escaper skips a lone `)` | RED 28 | unbalanced_round_trip 20 (+8 existing reader/golden tests) |
| M4d drop backslash escaping | RED 8 | unbalanced_round_trip 6, special_characters 1, escaper_bypass 1 |

M4a note: before this packet, EB survived every semantic test and was caught only by the golden (because `GRID N (EPSG:2263)` then emits unescaped balanced parens). The new unbalanced fixtures now catch it directly.

## Self-checks (verbatim) [OBSERVED]

cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t091\services\api`, command `python -m ruff check .`:
```
All checks passed!
exit=0
```

cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t091\services\api`, command `python -m pytest tests/cad/test_pdf_sheet_writer.py -q`:
```
........................................................................ [ 40%]
........................................................................ [ 80%]
....................................                                     [100%]
180 passed in 1.38s
exit=0
```

cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t091`, command `python tools/modularity_check.py --check`. Output as printed; no `app/cad` entry. There are 23 warnings, the same count as before the change.
```
selected 486 files; failures 0; warnings 23
  warn symbol_ceiling: apps/web/src/lib/surveyReview/types.ts - many top-level symbols (approximate count); a signal, not a verdict
  warn review_signal: services/api/app/api/v1/outline_bridge.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: services/api/app/api/v1/scenario_analysis.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: services/api/app/connectors/dcm_street_centerline_arcgis.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: services/api/app/connectors/dtm_condo_soda.py - above the justification threshold; record a cohesion justification in review
  warn symbol_ceiling: services/api/app/connectors/mappluto_geometry_arcgis.py - many top-level symbols; a signal, not a verdict
  warn review_signal: services/api/app/connectors/wide_street_buffer_engine.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: services/api/app/drawings/sheet_reader.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: services/api/app/rules/integration.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: services/api/app/scenario/breakeven.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: services/api/app/scenario/max_envelope.py - above the justification threshold; record a cohesion justification in review
  warn symbol_ceiling: tools/agent_supervisor/cli.py - many top-level symbols; a signal, not a verdict
  warn review_signal: tools/agent_supervisor/codex_reviewer.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: tools/agent_supervisor/durable_state.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: tools/agent_supervisor/evidence.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: tools/agent_supervisor/gate_wave.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: tools/agent_supervisor/next_task.py - above the warning threshold; consider the module boundary before growing it further
  warn symbol_ceiling: tools/agent_supervisor/policy.py - many top-level symbols; a signal, not a verdict
  warn review_signal: tools/agent_supervisor/process.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: tools/agent_supervisor/recovery_probes.py - above the justification threshold; record a cohesion justification in review
exit=0
```

[HARVEST] CI 3.12 is the authority. Local Python is 3.11.9 with pytest 8.4.2; CI uses 3.12 with the locked pytest 9.0.3. Under 3.12 the round-trip tests take the plain-import path of `app.documents.extraction` instead of the sideload. Recipe: the api CI job at the pushed head, `cd services/api && python -m pytest tests/cad/test_pdf_sheet_writer.py -q`, expected `180 passed`.

## Deviations (behaviour changes to off-contract input; all disclosed)

1. **Numeric strings, `bool` and `Decimal` coordinates are now refused** (`non_numeric_coordinate`).
   - Before, `float()` coerced them silently (for example `("0", "1.5")` rendered).
   - The declared type is `float`, no test or caller relied on the old behaviour, and parse-to-float belongs to the wiring layer (the same position as DB-054(o)).
   - Ints, floats, `Fraction` and numpy real scalars are still accepted, and list rings still produce identical bytes (test:354).
2. **Rings and vertices must be sequences.**
   - Generators, sets, dicts and numpy arrays used to be materialised through `tuple()` (a set gave an arbitrary vertex order). They now get `invalid_ring`.
   - The declared type is a tuple; the canonical connector rings are lists or tuples of float pairs (`mappluto_geometry_arcgis.py:588-590`).
3. **Caller text that is not a str is refused** (`invalid_text`). Before, it was printed through the f-string repr (for example `SITE: None`).
4. **Five new reject codes:** `invalid_input`, `non_numeric_coordinate`, `invalid_text`, `claim_class_word` (the same code name the DXF writer uses), and `non_finite_value`. Existing inputs keep their existing codes and their order of precedence.
5. **Refusal precedence:** the text screen runs before ring validation. This only matters when both the text and the geometry are bad; the text refusal wins.

## DISCOVERIES (D-069 routing; not fixed here)

- D1: `CLAIM_CLASS_WORDS` lives in `dxf_writer.py`, but now two writers use it, and `glb_writer.py` (M5-T092) may need it too. A shared honesty-vocabulary module under `app/cad/` would remove the PDF-on-DXF dependency. That needs a packet that grants a new path and an update to the `__init__` docstring.
- D2: Caller text has no length bound. A very long address grows the content stream without limit and runs off the title block, because there is no wrapping or clipping. A length cap plus a visual-fit rule is a pre-wiring rider.
- D3: Substring matching refuses legitimate text that merely contains a barred word, for example `PARALEGAL`, `ILLEGAL`, or a business name with `APPROVED`. Refusing is the fail-closed direction, but the wiring packet must show that refusal honestly to the user. It must not fall back to printing.
- D4: Limits of the screen:
  - letter-spaced text (`A P P R O V E D`) and ASCII look-alikes (`APPR0VED`) are not caught;
  - cross-field combinations on adjacent lines (address `MAXIMUM`, BBL `ALLOWED`) are not caught.
  These are bounded by the fixed `PROPOSED - NOT A CITY RECORD` stamp that is always printed.
- D5: The input contracts now differ. The DXF writer's `_normalize_ring` still coerces numeric strings with `float()`, while the PDF writer refuses them. The CAD export wiring packet should pick one rule for both writers.
- D6: Environment note. The session scratchpad directory holds a stray `inspect.py` that shadows the standard-library `inspect` for any script run from that directory, which broke pytest's import. Harness scripts must live in their own subdirectory.
