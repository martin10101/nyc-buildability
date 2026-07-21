# Session Handoff — NYC Buildability (updated 2026-07-21)

Open `nyc-development-feasibility-claude-pack` as the workspace root, then run the CLAUDE.md
start-of-session routine (`python tools/project_control.py status`). The `project-control/`
ledger + git + CI are the source of truth; this file is orientation only.

## Current state (read first)
- **main = origin/main = `6f9d603`.** Ledger: **40 accepted / 2 blocked / 1 claimed / 1 in_progress / 5 backlog.** Checkpoint **CP-0031** (CP-0032 is RESERVED for M0-T019 — do not create a checkpoint).
- **Milestone M0** active. M1 (source registry + connectors) accepted. M2 (property intelligence) mostly accepted; profile integration in progress.
- Repo PUBLIC; `protect-main` ruleset active; secret-scan + push-protection ON.

## Active work — M2-T012 (in_progress, lead-only)
- **M2-T012 Profile integration (single contract 1.4.0 update).** Claimed by orchestrator (lead session); branch `task/M2-T012-profile`; worktree `.claude/worktrees/M2-T012-profile` (based on `6f9d603`); 10% (G0 PASS + claimed).
- **Scope (additive-only):** one coordinated **contract 1.4.0** update via the accepted M2-T010 tooling — integrate zoning-features (M2-T007) + MapPLUTO geometry (M2-T009) + the accepted **M2-T013** spatial-intersection records into the canonical profile with full provenance and **uncertainty preserved (never collapsed)**; add the geometric assignment as the 4th cross-check evidence stream; fold in the enumerated carried LOW-defect fixes. 1.0.0–1.3.0 payloads must still validate. **STOP** on any non-additive schema need, any uncertainty-collapse, any 1.5.0 temptation, or credentials.
- **File scope:** `services/api/app/profile/**`, `packages/contracts/**` (1.4.0 via M2-T010 tooling), `_contract_schemas/**` (sync tooling only), `apps/web/src/lib/**` (derived declarations), tests; connector/resilience touches ONLY for the enumerated carried defects (each disclosed). Reviewers G0–G5: data-contract-verifier, code-reviewer, security-reviewer.
- **Read only:** the M2-T012 packet, the M2-T013 output (`services/api/app/spatial/`), the profile modules (`builder.py`/`contract.py`/`property_profile.schema.json`), the M2-T010 tooling, and the enumerated carried-defect sources. Do NOT broadly reread the repo or historical reports.

## Just delivered — M2-T013 (accepted, merged PR #71)
Production **spatial-intersection engine** (`services/api/app/spatial/`): determines which zoning
districts/overlays/special districts cover which parts of a tax lot, with an explicit
positional-uncertainty model (documented vs assumed ±20 ft; 40 ft linear-sum compound band),
a 5-class taxonomy, split-share ranges, per-family coverage audit, ZTLDB cross-check, and
professional-review triggers. Emits facts-with-uncertainty only — never labels "Verified", never
collapses uncertainty. Consumes MapPLUTO/zoning-features/ZTLDB domain models read-only. Gates
G1/G3/G4 + a bounded final-head delta review all PASS; full API suite 567 passed. It is the
geometric substrate M2-T012 (profile) and M4-T001 (rules) consume.

## FROZEN — M0-T019 / PR #64 (do NOT touch without separate owner authorization)
- **PR #64 (M0-T019 frontend dependency-security upgrade + permanent npm dependency-admission policy) is OPEN and FROZEN at SHA `39080822a361b6204813d2dcbd1f849b196100ea`.** Status `claimed`; worktree `.claude/worktrees/M0-T019-frontend`. It is blocked only by its own dependency-age gate (a lockfile package must reach 7 complete days old).
- **Scheduled action:** at or after **2026-07-22T06:10:00Z**, rerun ONLY the required *failed* CI jobs at that same SHA. Do NOT commit, regenerate the lockfile, weaken the age policy, or rerun the 3 already-passing reviewers. If CI goes green, run ONLY `ci-evidence-verifier` with a small evidence packet. PR #64 stays open/unmerged/unaccepted until the owner separately authorizes the merge.
- Do NOT merge/accept M0-T019, change its frozen SHA, advance CP-0032, or modify M0-T020.

