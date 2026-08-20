# D-021 bootstrap evidence (session-governance rows R002–R004, R012–R018, R024)

Producer of this evidence: **orchestrator** (main session, 2026-08-20). Independent verification is
performed by the directive-compliance-verifier (never the producer). This file records primary,
reproducible facts — not narrative claims.

## R003 — reconcile first (live repository, GitHub, ledger, directives, accepted tasks, open PRs, CI)

All checks ran BEFORE any file was created or modified, from the session working directory:

- `git rev-parse --show-toplevel` → `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064` (== session cwd; a
  linked worktree root of the repo, listed in `git worktree list`).
- Branch `main` at `d8b3899f61efa6620e18a26541ced96020f5bef9`; `git status --porcelain` empty (clean);
  after `git fetch origin`: `git rev-parse main origin/main` → both `d8b3899…` (zero divergence either
  direction).
- Ledger (`python tools/project_control.py status`): current milestone M4 (M0/M2 active, M1 complete);
  task_counts accepted=100, blocked=2 (M0-T007/T008 — Supabase credentials), awaiting_gate=9
  (M0-T021, M0-T034, M4-T001..T006, M5-T001), backlog=10 at reconciliation time.
- Directive registry: 20 active directives D-001..D-020 in `project-control/directives/index.json`;
  `python tools/validate_directive_compliance.py --check` → exit 0 before capture; exit 0 again after
  the D-021 capture.
- Open PRs (`gh pr list --state open`): exactly one — PR #64 (task/M0-T019-frontend-security, the
  long-parked frontend-security PR; untouched by this work).
- CI on main head d8b3899: 20/20 check runs `success` (code-graph, model-routing, api-lock-verify,
  context-index-a1, context-pipeline, control-plane, exact-production-install, supervisor-bridge,
  contracts-typegen, product-map, web-e2e, contracts-schema-bundle, contracts, web, modularity,
  api-tooling-lock-verify, api, web-dependency-security, credential scan, context-budget).
- Divergences found: none material. `docs/SESSION_HANDOFF.md` is stale (session-18 era, accepted=84);
  per its own header and CLAUDE.md, the ledger wins — treated as orientation only, not repaired.

## R004 — fresh process, worktree root, empty MCP roster

- This session is a fresh Claude Code process: this owner instruction is the first user message of the
  session; no prior conversation state.
- Working directory `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064` equals `git rev-parse
  --show-toplevel` → started at a repository worktree root.
