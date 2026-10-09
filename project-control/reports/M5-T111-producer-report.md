# M5-T111 producer report — D-087 pre-mount route hardening (ONE shared bounded limiter)

Task: M5-T111 (D-087 PKT-H pre-mount riders). Producer: backend-engineer.
Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t111` (branch `task/M5-T111-route-hardening`).
Claim seam / parent: `275ef85f05ca43a9cd2fd59a5ccdfa3b80cd3021`.
Directives: D-087 (R001,R002,R003,R004,R006,R009), D-066-R001. The routes STAY UNMOUNTED
(`app/main.py` untouched; every path absent from OpenAPI; flag-gated OFF by default).

Environment note (binding, [OBSERVED]): this producer sandbox is **Python 3.11.9**; the repo
requires `>=3.12` and CI runs 3.12 (`services/api/pyproject.toml:10`, `.github/workflows/ci.yml`).
This only affects self-check #3 (see COMMANDS): three pre-existing `tests/drawings` files fail to
COLLECT under 3.11 because `app/documents/units.py:276` uses PEP 695 generic syntax
(`def _match_unit[UnitT: enum.Enum](`) — a file I did not touch and my modules do not import. All
other neighbours run green; the isolation recipe is recorded below.

## Files changed (exactly the allowed paths)

- `services/api/app/resilience/rate_limit.py` — NEW shared module (limiter + caller_key + job slots).
- `services/api/tests/resilience/test_rate_limit.py` — NEW unit pack (14 tests).
- `services/api/app/api/v1/scene_api.py` — switched to the shared limiter + job slots; every-method 404.
- `services/api/app/api/v1/dxf_import_api.py` — shared limiter + slots; rate-limit-before-param-parse
  (DB-081 b); pre-render-guard utf-8 encode aligned (DB-081 e); every-method 404.
- `services/api/app/api/v1/export_api.py` — shared limiter + slots; every-method 404.
- `services/api/tests/scenario/test_scene_api.py`, `tests/drawings/test_dxf_import_api.py`,
  `tests/cad/test_export_api.py` — route-side riders (AS-1/4/5/6, DB-081 b/e).
- `project-control/reports/M5-T111-producer-report.md` — this report.

## Shared limiter design (`app/resilience/rate_limit.py`)

A NEW sibling of the connector-resilience package; it does not touch/import the existing
`app/resilience/*` modules or their `__init__` (those stay read-only — the routes import
`rate_limit` directly, and it is not re-exported from `__init__` to avoid the connector import
graph). Stdlib only (`threading`, `collections.deque`, `time`, `asyncio`,
`starlette.concurrency.run_in_threadpool`). Zero new dependencies.

- **`SlidingWindowRateLimiter`** — thread-safe (`threading.Lock`) per-caller sliding window.
  Public mutable attrs read LIVE inside `allow()`: `max_requests`, `window_seconds`, `max_keys`
  (tests tighten the live instance). Injectable `clock` (default `time.monotonic`).
  - Per-key window pruned of stamps `<= now - window`; a key whose window empties is dropped
    immediately (never retained as a dead entry).
  - **Key ceiling** `max_keys`: a NEW key arriving at the ceiling triggers a sweep of
    EXPIRED-window keys first; if the ceiling is still full of ACTIVE keys the new key is
    **refused (fail-closed)**. `_sweep_expired` only removes keys with NO live stamps, so an
    active key's history is **never evicted** (evicting it would silently reset that caller's
    window and let it exceed its limit — the exact LRU flaw in the old export limiter).
  - A non-positive `max_requests` refuses every caller (used by the limit-before-parse tests).
- **`caller_key(request)`** — ONE key helper. Returns `f"principal:{p}"` when the request
  carries an authenticated principal, else `f"host:{host or 'unknown'}"`. The two are namespaced
  so a host string can never collide with a principal id.
  - PRINCIPAL SOURCE (documented in the docstring): PKT-H's auth dependency/middleware sets
    `request.state.principal`; this helper reads exactly that attribute, so keying flips from
    host to principal the moment auth lands with no further change here.
  - PROXY-COLLAPSE (DB-080 b / DB-081 a / DB-082 b, in the docstring): while the key is the
    host, every caller behind Render's shared proxy presents the same peer address and collapses
    to one bucket; `X-Forwarded-For` is deliberately NOT trusted (spoofable → unlimited minted
    keys defeats the limiter). Real per-caller isolation is the principal, which is why this
    family stays UNMOUNTED until PKT-H supplies auth.
- **`JobSlots` + `run_in_job_slot(slots, work, *, timeout, runner=run_in_threadpool)`** — the
  bounded in-flight job cap. `run_in_job_slot` acquires a slot BEFORE starting `work`, wraps
  `work` in a `_guarded()` whose `finally` calls `slots.release()`, and runs `_guarded` off the
  event loop under `asyncio.wait_for(..., timeout)`. There is **no release on the coroutine's
  cancellation** — release lives in `_guarded`, bound to the worker THREAD's completion. So a
  job abandoned at the deadline keeps its slot until its thread ends, and abandoned threads
  cannot accumulate past `max_slots`. Over the cap raises `SlotsExhausted` (the routes map it to
  a typed **503, `capacity_exhausted`**). `runner` is injectable so the unit test models
  deadline-abandonment deterministically.

Per-route instances (per-route state; the CLASS is shared): each route builds its own limiter
(30 req / 60 s, `max_keys` 4096 scene / 8192 dxf+export — unchanged from before) and
`JobSlots(max_slots=16)`, exposed via `get_rate_limiter()` / `get_job_slots()`. Slot cap 16 is
below anyio's default 40-thread pool (`current_default_thread_limiter().total_tokens == 40`,
[OBSERVED]) so one saturated route cannot starve the pool; the pool is a second global backstop.

## Chosen job-slot refusal status (documented)

Over the in-flight cap → **`503 capacity_exhausted`** (a server-availability signal), kept
distinct from the per-caller **429 rate_limited** and the per-request **504/503 deadline**. Each
route's `*_STATUS_STATE_MATRIX` gained `(503, "capacity_exhausted")` and `(405, None)`.

## Per-AS evidence

- **AS-1 (one shared limiter)** — all three routes call `get_rate_limiter().allow(caller_key(...))`
  and `run_in_job_slot(get_job_slots(), ...)`; no route-local limiter class/dict/deque remains.
  Guard test `test_route_uses_the_shared_limiter_and_slots_only` (each route) asserts the shared
  types back the route, `not hasattr(mod,"_RateLimiter")` / `_rate_state`, and an AST-ish source
  scan (`class _RateLimiter`/`deque`/`OrderedDict`/`_rate_state` absent). Per-route limits
  unchanged (30/60 s). Mutation M1 red. Consumer sweep: the three route modules are imported only
  by their own test file; the only external references are negative "stays UNMOUNTED" assertions
  (`test_glb_writer.py:594`, `test_building_footprints_arcgis.py:852`) — both still green.
- **AS-2 (bounded + fail-closed + active-no-evict + idle-evict)** — `test_rate_limit.py`:
  `test_bounded_keys_fail_closed_and_never_evict_an_active_key`,
  `test_idle_keys_are_evicted_so_the_ceiling_readmits`,
  `test_single_key_with_an_empty_window_is_dropped_not_retained`,
  `test_admits_up_to_limit_then_refuses`, `test_window_slides_and_readmits`. Mutations M2
  (evict-active), M3 (no-sweep), M11 (no-ceiling) all red.
- **AS-3 (key: principal over host)** — `test_caller_key_prefers_principal_over_host`,
  `test_two_principals_from_one_host_are_distinct_keys`,
  `test_caller_key_falls_back_to_host_then_unknown`. Mutation M4 (host-first) red.
- **AS-4 (limit before parse, every route)** — scene/export
  `test_limiter_runs_before_body_parse` (over-limit + malformed body → 429, a body-read tripwire
  proves the body is NOT read; admitting the caller → 422 and the tripwire trips). dxf
  `test_draft_rate_limit_precedes_parameter_parse` is the canonical DB-081 (b): over-limit /draft
  with a malformed PARAMETER → 429, not a 422 ahead of the limiter (the fix moved the flag+limit
  ahead of `_parse_assignment`). Mutations M8 (scene bypass) and M9 (dxf parse-first) red.
- **AS-5 (job slots)** — `test_rate_limit.py::test_slot_held_until_thread_ends_not_on_await_cancel`
  (a real background thread blocks past the 0.05 s deadline; after `TimeoutError` `in_flight==1`;
  a second job over the cap raises `SlotsExhausted`; the thread finishing frees the slot), plus
  `test_over_cap_raises_slots_exhausted`, `test_slot_is_released_after_normal_completion`,
  `test_slot_is_released_when_work_raises`. Route-level: each route's
  `test_503_capacity_exhausted_and_its_reddening_mutation` (max_slots=0 → 503 capacity; restore →
  200). Mutation M5 (release-on-cancel) red.
- **AS-6 (every method 404 while disabled; OpenAPI absence)** — each route registered via
  `@router.api_route(path, methods=[GET,HEAD,POST,PUT,PATCH,DELETE,OPTIONS], include_in_schema=False)`
  with a flag-first / method-second dispatch: disabled → generic 404 for EVERY method (byte-identical
  to an unmounted path, no correlation id); enabled non-POST → a real 405. Tests
  `test_every_method_is_a_generic_404_while_disabled`, `test_enabled_non_post_method_is_a_real_405`,
  `test_no_path_in_the_throwaway_app_openapi` (router INCLUDED on a throwaway app, yet no path in
  `openapi()`). Mutations M6 (method-before-flag → 405 leak) and M7 (include_in_schema=True) red.
- **AS-7 (ceilings + encode step)** — see "Per-route ceiling arithmetic" and "DB-081 (e)" below.
- **AS-8 (scope)** — zero new deps; `app/main.py` untouched; routes UNMOUNTED; ruff clean;
  modularity exit 0; exactly the allowed paths (8 code/test files + this report). Every prior
  test of the three routes passes or was updated in scope (the limiter-internals tests moved to
  `test_rate_limit.py`; the rate-limit/deadline tests now tighten the shared limiter instance —
  reason: the route-local limiter classes/functions they targeted were replaced).

## Per-route body-ceiling arithmetic (AS-7 / DB-081 c / DB-082 e) — [OBSERVED, computed]

`MAX_BODY_BYTES = 262144` (256 KiB) is defined in `proposal_validation.py` (FORBIDDEN in this
packet) and re-exported by each route. Measured JSON sizes (`python -c`, [OBSERVED]): a
10,000-vertex ring ≈ 220,000 bytes; a full single-max-ring export body ≈ 232,207 bytes (fits);
a two-max-ring (lot + building, 10,000 each) + 2000-floor export body ≈ **452,226 bytes** (≈442
KiB).

- **Export (DB-082 e)**: the writer ring cap is 10,000 vertices (dxf/glb; pdf 1024) and floors
  ≤ 2000 (`export_service` `_FORMAT_RING_CAP` / `MAX_FLOORS`). A legitimate maximum input (two
  10,000-vertex rings) is **452 KB > 256 KiB → refused with a 413 BEFORE the writer's vertex
  cap**. The parser caps (10,000-vertex ring, 2000 floors) DO bound the work, so a larger ceiling
  would be safe. DECISION: **keep + route the finding** — the ceiling is shared/forbidden here and
  changing it would also affect proposal_validation + scene; the refusal fails CLOSED (413, safe).
  Recommend a dedicated per-route ceiling (~1 MiB, sized to two max rings + max floors) at the
  PKT-H mount, which owns `app/main.py`/config. (DISCOVERY below.)
- **DXF import (DB-081 c)**: `_IMPORT_DXF_LIMITS = DxfLimits(max_bytes=256 KiB)`; the reader's own
  default is 8 MiB and it clamps `max_vertices=100,000 / max_entities=200,000 / max_lines=2e6 /
  max_line_chars=4096`. Real architect ASCII DXF files are commonly 1–20 MB, so 256 KiB is TIGHT
  and would refuse a legitimate file (413, fail-closed). The reader caps bound the work
  independent of file size. DECISION: **keep + route the finding** (shared/forbidden ceiling);
  recommend a dedicated `DXF_IMPORT_MAX_BODY_BYTES` (e.g. 8 MiB) at PKT-H once real samples exist.
- **Scene**: body = lot_ring + proposed_massing (or generated_option) + a small context envelope.
  A realistic at-budget proposed massing is tens of KB (per the `proposal_validation` rationale);
  256 KiB comfortably fits it and the tiny context envelope. DECISION: **keep, no change** — no
  legitimate maximum input is refused.

## DB-081 (e) decision — pre-render guard utf-8 encode step

**ALIGNED.** `dxf_import_api._guard_finite_response` now does
`json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8")` (matching the sibling
routes / `proposal_validation`), so it also catches a non-encodable string (an unpaired
surrogate) the `ensure_ascii=False` renderer would raise on mid-response. Reachability: the
DB-081 (e) note holds — query params decode with replacement and drawing text is ASCII, so a
surrogate is not reachable via normal input today; the alignment is cheap defense-in-depth that
removes a divergence. Proven by `test_pre_render_guard_catches_a_non_encodable_string` (surrogate
→ typed 500; NaN → typed 500; safe body → None) with mutation M10 (drop `.encode`) red.
`except ValueError` still covers both cases (`UnicodeEncodeError` subclasses `ValueError`).

## Mutation table (in-process, CONSUMING namespace; scratch harness, NOT committed)

All 11 applied to source, targeted test run, source restored; baseline (restored) = 10 nodes
GREEN. [OBSERVED]

| # | Property | Mutation | Test reddened | Result |
|---|---|---|---|---|
| M1 | AS-1 shared-only | reintroduce a route-local `_RateLimiter` class (scene) | test_route_uses_the_shared_limiter_and_slots_only | RED |
| M2 | AS-2 active-no-evict | `_sweep_expired` deletes ACTIVE keys too | test_bounded_keys_fail_closed_and_never_evict_an_active_key | RED |
| M3 | AS-2 idle-evict | skip the expired-key sweep | test_idle_keys_are_evicted_so_the_ceiling_readmits | RED |
| M11 | AS-2 fail-closed | remove the key-ceiling refusal | test_bounded_keys_fail_closed_and_never_evict_an_active_key | RED |
| M4 | AS-3 key | host-first (ignore principal) | test_two_principals_from_one_host_are_distinct_keys | RED |
| M5 | AS-5 slots | release the slot on await cancellation | test_slot_held_until_thread_ends_not_on_await_cancel | RED |
| M6 | AS-6 404 | check method before the flag (non-POST disabled → 405) | test_every_method_is_a_generic_404_while_disabled | RED |
| M7 | AS-6 OpenAPI | `include_in_schema=True` | test_no_path_in_the_throwaway_app_openapi | RED |
| M8 | AS-4 order | bypass the limiter so the body is parsed (scene) | test_limiter_runs_before_body_parse | RED |
| M9 | DB-081 b | parse params before the limiter (dxf draft) | test_draft_rate_limit_precedes_parameter_parse | RED |
| M10 | DB-081 e | drop `.encode("utf-8")` in the pre-render guard | test_pre_render_guard_catches_a_non_encodable_string | RED |

## Commands (explicit cwd; verbatim tails)

1. `cwd services/api: python -m ruff check .` → **[OBSERVED]** `All checks passed!`
2. `cwd services/api: python -m pytest tests/resilience tests/scenario/test_scene_api.py
   tests/drawings/test_dxf_import_api.py tests/cad/test_export_api.py -q`
   → **[OBSERVED]** `183 passed in 5.79s`
3. `cwd services/api: python -m pytest tests/scenario tests/drawings tests/cad -q`
   → **[OBSERVED, isolated]** the command as-written is INTERRUPTED at collection by the
   pre-existing 3.11-vs-3.12 artifact (`app/documents/units.py:276 SyntaxError`, PEP 695, in the
   `tests/drawings` documents chain — not my modules). Run with the three version-blocked files
   isolated: `tests/scenario` → `787 passed`; `tests/cad` → `435 passed`; `tests/drawings
   --ignore=test_pdf_object_streams.py --ignore=test_sheet_reader.py
   --ignore=test_sheet_reader_split_equivalence.py` → `125 passed`. CI (3.12) collects those three
   without the SyntaxError. Route to HARVEST if a 3.12 confirmation is required.
4. `cwd repo root: python tools/modularity_check.py --check` → **[OBSERVED]** `DIRECT_EXIT=0`;
   none of my new/changed files flagged (rate_limit.py 208, scene_api.py 340, dxf_import_api.py
   417, export_api.py 264 non-blank lines — all < WARN_SLOC 600).

## Deviations

- Self-check #3 could not be run verbatim in this 3.11 sandbox (pre-existing 3.12-only file);
  isolated-run evidence recorded above. No code change of mine is implicated.
- The two body-ceiling findings (DB-081 c, DB-082 e) are KEPT + ROUTED rather than changed,
  because `MAX_BODY_BYTES` lives in the FORBIDDEN `proposal_validation.py` and is shared across
  routes; both refusals fail closed (413). See DISCOVERIES.

## OPEN QUESTIONS (owner asleep — recommended answers)

1. **Job-slot cap value (16/route).** Chosen below anyio's 40-thread pool so a single route
   cannot starve it; three routes at 16 (48) exceed 40, but they are exercised one-at-a-time in
   practice and the pool is a global backstop. RECOMMEND: accept 16; the mount packet (PKT-H) may
   revisit under a load test. (No owner action needed; a Tier-A tuning knob.)
2. **Per-route body ceilings (DB-081 c / DB-082 e).** RECOMMEND: introduce dedicated ceilings at
   PKT-H (export ~1 MiB; dxf-import ~8 MiB) in the mount packet that owns `app/main.py`/config,
   sized to the arithmetic above; keep 256 KiB for scene. Queued as DISCOVERIES, not fixed here.

## DISCOVERIES (D-069 — for the orchestrator to record; not fixed in-packet)

- **DB-D1 (export body ceiling)**: the shared 256 KiB body ceiling refuses a legitimate maximum
  export input (two 10,000-vertex rings ≈ 452 KB) with a 413 before the writer's vertex cap
  (fail-closed). Recommend a dedicated export body ceiling (~1 MiB) at PKT-H. Arithmetic in this
  report. (Refines DB-082 e.)
- **DB-D2 (dxf-import body ceiling)**: the shared 256 KiB ceiling is tight for real architect DXF
  files (commonly 1–20 MB); the reader caps bound the work regardless. Recommend a dedicated
  `DXF_IMPORT_MAX_BODY_BYTES` (~8 MiB) at PKT-H, validated against real samples. (Refines DB-081 c.)
- **DB-D3 (env)**: repo requires Python 3.12 (PEP 695 in `app/documents/units.py`); a 3.11
  producer sandbox cannot collect the `tests/drawings` documents chain. Not a defect — recorded so
  future 3.11 sandboxes isolate those files. (Matches the prior sandbox 3.11-vs-3.12 note.)

END-OF-REPORT
