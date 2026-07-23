# M4 footprint — bounded control-metadata reconciliation

**Scope:** exactly the three stale-metadata corrections the owner named for the R5 footprint
control-only PR (2026-07-23). This is a **bounded** reconciliation, not a full `/replan-project`
sweep. **No task JSON is created; no task status is changed; no CP is created.** The only ledger
file edited is `project-control/master_plan.json` (milestone summaries/status text). Task state,
gate records, and acceptance counts are untouched.

## What was stale, and the correction

| # | Stale | Corrected to | Evidence |
|---|---|---|---|
| 1 | **M4 summary said "0/5 … M4-T001..T005"** | **"0/6 … M4-T001..T006"** | M4-T006 (R5 height/setback) merged draft via PR #88, `awaiting_gate`; it was contracted but omitted from the count. `state.json.active_tasks` already lists M4-T006. |
| 2 | **M5 milestone `status: "planned"` with no summary** (reads as "not started"; contradicts `SESSION_HANDOFF.md` which already calls M5 active) | **`status: "active"` + honest summary** (1 contracted, 0 accepted; M5-T001 merged draft; FAR-cap only; every envelope constraint `missing`; `data_completeness` `missing_critical`; gated on M4 G6) | M5-T001 merged via PR #86, `awaiting_gate`; `state.json.active_tasks` lists M5-T001. |
| 3 | **The four proposed M4 footprint tasks were not represented anywhere in the plan** | **M4 summary now names M4-T007..T010 as PLANNED/PROPOSED, not yet contracted**, and states the scope impact (6 → 10 on contracting) | This PR's four DRAFT-PROPOSAL packets. |

`master_plan.json.updated_at` bumped to `2026-07-23T11:23:29Z`; `current_milestone_note` appended
with a one-line record of this reconciliation.

## Planned-count / dashboard impact (made explicit and honest)

Counts are derived by `tools/current_state.py` (and `project_control.py status`) **from the task
JSON files in `project-control/tasks/`** — `total_tasks` and per-milestone `total` count actual
contracted task files; the owner-dashboard (M0-T022) consumes the same control-plane substrate.

Consequently:

- **The four proposed tasks (M4-T007..T010) are deliberately NOT reflected in any numeric count**
  in this PR, because **no task JSON exists for them** — they are *proposed*, not *contracted*.
  Representing them as counted tasks would fabricate contracted work and violate historical honesty
  (owner-dashboard invariant: current work is read from lifecycle state, never inferred).
- **Today (unchanged by this PR):** M4 = **6 contracted / 0 accepted**; project accepted total = **42**.
- **Forward scope (explicit):** once the owner approves this PR and the tasks are contracted one at a
  time (T007 first), M4 contracted scope rises **6 → 10**; **accepted stays 0** until each clears its
  full gate set **including G6** qualified-human legal approval. The `legal_rule` type carries
  `required_gates = [G0,G1,G2,G3,G4,G5,G6]` (config.json), so none can be accepted on engineering
  gates alone.
- **No "blockers to beta" or acceptance metric moves** on this PR: it adds zero accepted work and zero
  contracted tasks; it only corrects descriptive metadata and stages proposals.

## What this reconciliation deliberately does NOT do

- Does not create `project-control/tasks/M4-T007..T010.json` (owner: do not create task JSON).
- Does not change any task's `status`, gate record, or acceptance.
- Does not create CP-0032 (reserved for M0-T019) or any checkpoint.
- Does not edit the historical `M5-T001-DRAFT-PROPOSAL.md` header ("NOT contracted, NOT started"),
  which is an accurate point-in-time record of that task's pre-contract proposal and is preserved as
  history; the **live** M5 representation (master_plan) is what was corrected.
- Does not touch product/dashboard code (`apps/web/**`) — the dashboard reflects reality by reading
  the corrected control plane, not by a code change (and `apps/web` is under the 3D/UI + PR-#64 holds).
