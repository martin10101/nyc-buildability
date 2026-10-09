# M0-T151 Producer Report -- D-034 ARCHITECTURE.md + /pr-review skill

- Task: M0-T151 (governance) -- implement D-034-R001..R004.
- Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t151`,
  branch `task/M0-T151-architecture-context`, base `cfdc9af6`.
- Worktree guard: `git rev-parse --show-toplevel` ->
  `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t151` (PASS).
- Deliverables (all NEW files, in allowed_paths):
  - `ARCHITECTURE.md` (repo root) -- 211 lines, ASCII.
  - `.claude/skills/pr-review/SKILL.md` -- 97 lines, ASCII, YAML frontmatter.
  - `project-control/reports/M0-T151-producer-report.md` -- this file.

## What I surveyed (before writing a word)

Packet + directive: `project-control/tasks/M0-T151.json`,
`project-control/directives/D-034-architecture-context-and-review-skill/source-001.md`.

System (read, not assumed): `CLAUDE.md`,
`docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md`, `docs/adr/ADR-004-frontend-hosting-render.md`,
the path-scoped rules `.claude/rules/{backend-api,geospatial,legal-rules,frontend-web,
project-control,code-architecture,deployment,supervisor-freeze,expansion-agent-dispatch-hold}.md`,
and real source: `services/api/app/main.py`, `services/api/app/api/v1/rule_evaluation.py`,
`services/api/app/profile/builder.py`, `services/api/app/spatial/adapter.py`,
`services/api/app/spatial/live_provider.py`, `services/api/app/documents/gate.py`,
`services/api/app/scenario/contract.py`, `tools/agent_supervisor/README.md`.
Layout confirmed by directory listing (services/api/app subsystems, apps/web, tools,
project-control, docs/adr, .claude/rules).

## Architecture claims mapped to verifying file(s)

| ARCHITECTURE.md claim | Verified against |
|---|---|
| FastAPI factory + /api/v1 routes | `services/api/app/main.py` (`create_app`), `app/api/v1/{properties,rule_evaluation}.py` |
| Connectors: bbl/pluto/ztldb/mappluto/zoning-features | `services/api/app/connectors/*.py` (dir listing) |
| Spatial engine + live provider + adapter read-only | `spatial/{engine,adapter,live_provider,models,policy}.py`; adapter docstring "no connector edits" |
| Rule engine owns calculation | `rules/{evaluator,integration,response}.py`; `rule_evaluation.py` delegates to `evaluate_property` |
| Provenance re-verified in builder | `profile/builder.py` docstring (provenance_ref referential integrity) |
| Next.js on Render, not Vercel | `apps/web/next.config.ts`; `docs/adr/ADR-004-...md`; `render.yaml` |
| Frontend holds only publishable keys | `.claude/rules/frontend-web.md`; ADR-004 decision item 4 |
| Ledger source of truth; orchestrator-only writes | `project-control/` tree; `.claude/rules/project-control.md`; ADR-005 |
| Supervisor shadow/supervised/limited-auto-OFF, frozen | `tools/agent_supervisor/README.md`; `.claude/rules/supervisor-freeze.md`; `project-control/reports/M0-T039-supervisor-freeze.md` |
| Document gate: sniffed content not filename | `services/api/app/documents/gate.py` docstring/controls |
| Dependency age gate fail-closed | `services/api/scripts/dependency_age_gate.py`; `.claude/rules/deployment.md` |
| Modularity checker | `tools/modularity_check.py`; `.claude/rules/code-architecture.md` |
| PR #241 never-merge hold | `docs/SESSION_HANDOFF.md` lines 45/54/76; `project-control/directives/D-023-.../source-001.md` |
| Fail-safe = normal 200 result, not error | `api/v1/rule_evaluation.py` (unsupported/professional_review_required paths) |
| Live provider returns None on any failure | `spatial/live_provider.py` (`build_live_substrate`, `_fail_safe`) |

## Acceptance-scenario mapping

- **S1 (six questions)** -- `ARCHITECTURE.md` has exactly six numbered sections (WHAT
  EXISTS / WHO OWNS WHAT / WHAT MAY DEPEND ON WHAT / HOW DATA MOVES / WHAT MUST STAY
  TRUE / WHEN AN AGENT MUST STOP); each answers only hard-to-infer intent and cites
  `CLAUDE.md`/rules rather than duplicating them. Every named component resolves to a
  real path (table above).
- **S2 (forbidden paths + invariants)** -- section 3 documents the real forbidden edges
  (engine never imports connectors/AI; frontend never holds service key / never
  computes compliance; connectors never write the ledger; workers/reviewers never run
  git; supervisor frozen lane). section 5 states each invariant WITH its enforcing mechanism.
- **S3 (stop conditions)** -- section 6 gives the exact `STOP -> explain conflict -> show
  impact -> propose smallest change` protocol and names the boundary classes (legal
  interpretation, credentials/payment, production approval, PR #241, owner holds).
- **S4 (skill correctness)** -- `SKILL.md` frontmatter makes it invocable as
  `/pr-review [branch|<commit-or-range>|<path>]`, states ADVISORY ONLY; body resolves
  the target diff, reads ARCHITECTURE.md + path-scoped rules first, reviews the six
  dimensions (4 captured + provenance + fail-safe), demands only-actionable output
  with `path:line` + failure scenario, requires an explicit UNPROVEN list, and closes
  with the gates-decide-DONE disclaimer.
- **S5 (trial run)** -- below.

## S5 -- Trial run of the /pr-review instructions against commit f12e828c

Target resolved per SKILL step (a): `git show f12e828c` (a single commit).
Commit: "M2-T020: settings-gated live spatial provider (default OFF) wired into the
default runtime path". Changed files (from `--stat`):
`services/api/app/spatial/live_provider.py` (new, 247), `api/v1/rule_evaluation.py`
(+21/-8), `tests/spatial/test_live_provider.py` (new, 414),
`tests/api/test_rule_evaluation_api.py` (new, 241), and the M2-T020 producer report.

Orientation per step (b): read `ARCHITECTURE.md` section 3/section 5 (spatial boundary, fail-safe
invariant) and `.claude/rules/{backend-api,geospatial,code-architecture}.md` for the
touched `services/api/app/spatial/**` and `api/v1/**` paths.

Review across the six dimensions (step c):

1. Code quality -- `live_provider.py` is orchestration-only (fetch -> compose), no new
   engine, no duplicated calculation; injectable `LiveSpatialFetchers` seam;
   `_candidate_layer_queries` dedupes and preserves official ordering. No unnecessary
   complexity or bad abstraction found. 247 SLOC, under thresholds.
2. Test adequacy -- the two new test files cover the CHANGED behavior directly:
   flag-off returns None with zero connector calls, unknown token stays off, live path
   composes a real substrate, any connector failure -> absent, `no_record` assignment
   -> absent, partial district page -> absent, empty label flows to engine (not
   fabricated), lot-no-feature passes the engine review class through, candidate-query
   dedupe/order. Negative and boundary cases present. No weakened assertions observed.
3. Security -- new trust boundary is the env flag `LIVE_SPATIAL_PROVIDER_ENABLED`,
   closed true-token set, default disabled; the route still accepts only the `bbl`
   path param (no request-body profile injection); `_fail_safe` logs typed error class
   + correlation id only, never `str(exc)`. No secret/leak path introduced.
4. Backward/contract compatibility -- flag-off behavior is byte-identical to the
   pre-M2-T020 default (`_default_spatial_substrate` returned `None`; now delegates to
   a provider that returns `None` when the flag is off, with zero connector calls). No
   contract/schema change; the route still returns the same versioned
   `rule_evaluation` document. No accepted record touched.
5. Provenance discipline -- no guessed source/unit/effective date; candidate districts
   derive from the OFFICIAL ZTLDB assignment, and the engine (not this module) decides
   geometric coverage, cross-checked against that assignment. No confidence->coverage
   mapping added.
6. Fail-safe correctness -- every failure branch returns `None` (absent substrate ->
   downstream `professional_review_required`), never a fabricated substrate, never a
   500; empty-district composition is explicitly refused to avoid laundering a missing
   input into a "no district covers this lot" claim; uncertainty classes returned
   unmodified.

Output (step d) -- actionable problems found: **none.** The diff conforms to the
spatial boundary and the fail-safe invariant; tests cover the changed behavior with
negative/boundary cases; no security or contract regression is visible in the diff.

UNPROVEN (explicitly unverified in this trial):
- I did not EXECUTE the test suites in this session; adequacy is judged from the test
  source in the diff, not from a green run. (The commit message records "suites 43+32
  passed" but that is the producer's claim, not my execution.)
- Real-network connector behavior (actual MapPLUTO / ZTLDB / zoning-features
  responses) is UNPROVEN -- the tests use doubles; the live flag is off everywhere by
  default, so no live path was exercised.
- Files outside the reviewed diff (e.g. `spatial/engine.py`, `adapter.py`
  `compose_from_connectors` internals) were read for orientation but not re-reviewed
  here; their correctness is out of this diff's scope and UNPROVEN by this run.

Authority disclaimer (per SKILL): this trial is ADVISORY ONLY and satisfies no gate;
M2-T020's DONE status rests on its own recorded gates/evidence, not on this review.

## Assumptions, limitations, deviations

- No deviation from the brief. All three deliverables written; only allowed_paths
  touched; no state-changing git run (guard check only, read-only).
- ARCHITECTURE.md is 211 lines (brief target 150-250) -- within range.
- I did not run `tools/project_control.py`, git write commands, `gh`, or push -- per
  ADR-005 the orchestrator owns those.

## Requested status

awaiting_gate -- ready for independent review (G0/G2/G3/G5; reviewers
code-reviewer, security-reviewer, directive-compliance-verifier).
