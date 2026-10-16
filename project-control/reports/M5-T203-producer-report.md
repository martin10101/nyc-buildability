# M5-T203 producer report — DB-273: one shared street-window fetch behind the live spatial flag

Producer: backend-engineer (session 2026-10-15c). Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-ad7caa6d6447c0c2e`.
Reset to dispatch head `60d0a096c1b009f29356f4faae5597a8a8f28114`.

## What was built

With `LIVE_SPATIAL_PROVIDER_ENABLED` on, the live geometry provider
(`live_geometry_provider`, `study_live_geometry.py`) and the live street-data provider
(`live_street_data_provider`, `study_inputs.py`) each build the SAME street window for the
lot in one request and fetched it independently (twice). DB-273 asks that they share ONE
fetch of that window. The route does call both in one request scope:
`pluto_study_inputs_provider.provider(canonical_bbl, correlation_id)` calls
`geometry_provider(...)` then `street_data_provider(...)` back to back with the same
`(canonical_bbl, correlation_id)` (`study_inputs.py:489-512`), so a per-request shared
fetch is possible without touching any file outside the packet.

Change (smallest that passes S1-S5):
- New helper `shared_street_window_fetch(fetch=default_fetch)` in
  `services/api/app/api/v1/study_live_geometry.py`: wraps a DCM street `fetch`
  (`(url, correlation_id) -> DcmTransport`) in a thin pass-through that memoises a
  SUCCESSFUL transport keyed by `(url, correlation_id)`. The URL identifies the window
  (the envelope is baked into it); the correlation id scopes the memo to one request, so a
  fresh id never reuses another request's or another lot's entry. A fetch that RAISES is
  not memoised (each provider still sees the failure). The cache is a lock-guarded bounded
  LRU (max 256), so a burst never grows it without limit and never returns a stale window;
  the fetch runs outside the lock so requests never serialise.
- `_live_study_inputs_provider` (`study_inputs.py`) now builds ONE
  `shared_street_window_fetch()` when the flag is on and passes it as `fetch_streets` to
  BOTH `live_geometry_provider(...)` and `live_street_data_provider(...)`. Flag off: both
  providers stay `None`, no shared fetch is constructed, and nothing fetches — byte-identical.
  The lot-geometry fetch stays each provider's own (DB-273 is the street window only).

The flag is off by default, so no live behaviour changes; with it on the merged result is
byte-identical to the two-fetch behaviour (the second provider reuses the first's transports).

## Scenario coverage (new test `tests/api/test_study_street_window_single_fetch.py`)

Driven by the recorded 215-16 Northern pack through the real B-03 connectors; no network.

- S1 `test_window_is_fetched_once_when_both_providers_share_the_fetch`: a one-provider
  baseline shows a window = 2 transports (metadata URL + one envelope page), each once; with
  the shared fetch both providers together transport the window once (`len(calls) == 2`,
  same URLs, no URL twice); and WITHOUT sharing both providers transport it twice (`== 4`).
- S2 `test_shared_fetch_results_equal_the_two_fetch_results`: the merged `SiteGeometry` and
  `StreetData` equal the accepted-composition reference AND equal the un-shared (two-fetch)
  results object for object — sharing removes only the duplicate transport.
- S3 `test_a_failing_shared_fetch_surfaces_the_same_result_in_both_providers`: a raising
  street fetch yields `None` in BOTH providers (fail-closed, same typed result as before),
  and the failure is not memoised (`len(calls) == 2`, both providers reached it).
- S4 `test_flag_off_builds_no_shared_window_fetch`: with the flag off,
  `_live_study_inputs_provider()` constructs no shared fetch (spy count 0); with it on,
  exactly one is constructed (spy count 1).
- S5 mutation: recorded below.

## Checks (lanes venv `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`)

- ruff (`cd services/api && python -m ruff check .`): `All checks passed!` — exit 0.
- Targeted pytest under `flock heavy-run.lock`:
  `pytest -p no:cacheprovider -q tests/api/test_study_street_window_single_fetch.py
  tests/api/test_study_live_geometry.py tests/api/test_study_inputs_live.py
  tests/api/test_study_live_outline_provider.py` → `27 passed, 1 warning in 4.80s` — exit 0.
- `python tools/modularity_check.py --check` → `failures 0; warnings 33` (neither edited
  file is warned) — exit 0.
- `python3 tools/research_record_check.py --check` → `PASS` — exit 0 (NB-01 reported
  `code_current=False`, reported-not-failed; see provenance note below).
- `python3 scripts/lanes/check_lane_paths.py --coverage` → `LANE COVERAGE PASS` — exit 0.

### S5 mutation proof (red/green)

Temporarily replaced the body of `shared_street_window_fetch` with `return fetch` (sharing
disabled). `pytest -q tests/api/test_study_street_window_single_fetch.py`:
`1 failed, 3 passed` — S1 failed with `AssertionError: assert 4 == 2` (the window was
transported twice: metadata + page, each twice). Restored the body;
re-ran: `4 passed` — exit 0.

## Provenance gap — STOP-and-report (requires orchestrator action before acceptance)

`docs/research/evidence-records/NB-01-zoning-lot-instruments.json` lists
`services/api/app/api/v1/study_inputs.py` in `implementation.code_paths`, and pins its
`implementation.code_identity` to `8f70a61cab9cb455677b460dbe53bbf43556f3e1b4a8b96e8a2cc7c5b4d72fa0`.
That pin equals the dispatch-head LF sha256 of `study_inputs.py` (NB-01 was CURRENT for this
file before this task). My edit changes the file's LF sha256 to
`6c743470ec38d79160f2711d91985f049fb85f10e792b872bab868ecc1d270a3`, invalidating the pin.

NB-01 is under `docs/` — a FORBIDDEN path, not in this packet's allowed_paths — so I did not
edit it (D-093 clause: a record whose code_paths include a file I edit is refreshed only if
the record is in my allowed paths; otherwise STOP and report). Required before acceptance
(matches NB-01 revisions 6-8, which refreshed study_inputs.py the same way): scope-correct
M5-T203 to add the NB-01 record to allowed_paths (or route the refresh to the orchestrator),
then refresh `code_identity["services/api/app/api/v1/study_inputs.py"]` to the new LF sha256
and add a dependency_assessment revision noting the DB-273 shared street-window fetch (behind
`LIVE_SPATIAL_PROVIDER_ENABLED`, default OFF; no zoning-lot reading, warning or figure
changed; `research_status` stays `access_blocked`). `study_live_geometry.py` is pinned by no
evidence record and by no review-register entry.

## What I did not check

Full `pytest -q` of `services/api` and the web/e2e suites (CI's job, must be green at the
accepted head, R639). The full api suite was not run locally (heavy-run policy). I did not
run the report print (no report page changed). No network was touched.
