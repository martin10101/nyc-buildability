# Owner Mission-Control Dashboard (M0-T022)

A **read-only** observability layer over the existing project-control system. It lets the
owner understand the whole project state in ~10 seconds — engineering vs launch-readiness
progress, current/next/blocked work, CI health, which product systems are complete/partial/
not-started, what changed, and what each technical task means in plain product language —
without reading GitHub, task JSON, gate reports, or CI logs.

It **observes**; it never mutates. It runs no `project_control.py` write command, holds no
secret, and performs no GitHub write. If data cannot be verified it says so — it never shows
a fabricated number.

## Where to see it

- **Route:** `/dashboard` in the existing Next.js app (`apps/web`). No new service.
- **Internal only:** gated behind the non-public runtime flag
  `INTERNAL_OWNER_DASHBOARD_ENABLED`. Unset (default) → the route returns **404** with no hint
  it exists. The app has no auth yet, so it must never be exposed publicly.

## Run it locally

```bash
# from the repo root, with the flag enabled (thin-client note: web deps/build run
# wherever you develop the web app — never installed on the owner's 7 GB PC).
cd apps/web
INTERNAL_OWNER_DASHBOARD_ENABLED=1 npm run dev
# open http://localhost:3000/dashboard
```

The page reads `project-control/*.json` from the repository working tree at request time
(`export const dynamic = 'force-dynamic'`), so it always reflects the current ledger. It also
fetches supplemental live status from the **public** GitHub repo (no token needed).

## Architecture

```
project-control/*.json ──► loader.server.ts (fs, read-only) ─┐
project-control/product-map.json ───────────────────────────┤
                                                             ├─► assemble.ts (PURE) ─► DashboardModel ─► /dashboard UI
GitHub REST (public, no token) ─► githubClient.ts (cached) ──┘
```

- **Pure engine** — `apps/web/src/lib/dashboard/` has no React/Next/fs/network in its core
  (`types, parse, membership, model, progress, health, currentWork, activity, launch, github,
  assemble`). It is unit-tested in isolation (`__tests__/engine.test.ts`).
- **Edges** — `loader.server.ts` (reads files) and `githubClient.ts` (fetches GitHub) are the
  only IO; they are injected into the pure `assembleDashboard(raw, github, nowIso)`.
- **UI** — `apps/web/src/components/dashboard/` (Mission Control, Product Map, Current Work,
  Roadmap, What Changed, System drawer). Light theme reusing the product's design tokens; zero
  new npm dependencies; the Product Map is a hand-built SVG dependency graph.

## Source of truth (what each value comes from)

| Dashboard value | Source (read-only) |
|---|---|
| Task status / progress / counts | `project-control/tasks/*.json` (authoritative) |
| Milestones + dependencies | `project-control/master_plan.json` |
| Per-task gate state | `project-control/gates/*.json` (`required_gates ∩ result:PASS`, independent role) |
| Acceptance eligibility | join of gates + dependency status + open blockers (reproduces `accept()`) |
| Open blockers | `project-control/blockers/*.json` (`status:open`) |
| Activity feed | dated control-plane events (accepted / gate / merge / blocker / checkpoint) |
| System map, weights, owner text | `project-control/product-map.json` (the one new metadata file) |
| CI / open PRs / main SHA / freshness | public GitHub REST (supplemental only) |

**GitHub never corrupts canonical state.** Project-state numbers are computed from files only.
GitHub supplies live CI/PR/head/freshness; if it is unavailable the numbers are unchanged and
the live panel shows "stale" or "unavailable".

## Progress algorithms (deterministic, auditable — no AI guessing)

Both numbers = `Σ over systems (weight × fraction)`, weights from `product-map.json`
(`eng_weight` and `launch_weight` each sum to 100). Every displayed % exposes a
"How is this calculated?" breakdown of the contributing systems, tasks, and weights.

**Engineering completion** (how much is *built*):
```
eng_fraction(system) = clamp( Σ task.progress_percent / (100 × max(contracted, planned)), 0, 1 )
Engineering % = Σ eng_weight(system) × eng_fraction(system)
```
Credits built-but-unaccepted code (e.g. merged drafts); planned-but-uncontracted scope counts
as incomplete (not "100% of zero").