- Active MCP roster: EMPTY. The session tool roster contains only built-in Claude Code tools; no tool
  with the `mcp__` prefix exists. A ToolSearch sweep for "mcp" over the deferred-tool registry returned
  only the built-in WebFetch (keyword match), no MCP server tools. Consistent with accepted D-020
  (program-wide MCP default-deny, M0-T077, merged in PR #240 = main head d8b3899). No stop condition
  triggered.

## R001 (context) — activation deferral honored

`NYC_BUILDABILITY_AUTONOMY_ACTIVATION_HANDOFF_2026-08-19.md` activation work was NOT continued: no
controller-update bundle run, no limited-auto, no edits under tools/agent_supervisor/**, protected
controller/model-selection configuration, context pipeline, or MCP policy (R005–R008 are verified as
task rows at the reviewed identity; this section records the session-side observance). Nothing was
canceled or dismantled either — deferral only.

## R012 — sources actually read before selection

`docs/IMPLEMENTATION_SEQUENCE.md` (full), `project-control/master_plan.json` (milestone summaries),
PRD.md (§7.2/§9/§12/§13 via the M5-T001 packet requirement_refs; pilot framing), every non-accepted
task file title/status (M0-T007/T008/T021/T025/T026/T032/T034/T037, M2-T019, M3-T002..T005,
M4-T001..T006, M5-T001, M6-T001), M5-T001's full packet + M5-T001-future-hardening.md, and the live
implementation code: services/api/app/scenario/* (builder/contract signatures), app/api/v1/
rule_evaluation.py + properties.py, app/rules/rulesets/ (7 R5 rule families), apps/web/src/app/property,
components/{property,rule-evaluation}, lib/rule-evaluation.ts, apps/web/e2e/* (rule-evaluation specs +
recorded-fixture harness), packages/contracts (scenario schema + generated/scenario.ts + fixtures).

## R013–R016, R024 — selection: exactly one clear dependency-ready product unit

**Selected: M5-T002 — internal flag-gated `GET /api/v1/properties/{bbl}/scenario` + flag-gated
property-screen scenario surface.** A future user (dev/internal today, same surface later) can look up
a real R5 lot and **view a calculated draft zoning-floor-area-cap scenario** with provenance, coverage
boundaries, and honest failure states — the smallest end-to-end step that makes the merged-but-invisible
M5-T001 scenario foundation actually visible (advances "calculate" + "view").

- **Already-planned (R014):** the accepted M5-T001 gate record set anticipates exactly this slice —
  M5-T001's packet froze "services/api/app/api/v1/** and any new public endpoint" OUT as
  "service-layer only this slice", and M5-T001-future-hardening.md addresses FH-M5T001-S1/S2 "at the
  future M5 rule-evaluation→scenario endpoint" boundary. This task is that planned next slice, with
  those two hardening items closed at the boundary they were assigned to.
- **Not documentation/discovery/refactor (R016):** new endpoint + new UI surface + tests; zero refactors
  of existing modules (all consumed READ-ONLY).
- **Pilot fit + architecture preserved (R013):** consumes the R5 draft rule families verbatim; the
  endpoint/scenario/contract path is district-agnostic (unsupported districts yield honest typed
  unsupported outcomes), preserving five-borough architecture and staged rule expansion.

**Alternatives examined and why they are NOT a materially different ready choice (R024):**

1. **R5 yards / lot-coverage / additional envelope rule families** — explicitly NOT dependency-ready:
   the PR #91 proposal is recorded SUPERSEDED in master_plan.json, re-proposal owed only after accepted
   M3-T004 + canonical zoning-lot model (both backlog).
2. **M2-T019 (survey-review HTTP routes + production ReviewStore)** — its seams are B-001-blocked
   (durable storage / Supabase token, open blocker; owner-only credential).
3. **M3-T002/T003/T004/T005 (legal corpus chain)** — acceptance blocked by open B-001 (and B-011 for
   T005); corpus infrastructure, not a user-visible product step.
4. **M0 backlog (T025/T026/T032/T037)** — control-plane/governance work, excluded by D-021 itself.
5. **M6-T001** — pre-public-launch traffic protection; deployment-adjacent, excluded scope.
6. **M4-T007/M4-T008** — already accepted (not next units).
7. **Finishing M4-T001..T006 / M5-T001 acceptance** — parked on genuine G6 qualified-human legal
   approval (owner-side hard stop), not an engineering unit; not weakened by this task.

No second dependency-ready product unit of comparable standing exists → the single-unit branch of the
directive applies (R017–R023 executed; R024's multiple-unit branch not triggered).

## R017/R018 — capture + decomposition

D-021 resolved as the next identifier from the live registry (D-001..D-020 present, D-021 absent);
source captured verbatim to `project-control/directives/D-021-resume-product-r5-pilot-next-unit/
source-001.md`, sha256 `9320b9b1a3398ad04ef40c38ce476f9f6e852b28ad99b0498442b377017a4682` recorded in
manifest; 25 atomic requirements with forward (p1–p11 → R001–R025) and reverse (every row carries
source_ref) trace; applicability: sentinel D-021-BOOTSTRAP for session rows, M5-T002 for task rows,
holds bound to both. `DirectiveRegistry().load().evaluate_task_refs(M5-T002)` → ok:True; validator
exit 0.

## R002/R025 — scope observance (session side)

Exactly one product task (M5-T002), one branch (task/M5-T002-scenario-endpoint), one PR (#241, opened
with an explicit DO-NOT-MERGE banner). No controller activation, no R060 promotion, no broad
infrastructure work, no deployment, no merge performed or scheduled.
