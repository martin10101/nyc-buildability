---
description: Creates or claims a tightly scoped tracked task with acceptance scenarios and gate requirements. Use before any implementation or research work.
---

1. Read project state and dependencies.
2. Confirm the task is `ready` and has no unresolved blockers.
3. **A task packet CANNOT be claimed unless it explicitly names all of the following.** If any is missing, complete the packet first — do not claim:
   - **Exact requirement identifiers** — the document(s) and section/numbered-item IDs the task implements (e.g. `PRD.md §13.3`, `GENERATIVE_DEVELOPMENT_STRATEGY_REQUIREMENTS.md §7`, `docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md`).
   - **Exact directive references** — every active owner directive/amendment/hold that constrains the task, as `directive_refs` (directive ID + requirement IDs, e.g. `D-001:ALL`) captured via `/directive-compliance`. An in-regime task cannot be claimed without them, and a task touching governance/control-plane paths must cite a covering governance directive (`tools/project_control.py` enforces this fail-closed).
   - **Exact source/evidence files required** — the specific fixtures, contracts, prior reports, or datasets the work reads (by path). No "read the repo" packets.
   - **Exact `allowed_paths` and `forbidden_paths`** — a non-overlapping write scope; a concurrent task may not share production code, schema, workflow, lockfile, ledger, checkpoint, task-packet, or handoff paths.
   - **Acceptance scenarios** — the executable examples per `docs/ACCEPTANCE_SCENARIO_STANDARD.md` (primary, boundary, missing/ambiguous, failure, and any domain pack).
   - **Required gates** — the G0–G7 set the task's risk demands, with reviewer roles that differ from the producer.
4. Confirm exclusive file scope and worktree/branch.
5. Claim through `python tools/project_control.py claim ...` (orchestrator only; ADR-005).
6. Update progress to 10%, then 20% only after scenarios are recorded.
7. Give each downstream agent only the packet's named requirement sections and evidence files — never the whole repo. Do not perform untracked work.