**Launch readiness** (what an architect can *safely rely on*):
```
launch_fraction(system) = clamp( accepted_count / max(contracted, planned), 0, 1 )
                          then reduced by any readiness cap still in force
Launch % = Σ launch_weight(system) × launch_fraction(system)
```
Only **accepted** capability counts, and readiness caps hold a system down until a gate passes
(e.g. the rules engine is capped until the **G6** qualified-human legal approval). This is why
launch readiness is deliberately lower than, and divergent from, engineering completion.

Whole numbers only in the main UI (owner directive #1); extra precision is in the breakdown.
If any contributing input is unverifiable, that system is **UNKNOWN** (never treated as 0), the
headline shows "Partial"/"Unavailable", and the breakdown names what could not be verified.

## Health vs completion

Health is **separate** from completion. A system is not "healthy" just because tasks are
accepted. Failed CI, stale GitHub, a blocked dependency, or a control-plane inconsistency
degrade **health** without rewriting historical completion. A state.json-vs-task-file
contradiction is flagged as an inconsistency (degrades health), never silently trusted.

## "Biggest things preventing an architect beta"

Derived deterministically from launch-critical systems below full readiness + unmet gates +
open blockers, ranked by missing launch weight. It is not an AI-generated opinion.

## Stale-data behavior

- Ledger unreadable → "Progress unavailable — project state could not be verified" (no number).
- GitHub fetch fails → last-known data is shown **marked STALE**, or "live data unavailable";
  it is never presented as live, and it never changes the file-derived numbers.
- Every live panel shows a "last synced" timestamp.

## Deploying on Render (later, owner-authorized)

The dashboard rides the existing `nycdf-web` service — **no new Render service**. To deploy:
1. Add `INTERNAL_OWNER_DASHBOARD_ENABLED` to `nycdf-web` env in `render.yaml` (`sync: false`),
   set to `1` only where the internal dashboard should be reachable.
2. Because the deployed slug's working directory is `apps/web`, if the runtime cannot see the
   sibling `project-control/` directory, add a build-time step that snapshots
   `project-control/*.json` into `apps/web` before `next build`. (V1 targets local-first +
   Render-ready; the loader walks up to find `project-control/` and fails safe to "unavailable"
   if it is absent.)
Deploys follow the normal ADR-003/004 flow (autoDeploy off; SHA-pinned; human approval).

## Environment variables

| Var | Where | Purpose |
|---|---|---|
| `INTERNAL_OWNER_DASHBOARD_ENABLED` | server only, non-public | `1/true/yes/on` enables `/dashboard`; anything else (incl. unset) = 404 |

No GitHub token is required (public repo, unauthenticated reads, 60 req/hr, cached ~45 s). If a
token is ever added for higher throughput, it is **server-only**, least-privilege
(read `Contents`/`Metadata`/`Actions`), and never inlined into the browser bundle.

## product-map.json (schema + how to extend)

`project-control/product-map.json` maps every ledger task to exactly one product **system** and
assigns the two weight sets. Schema: `project-control/product-map.schema.json`. Integrity is
enforced by `tools/validate_product_map.py` (stdlib) and the `product-map` CI job, which fail if
any task maps to zero or multiple systems, if either weight set does not sum to 100, or if any
reference does not resolve.

To add a **system**: add an entry to `systems[]` (id, name, owner purpose/why, `eng_weight`,
`launch_weight`, `planned_count`, `milestones`/`tasks_include`/`tasks_exclude`, `depends_on`,
`critical_for_beta`, `journey_steps`, optional `readiness_cap`); rebalance so each weight set
still sums to 100. To add a **task**: it maps automatically via its milestone; add an entry to
`task_overrides` for an owner-friendly title/description. Run
`python tools/validate_product_map.py` (and its tests) before committing.

## What V1 does NOT do

No historical progress deltas (no snapshot store yet), no auth (internal flag only), no live AI
summaries (all owner text is static metadata), no writes of any kind, and no Render provisioning
(local-first + Render-ready). See the task packet `project-control/tasks/M0-T022.json` for the
full acceptance scenarios and gate map.
