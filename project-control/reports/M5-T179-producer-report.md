# M5-T179 producer report — appendix scope note vs printed context maps

Builder (backend-engineer). Claim head `6cc452af0`. D-094 R137 (page 7 lists "Context
maps" under "Not yet in this report" even when the report prints its maps) and R083
(before/after of the changed page). Presentation only — no fact, reading, calculation
or verification label changes (D-093).

## What changed (allowed paths only)

- `services/api/app/drawings/report/builder.py` — line 92 passes the `maps_present`
  it already computes (`surroundings.available`) into `page_assumptions.render`
  (previously only page 1 / `page_decision_summary.render` received it).
- `services/api/app/drawings/report/page_assumptions.py` — `render` and
  `_material_exclusions` take `maps_present: bool = False` and hand it to
  `coverage.coverage_groups`; the default keeps every other caller unchanged. The
  docstring that said "this page is built without the map context" is corrected to say
  "Context maps" is excluded only when the report does not print its maps.
- `services/api/tests/drawings/report/test_report_scope_note_maps.py` — new test
  (placeholder replaced): S1, S2 (parametrized over every valid results fixture), S3.
- `coverage.py` not edited (it already supports `maps_present`).

## Scenario → test table

| Scenario | Test | Result |
|---|---|---|
| S1 benchmark + map context: scope note drops "Context maps"; every other name stays, same order/words | `test_s1_scope_note_drops_context_maps_when_maps_are_printed` | PASS |
| S2 every valid fixture, no map context: "Context maps" still listed (report byte-identical to claim head — proven below) | `test_s2_scope_note_keeps_context_maps_without_a_map_context` (12 params) | PASS (12) |
| S3 benchmark: maps-present vs no-maps scope note differs only by "Context maps" | `test_s3_benchmark_scope_note_difference_is_only_context_maps` | PASS |
| S4 mutation: revert builder pass-through → S1 fails; restore → passes | see mutation below | PASS |

S1/S3 run through `build_report_html`, so the builder pass-through is exercised (S4).
Expected names are read from `coverage.coverage_groups`, never retyped.

## S2 byte-identity proof (script over every valid fixture)

Frozen claim head extracted with `git archive 6cc452af0` into scratch. Built each of
the 12 valid results fixtures WITHOUT a map context at the claim head and after the
change; compared sha256 of the full report HTML. All 12 BYTE-IDENTICAL:

```
diff(baseline nomap digests, after nomap digests) -> no differences
S2 RESULT: all nomap outputs BYTE-IDENTICAL to claim head
```

Example digest (unchanged both sides), `recorded_215_16_northern_journey`:
`7964f53cdb40457a2d5b017307e0918f3b984dd990a92f61ce5e741a2ac1cb0f`.

## S3 byte proof (benchmark with its recorded window map context)

Built the benchmark WITH `recorded_pack_provider(benchmark_215_16_northern_window)`
(+`LANE_E_ENABLED=1`) at the claim head and after the change:

- claim head: `3a178918e01647a3e8ac5af4c742497c8cdc6fa4d2780cc715712a34f7d13662`
- after:      `ee751109b010d21dfe1a6e4dfb8105f9d5c848f0ee648238a1773e864897fd24`

Exact delta (common prefix 125497 B + common suffix 14432 B identical):

```
baseline-only middle: '; Context maps'
after-only middle   : ''
baseline len: 139943  after len: 139929  delta: -14
```

The ONLY difference is removal of the 14-byte `; Context maps` (the entry and its
"; " separator) from the appendix scope note. The `diff` reports a single hunk
(`818c818`). This is the before/after picture for page 7 (R083): the scope note goes
from "...; Financial analysis inputs (held); Context maps" to "...; Financial analysis
inputs (held)"; nothing else on the page moves.

## Mutation proof (S4)

Reverted line 92 of builder.py to `page_assumptions.render(results, ident, env=env)`:

```
FAILED ...::test_s1_scope_note_drops_context_maps_when_maps_are_printed
E  AssertionError: assert 'Context maps' not in [... 'Financial analysis inputs (held)', ...]
1 failed   MUTATED_S1_EXIT=1
```

Restored the pass-through:

```
1 passed   RESTORED_S1_EXIT=0
```

## Checks (lanes venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider)

| Check | Exit |
|---|---|
| `python -m ruff check .` (services/api) | 0 — All checks passed! |
| `pytest -q tests/drawings` (services/api) | 1 — 1 failed, 1178 passed, 6 skipped, 149.90s |
| new-file `pytest tests/drawings/report/test_report_scope_note_maps.py` | 0 — 14 passed |
| `python3 tools/modularity_check.py --check` (root) | 0 — 799 files, 0 failures, 33 pre-existing warnings (none on my files) |
| `python3 scripts/lanes/check_lane_paths.py --coverage` (root) | 0 — 10410 files, each owned by one lane |

Heavy-run serialization (coordinator rule): checked `pgrep -af pytest` before the
heavy run — none running, so I did NOT wait.

## The one heavy-suite failure is OUTSIDE my allowed paths — scope correction needed

`tests/drawings/report/test_report_pages.py::test_q3_coverage_and_maps_with_and_without_a_map_document`
fails at line 652: `assert "Context maps" in text` for the WITH-maps report. That
assertion pinned the pre-fix (buggy) behavior: before this task, the appendix scope
note listed "Context maps" even when maps were printed, which was the only place the
string appeared (the coverage inventory itself left the report in M5-T165, per the
test's own comment at lines 639-640). My fix removes exactly that, so the string no
longer appears in the with-maps report. `test_report_pages.py` is a FORBIDDEN path and
this is the packet's anticipated risk #1, so I did NOT edit it. The correct fix (by the
orchestrator or a separate task) is to change line 652 to assert "Context maps" is NOT
in the with-maps report text, matching the M5-T165 state. No other test failed; the
other 1178 passed.

### Follow-up: scope correction applied (recorded by the orchestrator at 2097dae85)

`test_report_pages.py` was made an allowed path for that one assertion only. The last
line of `test_q3_coverage_and_maps_with_and_without_a_map_document` now asserts
`"Context maps" not in text` (with a comment that the appendix scope note reads
maps_present, M5-T179); nothing else in that file changed. Folded into this one commit
(parent stays 6cc452af0). The heavy `tests/drawings` suite now passes fully (0 failed).

## What I could not check

- Browser/e2e, server, ports 3000/3001/8000: not run (forbidden; thin client).
- Full `services/api` pytest and CI: the orchestrator runs them in CI at the accept head.
- S5 (preview print before/after): requires integration + a print; out of this
  worktree's scope. The S3 byte proof above is the page-7 before/after evidence.
