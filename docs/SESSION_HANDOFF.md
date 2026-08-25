# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA here as still-current.** This
file is orientation only. Rules/gates/workflow routes live in `CLAUDE.md`. Old blocks via
`git log -p docs/SESSION_HANDOFF.md`. Keep CURRENT-ONLY: the `context-budget` CI check fails > ~4000 tok.

## D-024 SESSION 1 — capture corrected to v4; 11-task campaign contracted; validator PASS; NEXT = claim M0-T086

Refreshed **2026-08-24 (Fable 5, ctl24 worktree)**. Branch **`control/D-024-fable-codex-loop`** from
D-023 tip **`7649acf`** (single ledger lineage). `ctl23` = read-only history; **D-023 stays active**
(M0-T080 round-3 review in flight on its own branch — do not disturb). The stale main worktree
(`nyc-development-feasibility-claude-pack`, branch session14) is NOT ours to touch. **NEVER merge
PR #241** or any pre-existing PR (owner hold). Directive: `project-control/directives/D-024-fable-codex-loop/`
(source-001.md is the verbatim owner directive v4 — it is the full context; owner re-prompting is not required).

### Bootstrap Gate 0 — MANDATORY for every successor session BEFORE any repository write
- Launch Claude Code with **primary cwd = `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`**. Reaching the
  repo via added working dirs / absolute paths / post-launch worktrees does NOT pass (D-024-R125).
- Prove the session MCP-clean: `/mcp` must report no servers (or exactly the approved allowlist);
  record the evidence (D-024-R126).
- On fail/unknown: NO repo writes of any kind; bounded read-only diagnosis + terminal-visible handoff;
  require a fresh correctly-launched session (D-024-R127). Adopt uncommitted work only after the fresh
  session independently passes the gate; never rewrite/discard it to get a clean status (D-024-R128).
- This session's pass: cwd `ctl24`, branch `control/D-024-fable-codex-loop` @ `7649acf`,
  `/mcp` = "No MCP servers configured", directive file verified sha256 `0611bb45…` (85,855 B).

### Done this session (capture correction)
- `source-001.md` replaced with the owner's **v4** (prior capture was a v3 snapshot `e8375769…` that
  predated the Bootstrap Gate 0 section). Rows R001/R099/R109/R122/R123 updated to v4 wording;
  **R125–R128 appended** (Gate 0) → **128 requirements**, all pending.
- Campaign re-sized from 8 one-per-phase tasks to **11 workload-first tasks M0-T086..M0-T096**
  (Phases A/B/C split; D–H single cohesive extension units; rationale in manifest `applicability_note`).
- `verification.json` skeleton regenerated (11 tasks; applicable sets verified == shared resolver).
- Manifest source digest, locked IDs (128), requirements digests, affected tasks/branches, index updated;
  append-only `audit_log` entry records the correction + this session's Gate-0 pass.
- `python tools/validate_directive_compliance.py --check` → **EXIT=0 twice** (full run takes ~4–5 min:
  c17 hashes the supervisor-tree identity per task — be patient, don't kill it). The previously reported
  permission-denied/path-handle failure did **not reproduce** across 3 full runs; the validator was NOT
  modified or bypassed; the real recorded defects were 8× c17 empty-identity (`allowed_paths: []`),
  fixed with real path scopes.
- `evaluate_task_refs` ok:True for all 11 tasks (`D-024:ALL`; missing_ids `[]`).

### Campaign map (deps)
`T086 A1` capability probes/fixtures (+ supervisor-freeze qualifying-evidence amendment) → `T087 A2`
bootstrap continuity (campaign survives session turnover mechanically) → `T088 B1` telemetry core →
`T089 B2` subagent telemetry; `T088` → `T090 C1` contracts/sizing; `{T089,T090}` → `T091 C2` runtime
supervision → `T092 D` controller/seams/exact-once succession → `{T093 E` 4.8 bridge, `T094 F` operator
channel, `T095 G` repair gate + GitHub`}` → `T096 H` canaries + independent reviews + **two-unit golden
run** + activation package (**continuous mode default-off**; owner activation checkpoint retained).

### NEXT bounded action
Claim **M0-T086** (`/start-controlled-task`, refs `D-024:ALL`), author its acceptance-scenario pack,
then produce: workstation reconciliation record, reuse register, installed `claude`/`codex` capability
probes as deterministic fixtures (supported/unsupported/nullable/unknown), and the supervisor-freeze
amendment recognizing cited D-024 requirement IDs. Producer mechanics: worktree isolation off the
control branch (reset producers to the control-branch SHA — they auto-isolate off origin/main which
lags); never `name:` a producer spawn (read-only guard); never resume a TaskStop-killed producer.
