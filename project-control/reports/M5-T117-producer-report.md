# M5-T117 producer report - D-087 shared rate-limit hardening (M5-T111 G5 must-fix + riders)

Task: M5-T117. Producer: backend-engineer (orchestrator-dispatched subagent).
Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t117` (branch `task/M5-T117-rate-limit-hardening`).
Claim seam / parent: `ba48acad68ba7e0abb0c4fa5c31b63ebc622ce22`.
Directives: D-087 (R001,R002,R003,R004,R006,R009), D-066-R001. The routes STAY UNMOUNTED
(`app/main.py` untouched; every path absent from OpenAPI; flag-gated OFF by default). Zero new
dependencies (stdlib + already-admitted starlette only; no requirements/lockfile touch).

Environment note ([OBSERVED]): this producer sandbox is Python 3.11.9; ruff 0.13.0; the four
target test files collect cleanly under 3.11 (they do NOT import the PEP-695 `app/documents/units.py`
chain, so the documented self-check ran verbatim without the shim). CI (3.12) is the authority.

## Files changed (exactly the allowed paths; 6 code/test + this report)

- `services/api/app/resilience/rate_limit.py` - Findings 1-3 (pre-start-cancel slot release,
  bounded sweep, principal hygiene) + docstrings (the slot/anyio-pool relation).
- `services/api/tests/resilience/test_rate_limit.py` - 7 new tests: pre-start-cancel no-leak,
  post-start no-double-release, once-per-window sweep, empty/non-string principal, XFF-never-trusted,
  limiter contention, JobSlots contention.
- `services/api/app/api/v1/scene_api.py` - docstring import paths only (`app.resilience.rate_limit.*`).
- `services/api/tests/scenario/test_scene_api.py`, `tests/drawings/test_dxf_import_api.py`,
  `tests/cad/test_export_api.py` - HEAD/OPTIONS added to the every-method-404 loops; an AST-based
  no-local-limiter guard (catches a module-level dict/defaultdict/OrderedDict/deque).
- `project-control/reports/M5-T117-producer-report.md` - this report.

## Finding 1 (MEDIUM, must-fix-before-enable) - slot state machine (rate_limit.py `run_in_job_slot`)

The slot is acquired by `try_acquire()` BEFORE the job starts. WHO releases it is decided by a
lock-guarded `started` flag set inside the worker before `work()` runs, and a `released` flag makes
the single release idempotent. Every path releases EXACTLY ONCE, never leaks, never double-releases:

| Path | started? | Who releases the slot | in_flight outcome |
|---|---|---|---|
| Cap full at entry | (no slot taken) | nobody - `SlotsExhausted` raised before acquire | unchanged |
| Success | True | worker `finally` (thread returns) | -> 0 |
| `work()` raises | True | worker `finally` (thread returns) | -> 0 |
| PRE-START cancel (deadline fires while the runner still waits for a thread token; worker never runs) | False | the `except BaseException` cancel path (`if not started: _release_once()`) | -> 0 (was: LEAKED) |
| POST-START timeout/cancel (worker running, await abandoned) | True | worker `finally` when the thread later returns; cancel path does NOT release | held at 1, then -> 0 |

Race-freedom: with production's `run_in_threadpool` (`abandon_on_cancel=False`) the two owners are
already mutually exclusive - on cancellation it either never dispatched the worker (`started` stays
False -> cancel-path release) or shielded and waited for the running thread to finish first (worker
`finally` already released, `started` True -> cancel path is a no-op). The `released` flag guarantees
no double-decrement even under an exotic abandoning/delayed runner; `JobSlots.release()` also guards
`> 0` so a stray release can never go negative.

SLOT COUNT vs anyio POOL (documented in the module docstring): anyio's default thread-pool capacity
limiter is 40 tokens ([OBSERVED]: `anyio.to_thread.current_default_thread_limiter().total_tokens == 40`
inside an async context). Each of the three D-087 routes caps at `max_slots=16`, so no single route
(16 < 40) can starve the pool, but their SUM (3 x 16 = 48) EXCEEDS 40. Holding a slot therefore does
NOT imply an available thread token; under load a slot can be held while its worker waits for a token,
and if the per-request deadline fires during that wait the worker never starts - exactly the leak this
fix closes. (PKT-H may additionally size the summed caps at/under 40 or acquire the token with the slot.)

## Finding 2 - bounded full-table sweep (rate_limit.py `_maybe_sweep`)

The O(max_keys x max_requests) expired-key sweep is now throttled to AT MOST ONCE PER `window_seconds`
via `_maybe_sweep` (the first new key at the ceiling in a window sweeps and records `_last_sweep`; the
rest in that window are refused fail-closed after an O(1) ceiling check). `reset()` clears `_last_sweep`.
Cost bound only - correctness unchanged: skipping a sweep merely DELAYS reclaiming an expired key by up
to one window; an active key is never evicted and a new key is still refused while the ceiling is full
of active keys. A distinct-key flood at the ceiling can therefore no longer serialize every caller
behind a full sweep per refused key.

## Finding 3 - principal hygiene + XFF (rate_limit.py `caller_key`)

`caller_key` now keys on the principal ONLY when `request.state.principal` is a NON-EMPTY `str`
(`isinstance(principal, str) and principal`); None, "" and any non-string fall back to the host key,
so a blank/malformed principal can never collapse distinct callers into one `principal:` bucket.
`X-Forwarded-For` is still never read (the helper only touches `request.state.principal` and
`request.client.host`), and a new test proves an XFF header cannot change the key.

## Per-AS evidence

- **AS-1 (no slot leak)** - `test_rate_limit.py::test_pre_start_cancel_releases_the_slot_exactly_once_no_leak`
  (injected runner never runs the worker; after `TimeoutError`, `in_flight == 0` and a fresh
  `try_acquire()` succeeds) and `::test_post_start_cancel_releases_the_slot_exactly_once_no_double`
  (a `_CountingJobSlots` proves `release_calls == 1`, held at 1 while the thread runs, then 0). The
  pre-existing `test_slot_held_until_thread_ends_not_on_await_cancel` still passes. Mutations
  never-release-on-pre-start-cancel and release-on-every-cancel both RED (table below).
- **AS-2 (bounded sweep)** - `::test_full_table_sweep_runs_at_most_once_per_window` counts real
  `_sweep_expired` calls: a 50-key flood in one window -> at most one sweep; the next window re-opens
  the throttle (count 2) and reclaims a/b/c. Mutation sweep-on-every-refused-key RED. The existing
  `test_idle_keys_are_evicted_so_the_ceiling_readmits` and the bounded/active-no-evict tests stay green.
- **AS-3 (principal hygiene + XFF)** - `::test_empty_or_non_string_principal_falls_back_to_host`
  (`""`/`0`/`False`/`[]`/`{}`/tuple/int -> host; a non-empty string still keys principal) and
  `::test_x_forwarded_for_header_never_changes_the_key` (any XFF value keeps the host key; no client ->
  `host:unknown`). Mutations empty-principal-accepted and trust-XFF both RED.
- **AS-4 (test gaps)** - HEAD and OPTIONS added to `test_every_method_is_a_generic_404_while_disabled`
  in all three route test files (HEAD carries an empty body, OPTIONS carries `{"detail":"Not Found"}`,
  neither carries `X-Correlation-ID` - [OBSERVED] via a TestClient probe). An AST guard
  `_module_level_limiter_containers` in all three test files flags any module-level dict literal or
  `dict`/`defaultdict`/`OrderedDict`/`deque` construction (catches the plain-dict form the substring
  scan missed); it returns `[]` for all three route modules today. Multi-thread contention tests
  (`::test_limiter_admits_at_most_max_requests_under_concurrent_callers`,
  `::test_job_slots_admit_at_most_max_slots_under_contention`) admit EXACTLY the cap under 64
  barrier-synced callers.
- **AS-5 (scope)** - per-route limits (30/60 s), the 429 shape, deadlines and correlation ids are
  UNCHANGED (only docstrings + the release path in rate_limit.py; scene_api.py docstrings only). Routes
  UNMOUNTED (`app/main.py` untouched; `test_route_is_unmounted_in_the_real_app` green in all three).
  Zero new deps; ruff clean; modularity exit 0; exactly the allowed paths (6 files + this report).
- **G3 A3 (docstring path)** - scene_api.py docstrings now cite `app.resilience.rate_limit.run_in_job_slot`
  / `.SlidingWindowRateLimiter` (the real importable path); text only, no code change.

## Mutation table (in-process, CONSUMING namespace; scratch harness, NOT committed) - [OBSERVED]

Harness loaded the committed test module and patched the binding the tests consume, ran the target
test, restored. Baselines (8) GREEN.

| Mutation | Patch | Test reddened | Result |
|---|---|---|---|
| never-release-on-pre-start-cancel | `run_in_job_slot` w/o the cancel-path release (the old code) | test_pre_start_cancel_releases_the_slot_exactly_once_no_leak | RED |
| release-on-every-cancel | cancel path calls `_release_once()` unconditionally | test_post_start_cancel_..._no_double AND test_slot_held_until_thread_ends_not_on_await_cancel | RED (both) |
| sweep-on-every-refused-key | `_maybe_sweep = lambda self, now: self._sweep_expired(now)` | test_full_table_sweep_runs_at_most_once_per_window | RED |
| empty-principal-accepted | `caller_key` uses `if principal is not None` | test_empty_or_non_string_principal_falls_back_to_host | RED |
| trust-XFF | `caller_key` returns the `x-forwarded-for` header | test_x_forwarded_for_header_never_changes_the_key | RED |

Contention (G4 gap 1): a plain "drop the lock" did NOT over-admit in 25 trials on CPython (the GIL
serializes the ~3-bytecode check-then-act; matches the M5-T111 G4 note). A drop-lock WITH a yield
between the check and the increment DID over-admit (JobSlots worst-admitted = 12 > cap 10; locked = 10),
confirming the `threading.Lock` closes a genuine check-then-act race. The committed contention tests
are POSITIVE guards (admitted == cap under load); they are not claimed to redden on a bare lock-removal.

## Commands (explicit cwd; verbatim tails) - [OBSERVED]

1. `cwd services/api: python -m ruff check .` -> `All checks passed!`
2. `cwd services/api: python -m pytest tests/resilience tests/scenario/test_scene_api.py
   tests/drawings/test_dxf_import_api.py tests/cad/test_export_api.py -q` -> `190 passed in 4.29s`
   (was 183; +7 new resilience tests). Ran verbatim under 3.11 - the four target files do not import
   the PEP-695 chain, so the shim was not needed here.
3. `cwd repo root: python tools/modularity_check.py --check` -> `selected 503 files; failures 0;
   warnings 27`; `DIRECT_EXIT=0`. None of the 6 changed files is flagged (rate_limit.py grew only
   with the fix + docstrings; still well under the ceiling).

## Deviations

- None material. The LOCAL PYTHON shim named in the packet was available but unnecessary for the
  documented self-check (the four target files collect under 3.11); recorded for transparency.
- The contention mutation (drop-lock) is a POSITIVE-property guard, not a reddening mutation on CPython
  (GIL); demonstrated the lock is load-bearing with a widened-window variant instead (see above). This
  matches the M5-T111 G4 gap-1 assessment and is not one of the five task-named mutations.

## OPEN QUESTIONS (owner asleep - recommended answers)

1. **Summed slot caps (48) vs anyio pool (40).** This packet CLOSES the leak so held-but-unstarted
   slots cannot accumulate; it does not change the caps. RECOMMEND: leave `max_slots=16`/route as-is;
   PKT-H (which owns `app/main.py`/config and does a load test) sizes the summed caps at/under 40 or
   acquires the thread token with the slot. Tier-A tuning; no owner action needed.
2. **Sweep throttle granularity.** Chosen "at most once per `window_seconds`" (simple, correctness-
   preserving). RECOMMEND: accept; if PKT-H's load test shows reclamation lag matters, switch to a
   per-call cost cap. No owner action needed.

## DISCOVERIES (D-069 - for the orchestrator to record; not fixed in-packet)

- **DB-086 (d) / (e) remain PKT-H** (per-route body ceilings; auth to set `request.state.principal`) -
  unchanged by this packet; still routed to the mount.
- **DB-086 (k)** (route-level slot-hold past a REAL-runner deadline proven only at the primitive level)
  - unchanged: a 3.12 route-level integration test would fully close it; left `by note` per the packet,
  the primitive-level proof (`run_in_job_slot` tests + the route 503 mapping) stands.
- No new product/domain defects found.

END-OF-REPORT