## Next eligible product work (after M2-T012)
- **M4-T001** (rules-engine foundation + first R5 FAR family) — its M2-T013 dependency is now
  satisfied, BUT M4-T001 and the survey workstream (**M2-T014/T015/T016**) remain under the owner
  **"2026-07-20 planning-report review" dispatch hold**. Do NOT dispatch them without the owner
  releasing that hold. **M6-T001** is explicitly not-this-wave.
- If, after M2-T012, no product task is unambiguously eligible, report the exact blocking hold
  concisely — do NOT release a hold to find work.

## Operating rules (owner directives — persist)
- **Lead implements a single eligible task directly** (no producer subagent when there is no
  concurrent second task — a lone producer only duplicates context/tokens).
- **Reviewers:** only those the task's actual risk requires; dispatch **once, at a frozen SHA**;
  give each a **small exact packet** (task criteria + frozen SHA/diff + relevant modules + exact
  tests/reports); target **≤50k tokens per reviewer**; never ask a reviewer to read the whole repo
  or all reports; never repeat a review when the SHA is unchanged. Four-role review only when
  genuinely required by the task's control rules or risk.
- **Do NOT create broad agent-config / orchestration / process PRs during product work.** Any
  control-system codification is a separate bounded PR that must not interrupt active product work.
- **CI does not need continuous watching** — start it, do other independent work, inspect the
  result afterward (background `gh pr checks <n> --watch`, then merge on green).
- **Acceptance-with-sequencing-exception pattern** (used for M2-T013): when the owner authorizes
  accepting a task whose only unmet dependency is a superseded *sequencing* gate, remove that
  dependency from the task's `dependencies` (documented in the task record), then `accept`. The
  `accept` CLI does NOT create a checkpoint, so CP-0032 stays reserved.

## HARD RULES (unchanged)
- **Protected-main, PR-only.** Never push to main. Task/control branch → push → `gh pr create` →
  required checks green → `gh pr merge --merge` → `git fetch` + reconcile. `--match-head-commit`
  needs the FULL 40-char SHA (a short SHA errors "Could not coerce value to GitObjectID").
- **ADR-005:** only the orchestrator runs `tools/project_control.py` / git / gh. Producers edit
  files + return a report (thin client; no git/npm). Reviewers are read-only, return report content
  the orchestrator saves VERBATIM + records the gate. `project_control` lifecycle: G0 backlog→ready;
  claim needs `ready`; submit→awaiting_gate; G2 `--reviewer orchestrator`; independent gates
  (G1/G3/G4/G5/G6) need a rostered reviewer ≠ producer; accepted tasks immutable; gate `--report`
  path must exist when the CLI runs.
- **Thin client / low storage:** keep ≥4 GB free; no local node_modules/DB/citywide datasets; the
  web lockfile regenerates on a runner via `generate-lockfile.yml`. The Python API test env
  (shapely 2.0.7 / GEOS 3.11.4 / pytest) IS available locally for backend self-checks; CI (pytest
  9.0.3 from the hash-pinned tooling lock) is authoritative.
- **Shell/runtime:** Bash + PowerShell share a persisted cwd — prefer absolute paths and don't leave
  cwd drifted. On Windows git warns LF→CRLF on commit (harmless). Background tasks (subagents, CI
  watch) notify and re-invoke this session on completion — you may dispatch one and continue.

## Blockers (owner action required)
- **B-001** (Supabase access token — HIGHEST; blocks M0-T007/T008 + persistence + citywide imports),
  **B-002** (Render API key), **B-004** (Geoclient subscription key). B-003, B-005..B-009 resolved.

## Owner decisions pending
1. M0-T019 / PR #64 merge authorization (after the 2026-07-22T06:10Z CI + dependency-age gate resolves).
2. Release the "2026-07-20 planning-report review" dispatch hold on M4-T001 + the survey workstream (M2-T014/T015/T016).
3. Credentials: B-001 (highest), B-002, B-004.
4. GDS/expansion planning review (counter-notice §2 hold) and 3D holds — preserved.

Written by the orchestrator.
