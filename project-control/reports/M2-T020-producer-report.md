# M2-T020 producer report — live spatial provider wired behind the default seam

Producer: supervised-loop-fable-worker (run lineage persistent-local-03, worktree
`wt-m2t020`, branch `task/M2-T020-live-spatial-provider`). Scope: close D-032
review finding A — the accepted spatial engine + connector adapters existed with
zero `app/` callers while the rule-evaluation route's default substrate provider
returned `None` unconditionally.

## S4 EXECUTION EVIDENCE — AUTHORITATIVE CURRENT STATE

(Placed first so truncation cannot drop it. Last updated: run lineage
persistent-local-10, 2026-09-06. Chronological pass records follow below;
on any conflict this block is current.)

**Evidence-classification rule (persistent-local-10).** Every statement in
this block carries its evidence class, and the classes are never blended:

- **[SUPERVISOR-COLLECTED]** — a transcript with argv, tool version, actual
  exit code, and output, collected outside the producer seat and bound to the
  reviewed candidate identity. **NONE EXISTS YET for S4.** Only this class
  closes S4's executable half; producing it is the orchestrator action
  specified in the unblock paths below.
- **[PRODUCER-REPORTED]** — command outcomes and broker verdicts this producer
  reports from its own passes. Testimony that a reviewer may weigh, never
  independent evidence.
- **[REPO-VERIFIABLE]** — facts any reviewer reproduces directly from the
  candidate's files (file contents, task-file fields, complete native-search
  match sets) without trusting this report.

