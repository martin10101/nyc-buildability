# M5-T123 producer report — D-087 pre-mount riders 2 (per-route ceilings, summed slots, principal, test notes)

Task: M5-T123 (D-087 PKT-H pre-mount riders 2). Producer: backend-engineer (orchestrator-dispatched subagent).
Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t123` (branch `task/M5-T123-premount-ceilings-slots`).
Claim seam / parent: `8acf9c8691a1a1ddaf63418e9dc4ae98e81aed76`.
Directives: D-087 (R001,R002,R003,R004,R006,R009), D-066-R001. Discharges DB-086 (d) and DB-088
(a),(b),(e),(g). The routes STAY UNMOUNTED (`app/main.py` untouched; every path absent from
OpenAPI; flag-gated OFF by default). `proposal_validation.MAX_BODY_BYTES` stays 256 KiB (untouched,
verified). Zero new dependencies (stdlib + already-admitted starlette/anyio only).

Environment ([OBSERVED]): producer sandbox Python 3.11.9; ruff 0.13.0; anyio 4.10.0. The four
target test files do NOT import the PEP-695 `app/documents/units.py` chain, so the documented
self-checks ran verbatim under 3.11 without the shim (matches M5-T117). CI (3.12) is the authority.

## Files changed (exactly the 9 allowed paths)

- `app/resilience/rate_limit.py` — `caller_key` whitespace-only principal → host (DB-088 b); the
  slot/anyio-pool docstring updated to the new summed-under-40 relation.
- `app/api/v1/scene_api.py` — own `SCENE_MAX_BODY_BYTES` (2 MiB); `SCENE_MAX_IN_FLIGHT` 16→8.
- `app/api/v1/export_api.py` — own `EXPORT_MAX_BODY_BYTES` (1 MiB); `EXPORT_MAX_IN_FLIGHT` 16→12.
- `app/api/v1/dxf_import_api.py` — own `DXF_IMPORT_MAX_BODY_BYTES` (20 MiB), `_IMPORT_DXF_LIMITS`
  max_bytes raised with it; `DXF_IMPORT_MAX_IN_FLIGHT` 16→4.
- `tests/resilience/test_rate_limit.py` — whitespace-principal cases; the summed-slots-under-the-pool
  guard; the DB-088 (g) event-handshake fix (both post-start-timeout tests).
- `tests/scenario/test_scene_api.py`, `tests/cad/test_export_api.py`,
  `tests/drawings/test_dxf_import_api.py` — per-route ceiling tests (measurement + admission +
  ceiling+1) and the broadened list/set/Counter AST guard + its coverage test.
- `project-control/reports/M5-T123-producer-report.md` — this report.

## (1) PER-ROUTE BODY CEILINGS — AS-1 (DB-086 d = M5-T111 G5 Finding 4)

Each route now declares its OWN ceiling constant, sized from evidence; `proposal_validation.py`'s
256 KiB `MAX_BODY_BYTES` is UNTOUCHED and no longer borrowed by any of the three routes. Enforcement
is unchanged (the reused bounded-streaming `_read_body_within_ceiling` path enforces BEFORE the body
is buffered past the ceiling; the declared-Content-Length fast path stays; the 413 shape is unchanged
— only the byte number in the message changes).

### Ceiling table

| Route | Old ceiling | New ceiling | Basis / arithmetic |
|---|---|---|---|
| scene | 256 KiB (shared) | **2 MiB** = 2,097,152 | Maximal legit scene body = proposed_massing at `app.scenario.proposal` caps (MAX_TOTAL_OUTLINE_POSITIONS 20,000 coord pairs + MAX_EXTERIOR_WALLS 4,000 walls + MAX_LEVELS 500) + a lot_ring at MAX_OUTLINE_VERTICES 1,000 + context. **MEASURED 811,225 bytes (~792 KiB)** [OBSERVED]. 2 MiB ≈ 2.6× headroom. |
| export | 256 KiB (shared) | **1 MiB** = 1,048,576 | Maximal legit export = two rings at the DXF writer cap (`export_service._FORMAT_RING_CAP['dxf']` = 10,000 vertices) + MAX_FLOORS 2,000. **MEASURED 452,336 bytes (~442 KiB)** [OBSERVED] (matches M5-T111's ~452 KB). 1 MiB ≈ 2.3× headroom. |
| dxf-import | 256 KiB (shared) | **20 MiB** = 20,971,520 | Documented real architect ASCII DXF range **1–20 MB** (DB-086 d; the architect-drawing corpus records no DXF byte sizes, only TIFF/PDF masters — see DISCOVERIES). 20 MiB covers a 20 MB (decimal) file with headroom and is under the reader's own 64 MiB hard clamp (`dxf_reader._LIMIT_CEILINGS['max_bytes']`). `_IMPORT_DXF_LIMITS = DxfLimits(max_bytes=DXF_IMPORT_MAX_BODY_BYTES)` — the reader clamp is RAISED with the ceiling. |

The two measured maxima (811,225 / 452,336) are BOTH > 256 KiB, so the old shared ceiling would have
refused a legitimate maximum request with a 413 before any assembler/writer cap — exactly Finding 4 /
DB-D1/DB-D2. The measurement + the old-vs-new bound is asserted in-suite
(`test_ceiling_admits_the_contract_maximal_{scene,export}_request`); a maximal-SIZE body is admitted
past the 413 gate through the REAL route (`test_maximal_sized_*_body_is_admitted_past_the_ceiling`,
status != 413); ceiling+1 is refused 413 (`test_413_oversized_body`). For DXF, the enforcement
mechanism (ceiling+1 → 413, exact-ceiling accepted) is proven at a small monkeypatched ceiling to
avoid 20 MiB test bodies, and the REAL value (≥ 20 MB, reader clamp raised, under the hard clamp) is
proven by `test_dxf_ceiling_sized_for_real_files_and_raises_the_reader_clamp`.

### Worst-case memory arithmetic (ceiling × in-flight slots × parse overhead)

| Route | Ceiling | Slots | Raw buffered (ceiling×slots) | Parse peak factor | Worst-case peak |
|---|---|---|---|---|---|
| scene | 2 MiB | 8 | 16 MiB | ~6–10× (deep 20k-coord object graph) | ~144 MiB |
| export | 1 MiB | 12 | 12 MiB | ~5–8× | ~72 MiB |
| dxf-import | 20 MiB | 4 | 80 MiB | ~1.2× (byte buffer dominates; bounded reader structures) | ~96 MiB |
| **total** | — | 24 | 108 MiB raw | — | **~312 MiB** worst case |

The 20 MiB dxf ceiling makes dxf-import the heaviest per-slot memory (raw buffer), which is why it
gets the FEWEST slots (4). Scene's deep JSON parse makes its per-request peak heaviest, which is why
it gets fewer than export. The peak is transient (the raw buffer + parsed graph coexist only during
one request) and bounded; it is well within a Render instance and further gated by the per-caller
rate limit, per-request deadlines, and the summed-under-40 slot cap.

## (2) SLOT SIZING — AS-2 (DB-088 a)

anyio's default thread-pool token count is read LIVE from the INSTALLED anyio (never assumed):
**anyio 4.10.0**, `AsyncIOBackend.current_default_thread_limiter` builds `CapacityLimiter(40)`
(`anyio/_backends/_asyncio.py:2907`); [OBSERVED]
`anyio.to_thread.current_default_thread_limiter().total_tokens == 40`.

### Slot table

| Route | Old slots | New slots | Reasoning (heavier per-slot → fewer) |
|---|---|---|---|
| dxf-import | 16 | **4** | Heaviest per-slot memory: a 20 MiB upload buffer per in-flight read. |
| scene | 16 | **8** | 2 MiB ceiling + deepest JSON parse (20k coord pairs) + heaviest CPU (geometry + connector). |
| export | 16 | **12** | Lightest per-slot: 1 MiB ceiling; the writer is CPU-bound, not memory-bound. |
| **SUM** | 48 (> 40) | **24 (< 40)** | 16 tokens of headroom for the app's other `run_in_threadpool` users. |

The former sum 3×16=48 EXCEEDED the 40-token pool (the M5-T117 G5 / DB-088 a carry-forward). The new
sum 8+12+4=24 stays strictly UNDER 40 with 16 tokens of headroom, so a held job slot always implies a
thread token is (or will soon be) available. A test FAILS if the sum ever reaches/exceeds the pool
(`tests/resilience/test_rate_limit.py::test_summed_job_slots_stay_under_the_anyio_thread_pool`),
which also asserts the headroom and the heavier→fewer ordering.

## (3) PRINCIPAL HYGIENE — AS-3 (DB-088 b)

`caller_key` now keys on the principal only when it is a `str` that is non-empty AFTER stripping
whitespace (`isinstance(principal, str) and principal.strip()`); a whitespace-only principal
("   ", tabs, newlines) falls back to the host key exactly like an empty one, so it can no longer
collapse distinct callers into one `"principal:   "` bucket. A non-empty non-whitespace principal is
unchanged (keyed on the raw value; PKT-H supplies a clean server-authenticated id). Proven by the
extended `test_empty_or_non_string_principal_falls_back_to_host` (space/tab/newline/mixed → host).

## (4) TEST NOTES — AS-4

- **DB-088 (e)** — the AST no-local-limiter guard now also catches a module-level **list / set /
  Counter** limiter, not only the dict/deque family. `_LIMITER_CONTAINER_CALLS` gains
  `Counter`/`set`/`list`; the value check adds dict/set literals and an EMPTY list literal (`[]`, the
  empty-state shape) while leaving non-empty constant lists (`__all__`, `_ROUTE_METHODS`) and
  immutable `frozenset` constants (the status matrices, `_TRUE_TOKENS`) alone — no false positive.
  Applied identically to all three route test files (the helper is duplicated per the pre-existing
  G3 A3 note); `test_ast_guard_also_catches_list_set_counter_limiters` proves each reintroduction
  shape is flagged and each legitimate constant is not. The guard still returns `[]` for all three
  real route modules (asserted by the existing `test_route_uses_the_shared_limiter_and_slots_only`).
- **DB-088 (g)** — the two post-start-timeout tests no longer depend on the 50 ms thread-start
  window. Each `_abandoning_runner` now performs an EVENT HANDSHAKE: it starts the worker thread and
  blocks on `started.wait(5.0)` (a generous safety bound, not a timing guess) BEFORE returning the
  sleep coroutine, so the worker has provably entered `work()` and set its started flag before the
  0.05 s deadline even begins — no wall-clock race. (`_guarded` sets the internal started flag before
  `work()` sets the test event, so `started` being set implies the internal flag is already True.)
  The `_never_starts_runner` pre-start test is unchanged (the worker deterministically never runs).

Everything else is unchanged: per-window limits, the 429 shape, deadlines, correlation ids, the
generic 404 (incl. HEAD/OPTIONS) while disabled, the 413 shape, the 503 capacity/deadline mapping.

## Mutation table (in-process source mutation; scratch harness, NOT committed) — [OBSERVED]

Each mutation applied to source, the targeted test run, source restored; baseline (restored) = 199
GREEN. All RED (caught).

| # | AS / property | Mutation | Test(s) reddened | Result |
|---|---|---|---|---|
| M1 | AS-1 scene ceiling | `SCENE_MAX_BODY_BYTES` → 262144 (old 256 KiB) | test_ceiling_admits_the_contract_maximal_scene_request + test_maximal_sized_scene_body_is_admitted_past_the_ceiling | RED (2 failed) |
| M2 | AS-1 export ceiling | `EXPORT_MAX_BODY_BYTES` → 262144 | test_ceiling_admits_the_contract_maximal_export_request + test_maximal_sized_export_body_is_admitted_past_the_ceiling | RED (2 failed) |
| M3 | AS-1 dxf ceiling | `DXF_IMPORT_MAX_BODY_BYTES` → 262144 | test_dxf_ceiling_sized_for_real_files_and_raises_the_reader_clamp | RED (1 failed) |
| M4 | AS-2 slot sum | `SCENE_MAX_IN_FLIGHT` → 24 (sum 24+12+4=40 reaches pool) | test_summed_job_slots_stay_under_the_anyio_thread_pool | RED (1 failed) |
| M5 | AS-3 principal | `caller_key` → `and principal` (no `.strip()`) | test_empty_or_non_string_principal_falls_back_to_host | RED (1 failed) |
| M6 | AS-4 AST guard | revert `_LIMITER_CONTAINER_CALLS` to dict/deque only | test_ast_guard_also_catches_list_set_counter_limiters | RED (1 failed) |
| M7 | AS-4 handshake still tests semantics | `run_in_job_slot` cancel path releases on EVERY cancel | test_post_start_cancel_..._no_double + test_slot_held_until_thread_ends_not_on_await_cancel | RED (2 failed) |

M7 confirms the DB-088 (g) event handshake did not weaken the post-start slot semantics — the tests
still redden under the release-on-every-cancel mutation, now deterministically.

## Commands (explicit cwd; verbatim tails) — [OBSERVED]

1. `cwd services/api: python -m ruff check .` → `All checks passed!`
2. `cwd services/api: python -m pytest tests/resilience tests/scenario/test_scene_api.py
   tests/drawings/test_dxf_import_api.py tests/cad/test_export_api.py -q` → `199 passed in 11.75s`
   (was 190 in M5-T117; +9: 3 AST-guard coverage tests, 2 scene ceiling, 2 export ceiling, 1 dxf
   arithmetic, 1 slot-sum guard). Ran verbatim under 3.11 (the four files do not import the PEP-695
   chain; no shim needed).
3. `cwd repo root: python tools/modularity_check.py --check` → `DIRECT_EXIT=0`. None of the 4 changed
   production files flagged (rate_limit.py 298, scene_api.py 354, export_api.py 275, dxf_import_api.py
   433 non-blank lines — all < the 600 WARN line); the warnings are pre-existing out-of-scope files.

## Deviations

- The DXF ceiling boundary tests are proven at a SMALL monkeypatched ceiling (no 20 MiB test bodies),
  with the REAL 20 MiB value + the raised reader clamp proven by a separate cheap arithmetic test.
  Rationale: a genuinely maximal 20 MB DXF that reads to 200 is impractical to synthesize, and a
  20 MiB all-`9` blob would 422 at the reader anyway; the enforcement code is value-agnostic, so the
  mechanism-at-small-ceiling + real-value-arithmetic pair is both rigorous and fast.
- Scene/export "maximal legitimate request accepted" is proven as "admitted PAST the 413 size gate"
  (status != 413) plus the measurement bound; the maximal-at-caps geometry is degenerate so the
  assembler/writer then refuses it (422) — the ceiling's contract is the SIZE gate, and a legitimate
  end-to-end 200 is the existing happy-path test. No coupling of the ceiling test to the geometry
  contract.

## OPEN QUESTIONS (owner asleep — recommended answers)

1. **Ceiling values (scene 2 MiB / export 1 MiB / dxf 20 MiB).** Sized to the measured/ documented
   maxima with headroom. RECOMMEND: accept as-is; PKT-H (the mount, which owns a load test) may
   re-tune. Tier-A tuning knob; no owner action needed.
2. **Slot split (scene 8 / export 12 / dxf 4 = 24 < 40).** Sized heavier-per-slot→fewer with 16
   tokens headroom for other `run_sync` users. RECOMMEND: accept; PKT-H may re-tune under a real load
   test or acquire the thread token with the slot. Tier-A; no owner action needed.
3. **DXF `max_lines` vs a dense 20 MB file (see DISCOVERIES).** The reader is read-only here, so only
   `max_bytes` was raised. RECOMMEND: the next `dxf_reader.py` touch (or PKT-H) raises `max_lines`
   with `max_bytes`; queued as a DISCOVERY, not fixed in-packet.

## DISCOVERIES (D-069 — for the orchestrator to record; not fixed in-packet)

- **DB-D4 (dxf `max_lines` binds before `max_bytes` for a dense 20 MB file)**: raising the route's
  `DxfLimits.max_bytes` to 20 MiB is necessary but NOT sufficient for the densest real files. The
  reader's OTHER `DxfLimits` defaults are unchanged (dxf_reader.py is READ-ONLY here); a vertex-dense
  ASCII DXF averages **~7.45 bytes/line** [OBSERVED], so the default `max_lines = 2,000,000` becomes
  the binding constraint at **~14.9 MB (~14.2 MiB)** — a 20 MiB dense DXF has ~2.8M lines and is
  refused `TOO_MANY_LINES` before `max_bytes` matters. RECOMMEND: the next `dxf_reader.py` touch (or
  PKT-H) raise `max_lines` alongside `max_bytes` (both well under the reader's `_LIMIT_CEILINGS`:
  `max_lines` ceiling 8,000,000; `max_bytes` ceiling 64 MiB) once real samples exist. Sparse/typical
  drawings are unaffected.
- **DB-D5 (architect-drawing corpus records no DXF byte sizes)**: `docs/research/
  architect-drawing-corpus-2026-09.md` records TIFF/PDF master sizes and the DXF-reference PDF
  (1,756,239 bytes), but no ASCII-DXF file byte sizes, so the dxf-import ceiling was sized from the
  documented 1–20 MB range (per the packet) rather than a corpus measurement. RECOMMEND: a later
  capture task record real DXF byte sizes to validate/refine the 20 MiB ceiling. (Refines DB-D2.)
- **DB-D1/DB-D2 (per-route body ceilings)** from M5-T111 are now DISCHARGED by this packet (scene
  2 MiB, export 1 MiB, dxf 20 MiB). DB-086 (e) (auth setting `request.state.principal`) remains a
  PKT-H item — the auth principal itself is a separate decision, untouched here.

END-OF-REPORT
