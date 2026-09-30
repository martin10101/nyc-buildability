# Parallel Build Plan — lanes A–E (DERIVED)

| | |
|---|---|
| **Status** | **Derived by the integrator (Lane C) on 2026-09-30 — the owner may amend.** The owner's file `PARALLEL_BUILD_PLAN_LANES_2026-09-28.md` does not exist (owner, 2026-09-30). Per D-090-R005 this plan is derived from `docs/PRODUCT_PLAN_CURRENT_2026-09-28.md` (the plan) and the owner's lane prompts in `docs/lanes/LOOP_LAUNCH_PROMPTS.md`. Every rule below cites its source. |
| **Governs** | How the five lanes split the work, own files, branch, merge and hand off. Product scope, results and acceptance come from the plan only. Process authority is unchanged: the ledger (`tools/project_control.py`), gates G0–G7, and the ADR-005/ADR-006 tiers. |
| **Integration branch** | `candidate/D-024-mrl-option-b` (Prompt 0) |

---

## 1. The five lanes

| Lane | Name | Mission (lane prompt) | Owns (summary; `docs/lanes/OWNERSHIP.yaml` is exact) | Flag | API port | Web port |
|---|---|---|---|---|---|---|
| A | Engine | Correct numbers: rule tables, the three answers, add-ons, floor stack, §5b paths | `services/api/app/rules/**`, `app/_zr_snapshots/**`, `app/scenario/**`, their tests, `tools/residential_validation.py`, root `tests/fixtures/**`, `docs/research/zr-snapshots/**` | `LANE_A_ENABLED` | 8101 | 3101 |
| B | Data and site facts | Sourced facts: fixtures with provenance, measurement ranks, site geometry, §8a flags, parity data | `services/api/app/{connectors,profile,spatial,site_definition,resilience}/**`, their tests, `services/api/tests/fixtures/**`, `docs/research/**` (except `docs/research/zr-snapshots/**`, Lane A) | `LANE_B_ENABLED` | 8102 | 3102 |
| C | Contracts, study and integration | The backbone and traffic control: contracts, study store, invalidation, input channel, wiring, merge queue, every hot file | `packages/contracts/**`, `services/api/app/{main.py,config.py,api/**,contracts/**,_contract_schemas/**}`, web shared state + API clients, CI, manifests/lockfiles, e2e harness, `render.yaml`, `supabase/**`, `tools/**`, `project-control/**`, `.claude/**`, `docs/**` (including every `docs/lanes/queues/<X>.md`; excluding the docs paths of lanes A, B, D and E and each lane's own status and request files), `scripts/**` | `LANE_C_ENABLED` | 8103 | 3103 |
| D | Architect interface | The dashboard the architect uses (§3, §5a) | `apps/web/src/app/**` (except the root layout), `apps/web/src/components/**`, UI libraries in `apps/web/src/lib/**`, e2e specs, `apps/web/public/**`, `docs/design/**` | `LANE_D_ENABLED` | 8104 | 3104 |
| E | Outputs and parity | Everything that leaves the app, plus parity modules (§5c, §11b) | `services/api/app/{cad,drawings,documents}/**` and new output modules, their tests, `docs/samples/**` | `LANE_E_ENABLED` | 8105 | 3105 |

Each lane also owns exactly two kinds of file under `docs/lanes/`: its own `docs/lanes/status/<X>.md` and the requests it writes, `docs/lanes/requests/<X>-<n>.md`. The queues (`docs/lanes/queues/<X>.md`) are owned by Lane C (the integrator); a lane never edits its queue. A lane needing a file it does not own writes a request (§6) and moves on (lane prompts, shared rules).

## 2. How a lane task runs (reconciled with the repo's governance)

The lane prompts say "open the PR"; `CLAUDE.md` and ADR-005 say only the orchestrator runs git, `gh` and the ledger. Both hold as follows:

1. **Ledger first.** Every queue item becomes one ledger task `M<x>-T<n>` that cites D-090 and the plan task ID in its title (for example "M5-T130 [M1-14a] …"). The plan's IDs are workstream labels, like the pack IDs in `.claude/rules/expansion-agent-dispatch-hold.md` §3, and never ledger IDs.
2. **Branch:** `lane-<x>/<ledger-id>-<slug>` in that lane's worktree `../nyc-lane-<x>`, from the integration branch. The lane path checker reads the lane from this prefix.
3. **Producer** (the lane loop or the lane's producer agent) edits only its lane's paths, writes tests, runs its lane checks, commits in its worktree, and updates its status file. It does not push, merge, or run the ledger CLI.
4. **Integrator (Lane C = the orchestrator)** records G0/G2, pushes the branch, opens the PR, dispatches the independent reviewers for the task type's gates (producer ≠ verifier), records the gates, and merges in queue order. Merges are Tier A after required checks, or Tier B after the named specialist review (dependencies, CI, security-relevant changes).
5. **Merge queue:** one PR at a time: rebase, full CI (including the lane path check and web-e2e), merge. When several are ready: C → B → A → D → E (Lane C prompt).
6. **Hard stops never move:** Tier D, owner holds, PR #241, owner-typed commissioning, dependency security with no waiver, G6 for rules (D-090-R010, R012).

> **Owner decision pending: where the lane loops run.** (a) In the cloud as orchestrator-dispatched producers, one worktree per lane. This is the D-089/B-026 precedent and fits step 3–4 exactly. (b) As Codex loops on the owner's PC via the owner-typed D-088 commissioning (`tools/controller_update/commission_lanes.ps1`, Windows, 1 GiB disk floor). Under (b) the plan's "Codex loops" meets D-024-R003 (Codex reviews only), which needs the owner's word.

## 3. Waves

| Wave | Goal | Lanes | Exit |
|---|---|---|---|
| **0 — bootstrap** | Docs index, code map, reconciliation, this plan, ownership + path checker + lane flags, contracts v1 + benchmark fixtures, queues, estimate | C only | Owner GO (D-090-R007) |
| **1 — foundations** | Everything Milestone 1 needs that other work builds on, built against fixtures | all | Study store + input statuses live behind flags. Benchmark lot recorded. R6B draft rules for FAR (incl. the affordable option), heights, coverage, yards and units. Three-answer generator on fixtures. Drawing kit v0. Set-asides behind flags. Lot choice + status strip |
| **2 — Milestone 1 and Milestone 2** | Wiring, add-on switches, plan/section/3D, communication pass, compare, report + exports, validation suite, the journey (M1-20); then the Wallabout slice (M2-05..M2-08, M2-01..M2-03) | all | M1-20 journey green; C-1..C-12 pass on 215-16 Northern; architect session (M1-21) scheduled |
| **3 — breadth and parity** | R6–R10 family completion (plan §12a wave 2); §11b parity (unused floor area, data flags, neighbors, 485-x, comps, financials); L-2/L-3; L-11 groups | A, B, E (+C, D for surfaces) | Parity rows done with sources; never delays Milestone 1 (plan §11b) |

Lower-density (R1–R5), special districts and commercial districts follow the plan's §12a order after wave 3 and are queued then.

## 4. Order of first work (why this order)

- **The benchmark first.** Every check must pass on 215-16 Northern before results reach an architect (plan §9a-6). Its district is R6B, so Lane A's first rule family is R6B (FAR 23-22 with the qualifying option, heights 23-432, coverage 23-362, rear yard 23-344, units 23-52), as **draft** tables (D-090-R010). The Pilot A family follows once the owner answers Q1.
- **Contracts before surfaces.** Lanes D and E build against contract fixtures until Lane C wires live data (Lane D prompt; Lane E prompt).
- **Set aside before building on it.** Example defaults (M1-06a/b) and the coordinate drawing go behind flags early, so no new work lands on them.
- **The plan contradicts live code.** "Unused floor area" is computed from recorded building area, which the plan forbids (§3 step 4, M2-07). It goes behind a flag and shows "Not available — needs existing zoning floor area" (Lane A + D, wave 1).

## 5. Contracts v1 (the list the missing §5 would have held)

Additive only within a wave; breaking changes only at wave boundaries, announced in `status/C.md` (Lane C prompt). Each lands with valid + invalid fixtures under `packages/contracts/fixtures/{valid,invalid}/<stem>/` and passes `.github/scripts/validate_contracts.py`.

| Schema (`packages/contracts/schemas/v1/`) | Plan source | Holds |
|---|---|---|
| `site_fact.schema.json` | §4, §9, M1-07 | One site value with its measurement rank and label: survey (entered) / city records / approximate — tax map / entered / assumed / unknown; its source, dataset version and date; "blocks" when unknown |
| `study.schema.json` | §9, M1-09 | One study per property: selected lots + "lots you selected" statement; the shared site (site facts); options (add-on selections, goal, program, floor-to-floor heights, assumptions); selected option; revision |
| `results.schema.json` | §5, §5b, §5c-1, M1-14, M1-25 | For one option and revision: the three answers, each either a value with its rule sections or "not_available" with a reason. Also: shortfall reason, add-on gains vs the current selection, best-combination goal and exclusions, completeness line, floor-by-floor table, floor stack, §5b paths, status-strip items, and one geometry block in feet (lot outline, yards, setback lines per level, envelope, floor plates) that the drawings, PDF and DXF all read |
| `report_model.schema.json` | §3 step 7, §5a, §9, M1-19, M1-22 | What every export renders: identification line (option · revision · date), sheet list, standing notices (once), assumptions page, calculation table rows with ZR sections and sources |
| `export_record.schema.json` | §9 historical exports | An export's inputs, sources, rule versions and results; read-only; "start a new study from this" copies inputs only |
| `benchmark_lot.schema.json` | §9a-6, competitor review §A/§D | A benchmark or golden lot: expected values each with its source and verification state, and which checks C-1..C-12 apply |

## 6. Requests between lanes

`docs/lanes/requests/<X>-<n>.md`: who needs what, which file (owned by whom), why, and what is blocked. The requesting lane X writes and owns the request file. The lane that owns the requested file handles it the same day in a small PR (Lane C prompt); hot-file requests always go to Lane C. The request's **State** is updated by the requesting lane, or by the integrator (Lane C) on a non-lane branch (`task/`, `control/`); no other lane edits it (`OWNERSHIP.yaml`).

## 7. Guardrails

- **Lane path check** (`scripts/lanes/check_lane_paths.py`, CI step in `control-plane`): a PR from `lane-<x>/…` fails if it touches a file whose owner in `OWNERSHIP.yaml` is not lane x. There is no exception list: the map itself gives lane x its `docs/lanes/status/<X>.md` and `docs/lanes/requests/<X>-*.md`, and gives every queue to Lane C. Other branch prefixes (`task/`, `control/`) are not lane branches and pass. It also fails if any tracked file has no owner.
- **Lane flags:** `LANE_A_ENABLED` … `LANE_E_ENABLED` in `services/api/app/config.py`, absent means off (fail safe). New behavior goes behind the lane's flag (shared rules). Production never sets them until the owner releases a lane's work.
- **Ports:** API 8101–8105, web 3101–3105, written to each worktree's `.env.local` by `scripts/lanes/setup_worktrees.sh` (never pushes).
- **Live city data:** only Lane B, and not in Wave 0 (D-090-R009).
- **Pausing a lane:** it exceeds the owner's daily spending limit, or it breaks the path check twice in a row. The integrator pauses it and tells the owner (Prompt 0 step 10).

## 8. What stays with the owner

Q1 pilot lot and verifier · Q4 which property screen · Q5 scenario endpoint · Q7 sign-in timing · Q8 section view vs the hold · Q10 mockup review · Q12 reviewer licensing and hours · Q13 pricing · authorization of PRs #243–#246 · where the lanes run · the daily spending limit · GO. The integrator recommends; it never decides (D-090-R008).