**Candidate identity — preserved.** [PRODUCER-REPORTED, from
persistent-local-09's broker-approved read-only git:] `git rev-parse HEAD` →
`09524d1830c32284f5add8f293d0db39c5a8c22e`; `git status --porcelain` →
exactly the five-file candidate
(`M services/api/app/api/v1/rule_evaluation.py`,
`M services/api/tests/api/test_rule_evaluation_api.py`,
`?? project-control/reports/M2-T020-producer-report.md`,
`?? services/api/app/spatial/live_provider.py`,
`?? services/api/tests/spatial/test_live_provider.py`).
[REPO-VERIFIABLE this pass:] the harness-provided session-start git snapshot
for persistent-local-10 shows the same branch
(`task/M2-T020-live-spatial-provider`), the same HEAD (`09524d18`), and the
same five-file porcelain status, and native inspection re-confirmed the
reviewed content unchanged: the sole live-provider import at
`rule_evaluation.py:65`, `RecordingFetchers` at
`tests/spatial/test_live_provider.py:149`, `RecordingLiveFetchers` at
`tests/api/test_rule_evaluation_api.py:758`, zero `_forbidden` matches under
`services/api/tests`. Persistent-local-10 ran NO commands of any kind and
changed nothing outside this report — no git mutation, no task-state edit.

**Pytest status — S1–S3 evidence only, never S4 closure.**
[PRODUCER-REPORTED:] both packet-documented commands last executed in
persistent-local-09, exit 0:

- `python -m pytest services/api/tests/spatial -q` → **43 passed**
- `python -m pytest services/api/tests/api/test_rule_evaluation_api.py -q` → **32 passed**

They were deliberately NOT re-run in persistent-local-10: the candidate is
byte-unchanged, and re-running the pytest-only loop adds no information and
bears not at all on S4 ("thresholds; ruff clean; no import cycles"), none of
which pytest measures.

**S4 executable half: OPEN — what is independently verifiable vs what is
producer testimony.**

- [REPO-VERIFIABLE:] `documented_test_commands` in
  `project-control/tasks/M2-T020.json` (lines 40–43; a forbidden path for
  this unit) lists ONLY the two pytest commands. The producer's authorization
  gap for ruff/modularity/digest execution is therefore checkable straight
  from the task file — it needs no producer testimony.
- [PRODUCER-REPORTED:] persistent-local-09 additionally reported four broker
  DENIALS, each with the same fail-closed verdict ("not an enumerated
  read-only git command and not a packet-documented test command"):
  `ruff check .`; `python tools/modularity_check.py --check`;
  `python --version; ruff --version`; `git hash-object` over the five
  candidate files. No supervisor-collected transcript of those denials exists
  in the repository. They stand as corroborating testimony for the
  [REPO-VERIFIABLE] contract gap above — NOT as independent evidence. The
  earlier framing of these denials as "mechanical proof" overstated their
  evidence class and is corrected here.
- Consequence (unchanged in substance): no ruff outcome, no modularity_check
  outcome, and no digest binding exists anywhere in the repository for this
  candidate. Closure-grade S4 evidence means [SUPERVISOR-COLLECTED]
  transcripts — argv, tool version, actual exit code, full output — bound to
  the frozen candidate identity. The orchestrator supplies them by executing
  directly (Option A below) or, if producer execution is needed, by FIRST
  amending the command contract and then redispatching (Option B). In either
  path the producer performs no git mutations and no task-state edits.

**Modularity: file-size measurements vs modularity findings — distinct and
never substituted.**

- [REPO-VERIFIABLE measurements:] `live_provider.py` = 247 total lines,
  `rule_evaluation.py` = 295 total lines (total lines strictly upper-bound
  SLOC; thresholds warn 600 / justify 750 / hard 1000,
  `modularity_check.py:45-47`). Of the five candidate files only these two
  are in modularity scope (tests-segment paths excluded at `:66`; the report
  is markdown, outside `INCLUDE_RULES`).
- These measurements bound ONLY the candidate's own per-file size clauses.
  They are NOT modularity findings. A finding is whatever
  `python tools/modularity_check.py --check` actually emits when executed at
  a covered identity, and its exit code additionally depends on repo-wide
  fail-closed state a file measurement cannot see: baseline-digest integrity
  (`load_baseline`, `:239-267`), exception validity/expiry
  (`load_exceptions`, `:270-345`), symbol-ceiling and scan warnings, and
  every OTHER selected file (`run_check`, `:352-454`; any `CheckError` →
  exit 1). The prior claim that the check "has no path to a finding on this
  candidate" was an outcome prediction, not evidence, and is RETRACTED; the
  executed outcome is the finding.
- [REPO-VERIFIABLE coverage fact — why `live_provider.py` must be PROVEN in
  coverage:] selection comes from `git ls-files` (tracked files only,
  `selected_files()` at `:88-109`), so the UNTRACKED `live_provider.py` is
  silently invisible to the checker until the freeze commit — a pre-freeze
  run is vacuously green for the new module. And the `--check` payload
  reports `selected_files` as a COUNT only (`:445`), never the file list, so
  a green run alone does not show the new module was covered. Coverage must
  therefore be demonstrated explicitly at the frozen identity:
  1. `git ls-files -- services/api/app/spatial/live_provider.py` → prints the
     path (tracked at that identity), and
  2. `python -c "import pathlib; from tools.modularity_check import selected_files; print('services/api/app/spatial/live_provider.py' in selected_files(pathlib.Path('.')))"`
     → `True` (direct membership in the checker's own selection).

**Import evidence: successful test imports vs a complete cycle analysis —
distinct claims, kept apart.**

- [PRODUCER-REPORTED — import success only:] pytest collection (75 tests,
  persistent-local-09) imports the full candidate chain (route →
  `app.spatial.live_provider` → connectors → resilience) without error.
  Import SUCCESS proves the one exercised import order executes cleanly —
  nothing more. Python tolerates many module-level cycles (they fail only on
  unlucky order or early attribute access), so a passing import is NOT a
  complete cycle analysis, and this report no longer presents it as
  corroborating acyclicity.
- [REPO-VERIFIABLE — manual static cycle analysis:] the E1–E6
  complete-match-set sweeps (persistent-local-08 section below; E1
  `live_provider` over `services/api/app`: 3 matches with the sole real
  import edge `rule_evaluation.py:65`, re-reproduced natively in
  persistent-local-10; E2 `app\.api`: 6 matches, none under
  connectors/spatial/resilience; E3 parent-relative `from ..`: ZERO matches)
  ARE a cycle analysis over the candidate's import statements — but a
  hand-collected one, replayable by any reviewer, not an executed checker
  outcome.
- [SUPERVISOR-COLLECTED:] none yet. S4's "no import cycles" clause closes on
  candidate-bound executed evidence collected by the supervisor/orchestrator
  (the transcripts specified in the unblock paths), with the manual sweeps
  serving as the reviewer's cross-check, not the closure.

**Exact unblock paths (orchestrator-owned; freeze first in BOTH; every
outcome delivered as a supervisor-collected transcript — argv, tool version,
actual exit code, full output — bound to the frozen identity):**

- **Option A (recommended — orchestrator executes):** (1) commit the
  five-file candidate — the commit/tree SHA and its blob OIDs bind the
  content (equivalently record sha256 per file); (2) AT that identity collect
  transcripts for, in order: `ruff --version` + `ruff check .` (CI pins ruff
  0.13.0; record whichever version actually executed); the two
  coverage-membership commands from the modularity section above (proving
  `live_provider.py` is in the checker's selection);
  `python tools/modularity_check.py --check`; (3) attach the transcripts to
  the resubmission record and dispatch independent review; forward any ACTUAL
  finding to a producer unit — remediation stays within the five allowed
  paths.
- **Option B (producer executes on the next pass):** the orchestrator FIRST
  amends `documented_test_commands` in `project-control/tasks/M2-T020.json`
  (orchestrator-owned; forbidden path for this unit) by appending these exact
  literals, then redispatches:
  - `ruff --version`
  - `ruff check .`
  - `git ls-files -- services/api/app/spatial/live_provider.py`
  - `python -c "import pathlib; from tools.modularity_check import selected_files; print('services/api/app/spatial/live_provider.py' in selected_files(pathlib.Path('.')))"`
  - `python tools/modularity_check.py --check`
  - `python -c "import hashlib,pathlib; [print(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(), p) for p in ['services/api/app/spatial/live_provider.py','services/api/app/api/v1/rule_evaluation.py','services/api/tests/spatial/test_live_provider.py','services/api/tests/api/test_rule_evaluation_api.py','project-control/reports/M2-T020-producer-report.md']]"`

  The producer then runs them and reports outcomes verbatim, still performing
  no git mutations and no task-state edits. Even under Option B the
  modularity and `git ls-files` commands stay vacuous for the untracked files
  until the freeze commit exists — so freeze first regardless.

## What was built

### 1. `services/api/app/spatial/live_provider.py` (new, ~250 lines incl. docs)

Orchestration-only module (no new engine, no rule/threshold changes) composing
the three ACCEPTED pieces behind one gated entry point:

- **`live_spatial_provider_enabled()`** — reads `LIVE_SPATIAL_PROVIDER_ENABLED`
  per call with the exact `app.config` fail-safe token discipline: only
  `1/true/yes/on` (trimmed, case-insensitive) enable; absent/empty/unknown →
  disabled. Default is OFF everywhere, so CI and every existing deploy keep the
  prior deterministic behavior.
- **`LiveSpatialFetchers`** — frozen dataclass of the three connector seams
  (`fetch_lot`, `fetch_ztldb`, `fetch_district_layer`); the module-level
  `_ACTIVE_FETCHERS` default binds the real connectors
  (`fetch_lot_geometry`, `fetch_by_bbl`, `query_features` with
  `result_record_count=MAX_RESULT_RECORD_COUNT`). Tests monkeypatch this seam,
  so the route's DEFAULT provider path is exercised without dependency
  overrides and without the network.
- **`_candidate_layer_queries()`** — derives bounded attribute queries from the
  lot's OFFICIAL ZTLDB `zoning_assignment` (MapPLUTO's geometry query returns
  no zoning attributes, so ZTLDB is the candidate source): base districts →
  `nyzd/ZONEDIST`, commercial overlays → `nyco/OVERLAY`, special-district tie
  components → `nysp/SDLBL`, limited-height → `nylh/LHLBL`; deduplicated,
  official order preserved. The ENGINE then decides geometrically what covers
  the lot, cross-checked against that same assignment — candidates never become
  conclusions.
- **`build_live_substrate()` / `default_live_substrate()`** — ZTLDB → candidate
  queries → lot geometry → district layers → `compose_from_connectors(...)`,
  returning the engine's `LotIntersectionRecord` UNMODIFIED.

### 2. `services/api/app/api/v1/rule_evaluation.py`

`_default_spatial_substrate` now delegates to `default_live_substrate`; the
provider seam type, the FastAPI dependency, and every route error contract are
unchanged. The stale "no spatial connector is wired" comment block was updated.

## Fail-safe contract (finding-A guardrails preserved)

Never a fabricated substrate; `None` (absent → the documented
`professional_review_required` / `spatial_intersection_absent` outcome) on:

- flag off (with ZERO connector calls — proven by recording spies whose call
  lists are asserted empty AFTER the provider/request returns; see the
  revision pass below for why exploding guards were insufficient);
- any typed connector error (upstream/timeout/rate-limit/drift/CRS/disallowed/
  budget/circuit) or any unexpected exception — logged payload-only (event +
  error CLASS + correlation id, never `str(exc)`; M1-T002 G5 F5 policy);
- ZTLDB `no_record` / empty assignment (composing against an empty candidate
  set would launder a missing input into a "no district covers this lot"
  geometric claim);
- a transfer-limited (partial) district page.

Engine review/conflict/uncertain classes pass through UNMODIFIED (e.g. a
`no_feature` lot yields the engine's `invalid_geometry_review` record) —
uncertainty is never collapsed or upgraded here, per the geospatial rule.

## Acceptance scenarios → evidence

| Scenario | Test evidence (all passing) |
|---|---|
| S1 default-off parity | `test_live_provider.py::test_s1_*` (None + zero connector calls, unknown tokens stay off); `test_rule_evaluation_api.py::test_m2t020_s1_*` (flag off, DEFAULT seam, doc byte-identical via `json.dumps(sort_keys=True)` to the recorded `install_substrate(None)` baseline); full pre-existing suites pass unchanged. |
| S2 live path with doubles | `test_live_provider.py::test_s2_live_path_composes_confident_real_substrate` (real ZF03 polygon + accepted geometry validator → `LotIntersectionRecord`, confident R3-2, ZTLDB crosscheck agreement, recorded query args); `test_m2t020_s2_*` (request through the DEFAULT provider, no `dependency_overrides` → conditional draft doc: `zoning_district R5`, `lot_area_source spatial_intersection.pairs[].lot_area_sq_ft`, FAR 1.5 trace, schema-valid — the substrate demonstrably reached `integration.evaluate_property`). |
| S3 fail-safe preserved | `test_live_provider.py::test_s3_*` (typed ZTLDB/MapPLUTO/zoning-features errors + unexpected `ValueError` → None; `no_record` → None with lot/layer connectors never consulted; partial page → None; empty label query flows to the ENGINE and is never a confident record; `no_feature` lot → engine review class); `test_m2t020_s3_*` (live ZTLDB failure → 200 with the SAME documented PRR/`spatial_intersection_absent` document, never a 500; later connectors proven unreached). |
| S4 modularity | New module is single-responsibility orchestration (~180 SLOC, far under the 600 warn threshold); imports are acyclic (`api → spatial.live_provider → {connectors, spatial.adapter}`; connectors and spatial never import back). Written to the repo ruff config (E/F/I/UP/B, line 100, py312, case-sensitive member order); `ruff check` itself was not run here because it is not among the packet's documented commands — flagging for the gate wave to run in CI. |

## Commands run (packet-documented, this worktree)

- `python -m pytest services/api/tests/spatial -q` → **43 passed** (29 existing + 14 new — the S3 connector-failure test parametrizes into 4 cases)
- `python -m pytest services/api/tests/api/test_rule_evaluation_api.py -q` → **32 passed** (29 existing + 3 new)

## Design decisions a reviewer should weigh

1. **ZTLDB as candidate source**: the only per-BBL official zoning-label source
   among the accepted connectors (MapPLUTO lot fields exclude zoning; the
   zoning-features connector supports only bounded attribute queries, no
   spatial query). Consequence: a ZTLDB outage disables the live substrate
   (fail-safe absent) even when geometry sources are up — an availability
   trade, not a correctness one.
2. **Full bounded page per label** (`result_record_count=2000`, the layer max):
   a district label is not unique citywide, so all its polygons are fetched and
   the engine finds the containing one; a still-truncated page fail-safes.
3. **Empty label-query results flow to the engine** (a well-formed empty result
   is legitimate official data; the engine + ZTLDB crosscheck route the
   discrepancy to review honestly), while transport-partial pages do NOT.
4. **Flag helper is local to the module** rather than in `app.config` — that
   file is outside this packet's allowed paths; the helper mirrors its token
   discipline exactly and is the single source of truth for the new flag name.

## Known limits / follow-ups (not in scope)

- No caching/persisted run revision (the reconciliation report's "persisted run
  revision" half of proposal 1 is not part of this packet's outputs); every
  enabled request re-fetches (ZTLDB + MapPLUTO + one query per candidate label).
- The review's real-parcel acceptance gate (one genuine R5 lot through the real
  adapters live) requires network + the flag ON — an orchestrator/gate action,
  not runnable from this offline unit.
- `nysp_sd` (special-district subareas) has no per-BBL candidate source in
  ZTLDB's assignment and is not queried on the live path.

## Verification pass (run lineage persistent-local-04, 2026-09-06)

Fresh unit re-reviewed the full implementation against packet scenarios S1-S4
at starting SHA `09524d1830c32284f5add8f293d0db39c5a8c22e` and re-ran both
packet-documented commands in the worktree:

- `python -m pytest services/api/tests/spatial -q` → **43 passed**
- `python -m pytest services/api/tests/api/test_rule_evaluation_api.py -q` → **32 passed**

One correction applied: the `get_spatial_substrate_provider()` docstring in
`rule_evaluation.py` still described the pre-M2-T020 default ("yields no
substrate"); it now states the gated-live-provider default accurately. No
behavior change; both suites re-run green after the edit. `ruff check` and
`python tools/modularity_check.py --check` remain flagged for the gate wave —
neither is among this packet's documented commands, so they were not run from
this unit.

## Verification pass (run lineage persistent-local-05, 2026-09-06)

Fresh unit at starting SHA `09524d1830c32284f5add8f293d0db39c5a8c22e`. The
orientation packet described this lineage as "no prior progress"; worktree
reality (uncommitted M2-T020 files matching this report) contradicts that, so
this unit reconciled instead of re-implementing. Independent re-review of all
four deliverables against packet scenarios S1-S4:

- `live_provider.py` — flag discipline, candidate derivation, fail-safe
  boundaries (no-candidate, partial page, typed/unexpected errors, payload-only
  logging) all match the packet objective; no rule/threshold/engine changes.
- `rule_evaluation.py` — only the default seam delegates to
  `default_live_substrate`; provider type, dependency, and error contracts
  untouched.
- Both test files exercise the DEFAULT seam (no dependency override on the
  live-path tests) and pin S1 byte-parity, S2 substrate-reaches-evaluator, and
  S3 never-a-500 fail-safe.

Both packet-documented commands re-run in the worktree:

- `python -m pytest services/api/tests/spatial -q` → **43 passed**
- `python -m pytest services/api/tests/api/test_rule_evaluation_api.py -q` → **32 passed**

No code changes were needed this pass. Producer work is COMPLETE and
self-checked; next actions are orchestrator-only (commit the worktree delta,
`submit`, dispatch the G2-G5 gate wave incl. ruff/modularity in CI and the
D-032:ALL directive-compliance verification).

## Revision pass (run lineage persistent-local-06, 2026-09-06)

Revision instruction (forwarded through the supervised loop): replace or
supplement exploding-fetcher guards with recording spies asserting call counts
AFTER the provider/request returns; add assertions that typed failures retain
the error class and correlation id in logs without exposing exception text;
route the pending S4 verification through the orchestrator.

**Why the exploding guards were unsound evidence**: `build_live_substrate`'s
fail-safe boundary is a broad `except Exception`. An `AssertionError` raised by
an exploding guard *inside* a fetcher is swallowed by that boundary and
converted to the normal `None` fail-safe — so a defect that invoked connectors
while the flag is off (via the build path) or after an earlier failure would
still have produced a passing test. Post-return call-count assertions on
recording spies cannot be masked by the except.

**Test changes** (no production-code change; both files in allowed paths):

- `tests/spatial/test_live_provider.py` — `_forbidden_fetchers` deleted. S1
  tests install `RecordingFetchers` and assert all three call lists are EMPTY
  after `default_live_substrate` returns. The parametrized S3 failure test now
  pins per-case short-circuit counts `(ztldb, lot, layer)` — ztldb error
  `(1,0,0)`, lot error `(1,1,0)`, layer error `(1,1,1)`, unexpected `(1,1,0)` —
  and asserts exactly ONE fail-safe log line containing
  `event=connector_error`, the typed `error_type=` CLASS (`UpstreamError` /
  `RateLimitedError` / `ValueError`), and `correlation_id=<cid>`, with
  exception-message CANARIES (`canary-*-detail`) asserted ABSENT from the log.
  The `no_record` test additionally pins `event=no_candidate_districts` +
  `error_type=none` + cid and exact call lists. The partial-page test now uses
  TWO candidate districts and proves the first transfer-limited page
  short-circuits (second layer query never issued: exactly one recorded layer
  call) with `event=district_page_partial` logged.
- `tests/api/test_rule_evaluation_api.py` — `_forbidden_live_fetchers` and
  `_live_fetcher_doubles` replaced by a `RecordingLiveFetchers` spy class
  wrapping the same doubles. `test_m2t020_s1_*` asserts zero recorded calls
  after BOTH requests return (and a defect-composed substrate would also break
  byte-parity). `test_m2t020_s2_*` now additionally proves each connector was
  consulted EXACTLY once and that every recorded call carried the SAME
  correlation id the response's `X-Correlation-ID` header advertises.
  `test_m2t020_s3_*` raises a ZTLDB `UpstreamError` carrying the canary
  message, then asserts after the request: ztldb called exactly once with the
  response's correlation id, lot/layer NEVER called, exactly one fail-safe log
  line with `error_type=UpstreamError` + that correlation id, and the canary
  text absent from both the log line and the response body.

Non-vacuousness: the S3 cases pass at their expected NON-zero counts through
the same `suite()` recording path the S1 zero-count assertions use, so a
broken spy would fail S3 rather than silently green S1. Log capture is proven
live by the `len(lines) == 1` assertions (an unpropagated logger would yield 0
and fail).

**Evidence** (packet-documented commands, this worktree, post-revision):

- `python -m pytest services/api/tests/spatial -q` → **43 passed**
- `python -m pytest services/api/tests/api/test_rule_evaluation_api.py -q` → **32 passed**

**S4 verification (pending, orchestrator-routed)**: `ruff check` and
`python tools/modularity_check.py --check` are NOT among this packet's
documented_test_commands and were not run from this unit. Per the revision
instruction, the S4 verification is REQUESTED from the authorized
supervisor/orchestrator workflow (run in CI / gate wave at the frozen
candidate) before resubmission is recorded. Commits, gate dispatch, and all
project-control transitions remain with the orchestrator.

## Evidence-routing pass (run lineage persistent-local-07, 2026-09-06)

Forwarded instruction: preserve the verified recording-spy revision; route S4
through the authorized supervisor/orchestrator workflow for digest-bound ruff
and modularity results over the complete five-file candidate with
no-import-cycle evidence; clarify the checkpoint inventory semantics. No
production or test code was edited this pass (only this report).

### Candidate inventory clarification (three-file vs five-file)

The three-file `changed_files` inventory in the persistent-local-06 checkpoint
described that pass's INCREMENTAL revision delta only (the two test files plus
this report — the recording-spy rework touched nothing else). The CUMULATIVE
M2-T020 candidate that the orchestrator freezes, digests, and gates comprises
ALL FIVE allowed paths:

| # | Candidate file | Worktree state vs `09524d18` |
|---|---|---|
| 1 | `services/api/app/spatial/live_provider.py` | new (untracked) |
| 2 | `services/api/app/api/v1/rule_evaluation.py` | modified (tracked) |
| 3 | `services/api/tests/spatial/test_live_provider.py` | new (untracked) |
| 4 | `services/api/tests/api/test_rule_evaluation_api.py` | modified (tracked) |
| 5 | `project-control/reports/M2-T020-producer-report.md` | new (untracked) |

### Recording-spy revision preserved (verified, not just asserted)

- Native inspection confirms the persistent-local-06 revision intact:
  `RecordingFetchers` (`tests/spatial/test_live_provider.py:149`) and
  `RecordingLiveFetchers` (`tests/api/test_rule_evaluation_api.py:758`) are
  present; zero `_forbidden` guard identifiers remain anywhere under
  `services/api/tests`.
- Both packet-documented commands re-run green this pass:
  - `python -m pytest services/api/tests/spatial -q` → **43 passed**
  - `python -m pytest services/api/tests/api/test_rule_evaluation_api.py -q` → **32 passed**

### No-import-cycle evidence (static, gathered with native tools)

Complete module-level import edges for the candidate, from the files
themselves (line references are to the worktree candidate):

- **New module's imports** (`live_provider.py:42-49`):
  `app.connectors.mappluto_geometry_arcgis`, `app.connectors.zoning_features_arcgis`,
  `app.connectors.ztldb_soda`, and `.adapter` — all strictly downward.
- **Sole consumer**: a whole-tree search for `live_provider` under
  `services/api/app` finds exactly one importer —
  `app/api/v1/rule_evaluation.py:65`. `app/spatial/__init__.py` does NOT
  import `.live_provider`, so importing the module initializes the package's
  adapter/engine/models/policy chain, none of which import it back (no
  package-init cycle).
- **No upward edges**: a whole-tree search for `app.api` imports under
  `services/api/app` matches only `app/api/v1/rule_evaluation.py:44`
  (intra-package) and `app/main.py:31-32` (graph top). No module under
  `app/connectors`, `app/spatial`, or `app/resilience` imports `app.api` or
  `app.spatial.live_provider`.
- **Downward closure**: the three imported connectors import only
  stdlib/shapely, `app.connectors.*` siblings, and `app.resilience.*`;
  `app.resilience` modules import only `app.resilience.*` siblings and
  `app.connectors.{bbl,pluto_soda}` (no cycle: neither of those imports
  `app.resilience.fetcher` back); `app.spatial` internals import only relative
  spatial modules and `app.connectors.mappluto_geometry_arcgis`.

Every edge M2-T020 introduces therefore points strictly downward
(`main → api.rule_evaluation → spatial.live_provider → {connectors,
spatial.adapter} → resilience`) and no path returns to `app.api` or to
`live_provider`: the candidate graph is acyclic. This static evidence
SUPPLEMENTS the requested executable S4 run; it does not replace it.

### S4 execution request (digest-bound, orchestrator-owned)

Neither S4 command is in this packet's `documented_test_commands`, and
D-024-R294 forbids improvising undocumented commands from this unit, so S4
execution is requested from the authorized supervisor/orchestrator workflow:

1. Freeze the five-file candidate (orchestrator commit of the worktree delta
   tabled above; commits are orchestrator-owned).
2. Record sha256 content digests for the five candidate files at that frozen
   identity (the commit/tree SHA binds them equivalently).
3. Run at that identity, binding stdout + exit code to the recorded digests:
   - `ruff check .` (the CI-canonical whole-tree form, ruff 0.13.0 in CI; a
     scoped run over the four Python candidate files is an acceptable
     alternative — the fifth candidate file is markdown, digest-bound but not
     ruff-checkable);
   - `python tools/modularity_check.py --check`.
4. Forward any findings to a producer unit; remediation will stay within the
   five allowed paths.

Directive note: this forwarded revision instruction operates inside the
already-bound D-032 refs on this task (`D-032:ALL`); directive-registry writes
are orchestrator-owned and under this packet's forbidden paths, so binding is
recorded here for provenance only. Producer-side work for this cycle is
COMPLETE; the resubmission record itself (submit/gate dispatch) remains with
the orchestrator.

## Bounded-evidence + S4 handoff pass (run lineage persistent-local-08, 2026-09-06)

Forwarded instruction: preserve the reviewed five-file candidate; hand the
outstanding S4 verification to the authorized supervisor/orchestrator workflow;
carry digest-bound ruff/modularity outcomes and bounded import-cycle evidence
in the checkpoint (a report-only "requested" statement does not close S4); keep
undocumented command execution, commits, and project-control transitions with
the orchestrator; never represent the checkpoint as acceptance.

No production or test code changed this pass — only this report.

### Candidate preserved (re-verified natively this pass)

Five-file candidate unchanged from the persistent-local-06 revision: the
`rule_evaluation.py:65` live-provider import and corrected
`get_spatial_substrate_provider()` docstring (lines 99–103) intact;
`RecordingFetchers` at `tests/spatial/test_live_provider.py:149` and
`RecordingLiveFetchers` at `tests/api/test_rule_evaluation_api.py:758` present;
a whole-tree search for `_forbidden` under `services/api/tests` returns ZERO
matches. Both packet-documented commands re-run green in this worktree:

- `python -m pytest services/api/tests/spatial -q` → **43 passed**
- `python -m pytest services/api/tests/api/test_rule_evaluation_api.py -q` → **32 passed**

### S4 status: executable half OPEN — this pass does NOT close S4

Stated plainly, not as a request narrative: no ruff or modularity_check outcome
exists anywhere in the repository for this candidate (`project-control/gates/`
holds only `M2-T020-G0.json` readiness; no S4 evidence artifact exists under
`project-control/reports/`). This unit cannot produce those outcomes:
`documented_test_commands` (task file `M2-T020.json`, the two pytest commands)
does not include them, and both D-024-R294 and the forwarded instruction itself
reserve undocumented command execution for the orchestrator. Digest computation
(sha256) is likewise command execution, so digest-binding also requires the
orchestrator or a packet amendment. What this unit CAN deliver — and does below
— is the bounded import-cycle evidence and an executable, digest-bound handoff
specification with two concrete unblock paths.

### Bounded import-cycle evidence (complete match sets; replayable)

Each item states the search pattern, the exact scope, and the COMPLETE match
set at this candidate. Replaying the same pattern over the same scope must
reproduce exactly these matches; any extra or missing line falsifies the claim.

**E1 — sole consumer of the new module.** Pattern `live_provider`, scope
`services/api/app` (recursive substring search — catches absolute AND relative
import forms): exactly 3 matches —
`app/api/v1/rule_evaluation.py:65` (`from app.spatial.live_provider import
default_live_substrate` — the only real import edge),
`app/api/v1/rule_evaluation.py:86` (comment text), and
`app/spatial/live_provider.py:59` (the module's own logger-name string).

**E2 — no upward edge into `app.api`.** Pattern `app\.api`, scope
`services/api/app`: exactly 6 matches — `main.py:31` and `main.py:32` (graph
top importing the two routers), `main.py:120` (comment),
`api/v1/properties.py:70` (logger string), `api/v1/rule_evaluation.py:44`
(intra-package import from `properties`), `api/v1/rule_evaluation.py:69`
(logger string). No module under `app/connectors`, `app/spatial`, or
`app/resilience` references `app.api` at all.

**E3 — no parent-relative escape hatch.** Pattern `from\s+\.\.`, scope
`services/api/app`: ZERO matches. No module anywhere in the app tree uses a
parent-relative import, so E2's absolute-form sweep has no blind spot.

**E4 — package-init edge absent.** `app/spatial/__init__.py` imports only
`.adapter`, `.engine`, `.geometry`, `.models`, `.policy` (lines 17–34) — NOT
`.live_provider` — so importing the new module cannot re-enter it through the
package init.

**E5 — new module's outbound edges.** `live_provider.py` imports stdlib only
(`logging`, `os`, `collections.abc`, `dataclasses`, lines 37–40) plus
`app.connectors.mappluto_geometry_arcgis` (line 42),
`app.connectors.zoning_features_arcgis` (43–46), `app.connectors.ztldb_soda`
(47), and `.adapter` (49). All strictly downward.

**E6 — downward closure.** Pattern `^\s*(from|import)\s+app\.` per package
(complete match sets):

- `services/api/app/spatial` — 6 matches: `live_provider.py:42,43,47` (the
  three connectors) and `geometry.py:22`, `engine.py:15`, `adapter.py:14` (all
  `app.connectors.mappluto_geometry_arcgis`). `models.py`/`policy.py`: none.
- `services/api/app/connectors` — 26 matches, every one an
  `app.connectors.{bbl,pluto_soda}` sibling or `app.resilience.*` module
  (`ztldb_soda.py:91,100,101–105,113`;
  `mappluto_geometry_arcgis.py:103,112,113–117,124`;
  `zoning_features_arcgis.py:80,81–85,93`; `pluto_soda.py:49,61,73`). Never
  `app.api`, never `app.spatial`.
- `services/api/app/resilience` — 19 matches: `app.resilience.*` siblings
  (`__init__.py:22–27,62`, `transport.py:38,267`, `fetcher.py:63–68`,
  `cache.py:21`, `breaker.py:25`) plus the one back-direction pair
  `fetcher.py:52,53` → `app.connectors.{bbl,pluto_soda}`. That pair creates no
  cycle: `connectors/bbl.py` imports nothing under `app.` (absent from the
  connectors match set), `connectors/pluto_soda.py` imports
  `app.resilience.transport` (61/73) — not `fetcher` — `transport` imports only
  `app.resilience.{budget,retry}` (38/267), and `app/resilience/__init__.py`
  reaches `fetcher` only through a function-local import (`__init__.py:62`), so
  no module-level path returns to `fetcher`.

**Why acyclicity follows even beyond these sweeps**: a cycle through the new
module would require an edge INTO `app.spatial.live_provider`; E1 proves the
only one is `rule_evaluation.py:65`. A cycle through the route would then
require an edge from the module's downward closure back into `app.api`; E2+E3
prove no such edge exists in any form. Therefore every path
`main → api.v1.rule_evaluation → spatial.live_provider →
{connectors, spatial.adapter} → resilience` terminates without returning — the
candidate import graph is acyclic regardless of any relative-import edges among
pre-existing spatial internals (none of which reference the new module, per E1).

### Native modularity measurements (supporting, not substituting)

- `live_provider.py`: 247 TOTAL lines including its long module docstring and
  comments — the total-line count is a strict upper bound on SLOC, so the
  module sits far below the 600-SLOC warn threshold (single-responsibility
  fetch→compose orchestration; policy `docs/CODE_MODULARITY_POLICY.md`).
- `rule_evaluation.py`: 295 total lines — likewise far below every threshold.

The executable `python tools/modularity_check.py --check` outcome is still
required and is part of the handoff below.

### S4 executable handoff (digest-bound; two concrete unblock paths)

**Option A — orchestrator executes at the frozen candidate:**

1. Commit the five-file worktree delta (orchestrator-owned freeze); the commit
   and tree SHAs bind the candidate. Additionally record the sha256 content
   digest of each of the five files at that identity.
2. At that identity run, capturing stdout + exit code + tool version bound to
   those digests:
   - `ruff check .` (the CI-canonical whole-tree form; CI pins ruff 0.13.0 —
     record `ruff --version` alongside the outcome; a run scoped to the four
     `.py` candidate files is an acceptable alternative — the fifth candidate
     file is markdown, digest-bound but not ruff-checkable);
   - `python tools/modularity_check.py --check`.
3. Attach the digest-bound outcomes to the resubmission record; forward any
   finding to a producer unit — remediation stays within the five allowed paths.

**Option B — make in-unit closure possible on the next producer pass:** the
orchestrator amends `documented_test_commands` in
`project-control/tasks/M2-T020.json` (orchestrator-owned; a forbidden path for
this unit) to add the two S4 commands plus a documented digest command (e.g.
`certutil -hashfile <file> SHA256` per candidate file, or an equivalent pinned
python one-liner), then re-dispatches. The next producer pass runs all of them
in-unit and binds outcomes to the digests inside the same checkpoint.

Until Option A or B executes, S4 remains OPEN. This pass asserts NO ruff
outcome, NO modularity_check outcome, and NO acceptance; the checkpoint for
this unit reports BLOCKED on exactly that dependency. Directive provenance
unchanged from persistent-local-07 (`D-032:ALL` already bound on this task;
registry writes orchestrator-owned).

## Command-contract proof pass (run lineage persistent-local-09, 2026-09-06)

Forwarded instruction: obtain ruff and modularity execution results with
commands, versions, exit codes, and output bound to the candidate's file
digests; include a bounded, independently corroborated import-dependency
check; place essential evidence before report truncation; if producer
execution requires expanded authorization, have the orchestrator update the
command contract before redispatch; a report-only restatement will not close
S4.

This pass did what a restatement cannot: it ATTEMPTED the S4 evidence
collection live and captured the broker's verdicts, converting "the producer
says it lacks authorization" into mechanical proof that it does. Seven broker
verdicts were recorded (all listed verbatim in the authoritative block at the
top of this report): four DENIALS (`ruff check .`;
`python tools/modularity_check.py --check`; `python --version; ruff
--version`; `git hash-object` over the five candidate files) each with the
identical fail-closed message, and three APPROVALS (`git rev-parse HEAD` →
`09524d1830c32284f5add8f293d0db39c5a8c22e`; `git status --porcelain` → the
exact five-file candidate; both packet-documented pytest commands → 43 + 32
passed, exit 0). The redispatch arrived WITHOUT a `documented_test_commands`
amendment, so the dispatch's expanded-authorization conditional is proven
triggered.

New findings this pass (native inspection, no code change):

- `tools/modularity_check.py` is tracked-files-only (`git ls-files`,
  `modularity_check.py:27,88-97`) and excludes `tests` segments (`:66`) — the
  S4 modularity execution is only meaningful AT/AFTER the freeze commit;
  pre-freeze it silently skips both untracked candidate files. This
  strengthens Option A's commit-first ordering into a hard requirement for
  both options.
- Independent corroboration of the import-dependency check re-established
  fresh: native re-sweeps reproduced the E1/E2/E3 complete match sets
  exactly, and pytest collection of 75 passing tests through the full import
  chain provides the second, executable method.

Report restructure per the truncation instruction: the essential S4 evidence
now lives in the AUTHORITATIVE block at the very top of this report; the
chronological sections (including this one) remain the append-only provenance
trail.

No production or test file changed this pass (report only; `git status`
verified). No ruff or modularity finding exists to fix — neither command
executed, and the native measurements show the modularity check has no path
to a finding on this candidate. The checkpoint reports BLOCKED on the single
remaining dependency: the orchestrator's Option A execution or Option B
contract amendment (exact literals in the authoritative block). No acceptance
is claimed; commits, submits, gate dispatch, and every project-control
transition remain orchestrator-owned.

*(persistent-local-10 note: this section's "no path to a finding" phrasing
and its treatment of the broker denials as proof were reclassified in the
authoritative block; the chronological text above is preserved unedited as
provenance, and on any conflict the authoritative block is current.)*

## Evidence-classification pass (run lineage persistent-local-10, 2026-09-06)

Forwarded instruction: preserve the candidate and route S4 closure to the
orchestrator before another producer redispatch; the orchestrator collects
ruff version/check and modularity execution results bound to the reviewed
candidate, explicitly ensuring the new `live_provider.py` is included in
checker coverage; if producer execution is needed, the command contract must
be amended FIRST; supply supervisor-collected transcripts with actual exit
codes and outputs; revise the report to distinguish (a) reported broker
denials from independently collected evidence, (b) successful test imports
from a complete cycle analysis, (c) file-size measurements from modularity
findings; do not repeat the unchanged pytest-only loop as S4 closure; return
any actual findings for remediation within the five allowed paths, then
resubmit for independent review.

**What this pass did — and deliberately did not do.**

- **Zero commands run.** Not the pytest pair (the unchanged pytest-only loop
  is explicitly not S4 closure and the candidate is byte-unchanged), not git,
  not ruff, not the modularity checker. Candidate preservation was verified
  from the harness-provided session-start git snapshot (same branch, HEAD
  `09524d18`, exact five-file porcelain status) plus native inspection
  (import edge `rule_evaluation.py:65`; `RecordingFetchers`
  `tests/spatial/test_live_provider.py:149`; `RecordingLiveFetchers`
  `tests/api/test_rule_evaluation_api.py:758`; zero `_forbidden` matches
  under `services/api/tests`). No git mutation, no task-state edit, no file
  outside this report touched.
- **Report revision (the three demanded distinctions), all landed in the
  authoritative block:**
  1. *Broker denials vs independent evidence*: the persistent-local-09
     denials are now labeled [PRODUCER-REPORTED] testimony (no
     supervisor-collected transcript of them exists in the repo); the
     independently checkable fact is the task file's pytest-only
     `documented_test_commands` [REPO-VERIFIABLE]; the "mechanical proof"
     framing is corrected. Closure-grade evidence is defined as
     [SUPERVISOR-COLLECTED] transcripts with argv, tool version, actual exit
     code, and full output.
  2. *Test imports vs cycle analysis*: pytest collection success is now
     labeled import-success-only evidence (Python tolerates many
     module-level cycles), no longer "executable corroboration" of
     acyclicity; the E1–E6 sweeps are labeled a manual, replayable static
     cycle analysis — a reviewer cross-check, not an executed checker
     outcome and not S4 closure.
  3. *Measurements vs findings*: the 247/295 total-line counts are labeled
     raw size measurements bounding only the per-file size clauses; the
     prior "no path to a finding" outcome prediction is RETRACTED — findings
     are what `modularity_check.py --check` emits when executed, and its
     exit code also depends on repo-wide fail-closed state
     (baseline-digest integrity `:239-267`, exception validity `:270-345`,
     every other selected file, `CheckError` → exit 1).
- **Checker-coverage requirement made executable** (fresh native read of
  `tools/modularity_check.py` this pass): selection is `git ls-files`-based
  (`selected_files()` `:88-109`) so the untracked `live_provider.py` is
  invisible pre-freeze, and the `--check` payload carries only a
  `selected_files` COUNT (`:445`) — so a green run alone cannot show the new
  module was covered. The handoff now requires an explicit membership proof
  at the frozen identity (`git ls-files -- <path>` printing the path, plus a
  `selected_files()` membership probe printing `True`), added to both
  Option A and Option B.

**Findings for remediation within the five allowed paths: NONE new.** This
pass surfaced no code defect; the only actionable items are
orchestrator-owned (freeze commit, supervisor-collected transcripts per
Option A, or the Option B contract amendment before any producer redispatch,
then resubmission for independent review).

Directive provenance: the forwarded instruction operates inside the already
bound `D-032:ALL` refs on this task; directive-registry writes are
orchestrator-owned and under this packet's forbidden paths, so binding is
recorded here for provenance only. No acceptance is claimed; commits,
submits, gate dispatch, and every project-control transition remain
orchestrator-owned.
