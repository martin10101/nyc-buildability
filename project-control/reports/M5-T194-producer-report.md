# M5-T194 (M5-T173 part B4) producer report - drawn-content manifest

Builder: backend-engineer. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a0df7849c15c5732f`.
Base head reset to `b9e9d563a8b9e869bcaf4af8862c9f3d411de645` (head of `task/wave29-scenario-drawings` at dispatch).

## What changed and why

Audit 2026-10-15c section 3: a data field is not proof a drawing was rendered. H4 R1-R3 found two
hard-coded `return False` predicates (`drawings_embed.site_plan_draws_placed_footprint`,
`page_evidence._area_illustration_drawn`) plus a data-field read in the page-5 chart. This part adds the
H4/H5 DrawnManifest and threads an explicit drawn state into the page-5 chart status and the appendix
area-illustration method, so each claim can read rendered content. All new behaviour is behind keyword
arguments that default to the legacy output, so an unwired caller is byte-identical (the serial wiring is
part W; builder.py and page_location.py are forbidden here and untouched).

1. NEW `services/api/app/drawings/report/manifest.py` (66 SLOC): frozen `DrawnManifest`
   (`site_plan_drawn`, `site_plan_draws_footprint`, `section_drawn`,
   `area_illustration_state in {'zones','bar',None}`) and
   `build_manifest(*, site_plan, area_illustrations=(), sections=())`. Derived from the rendered
   `Embedded` values ONLY, no results field and no arithmetic: `site_plan_draws_footprint =
   site_plan.is_drawing and 'illustrative_footprint' in site_plan.kinds_drawn`; the area state reads the
   kernel's own SVG `data-role` attributes (`area_zone_apartment`/`area_zone_other` -> 'zones';
   `area_bar_apartment`/`area_bar_other` -> 'bar'; else None). The `illustrative_footprint` kind and the
   kernel data-roles are the only cross-part contracts (part W pins them; the kit style for that kind is
   added by part B1).
   - Decision (reported): `area_illustrations`/`sections` default to `()` (additive; the packet signature
     lists them without defaults). A caller passing all three behaves identically; defaults only let W / a
     test omit an absent list. `site_plan` has no default.
2. `drawings_embed.py` (+20 SLOC, cap +40): `Embedded` gains `kinds_drawn: tuple = ()` filled by
   `_from_result` from the kit `Drawing.kinds_drawn`, and `embed_map` reads it from the map result too
   (the page-4 close frame is a map). HTML is unchanged: `kinds_drawn` is never rendered.
   `allowance_bar_chart_svg(..., footprint_drawn=None)`: `None` keeps the legacy
   `site_plan_draws_placed_footprint()` path; `True`/`False` select "Shown on the site plan" /
   "Worked out; not drawn". `embed_map(..., placed_footprint=None)` forwards the keyword only when given;
   on a render failure it re-renders without the overlay AND the footprint and carries a note naming what
   was not drawn (the existing zoning-line note for the overlay; a new footprint note). The legacy
   `site_plan_draws_placed_footprint` is KEPT (deletion is part W's).
3. `page_option_comparison.py` (+2 SLOC): `render(..., footprint_drawn=None)` and `_chart(...,
   footprint_drawn=None)` pass it to the chart; `building_not_placed(results)` is still the engine-placed
   signal.
4. `page_evidence.py` (+17 SLOC): `render(..., illustration_state=None)` and
   `_area_illustration_method(results, illustration_state=None)` via a new
   `_area_illustration_drawing_clause` helper: `None` keeps the legacy `_area_illustration_drawn(results)`
   path (byte-identical); `'zones'` -> "it is shown as zones inside the placed building footprint on the
   scenario sheet"; `'bar'` -> "it is shown as a proportional bar on the scenario sheet"; any other
   (explicit not-drawn) state -> today's "not yet drawn" clause WITHOUT reading the legacy predicate. The
   method's figures (share, measure, conversion) still come from the document. `_area_illustration_drawn`
   is KEPT (deletion is part W's).
5. NEW `services/api/tests/drawings/report/test_report_drawn_manifest.py` (8 tests, S1-S7 + section flag).

Handoff note for part W: the manifest's not-drawn state is `None`, but `_area_illustration_method`'s
`illustration_state=None` means "use legacy". After W deletes `_area_illustration_drawn`, W must either
pass an explicit not-drawn value (any non-None, non-'zones'/'bar' value, proven here) for the manifest's
`None` state, or rewrite the `None` branch. The explicit-not-drawn branch is already implemented and tested
so W can rely on it.

## Owner-standard / scope

No zoning arithmetic in renderers; every figure still comes from the document via the readers. No measurement
bases mixed. No rooms/units/counts drawn or claimed. No hardcoded property numbers in the manifest or the
clause (literals are the kernel's own data-role names and the kit style-kind contract). No evidence record or
`review_register/register.json` pins any file edited here (verified by grep; H5 findings 7 and 11). NB-04
`code_current=False` is a pre-existing DB-283 note on `close_frame_dimensions.py` (not touched; part W owns
revision 4) and is "reported, not failed".

## Checks (direct exit codes; lanes venv; `PYTHONDONTWRITEBYTECODE=1`, `pytest -p no:cacheprovider`)

- `cd services/api && python -m ruff check .` -> `All checks passed!` EXIT 0.
- `cd services/api && flock heavy-run.lock python -m pytest -q tests/drawings/report/test_report_drawn_manifest.py`
  -> `8 passed in 1.08s` EXIT 0.
- `cd services/api && flock heavy-run.lock python -m pytest -q tests/drawings/report`
  -> `235 passed, 1 warning in 84.49s` EXIT 0 (S1: every existing report test passes unedited, incl.
  test_report_comparison.py:107-134 and test_report_appendix.py:204-213).
- `python tools/modularity_check.py --check` -> EXIT 0 (no file I touched flagged; manifest.py 66 SLOC < 150;
  drawings_embed.py 259 (+20, cap +40); page_evidence.py 219 (+17, cap +40); page_option_comparison.py 93).
- `python3 tools/research_record_check.py --check` -> `PASS` EXIT 0 (NB-04 pre-existing note only).
- `python3 scripts/lanes/check_lane_paths.py --coverage` -> `LANE COVERAGE PASS: 10920 file(s)` EXIT 0.

## Mutation proof (revert behaviour -> test fails -> restore), run without the lock (single-file, <1s each)

1. manifest `site_plan_draws_footprint` -> forced `False`: `test_s2` FAILED
   (`assert (True and False)` on `site_plan_draws_footprint`). Restored.
2. `allowance_bar_chart_svg` -> ignore `footprint_drawn` (always legacy): `test_s2` FAILED
   ("Shown on the site plan" absent; row read "Worked out; not drawn"). Restored.
3. `page_evidence` zones clause -> replaced with "it is shown MUTATED": `test_s3` FAILED
   (zones sentence absent). Restored.
4. manifest zone-role detection disabled (`if False and ...`): `test_s3` FAILED (`assert None == 'zones'`).
   Restored. `grep MUTATION services/api/app/drawings/report/*.py` -> NO MUTATIONS REMAIN; full file re-run
   `8 passed`.

## Report print comparison

Not applicable: this part changes no rendered report page. Every new behaviour defaults to the legacy output
(byte-identical, proven by S1 and the 235-test folder run); the manifest is wired into the live report by the
serial part W. No PDF print was required or produced for this part.

## Limitations / stopped on

- Nothing stopped. No file outside the allowed paths was needed.
- The `illustrative_footprint` kit style kind does not exist at this head (part B1 adds it); the manifest
  carries the literal as the cross-part contract, so no kit import/assert is possible yet (left to part W's
  integration test, per RISK 1).
