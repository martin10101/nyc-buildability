# M0-T086 — capability baseline + live-workstation reconciliation

Producer: orchestrator. Date: 2026-08-25. All findings below are LIVE-workstation facts measured
this session unless labelled otherwise; imported-snapshot conclusions are labelled historical
(D-024-R001: snapshot absence proves nothing).

## 1. Live workstation reconciliation (D-024 §1 / Phase A item 2)

- **Repository**: single origin `https://github.com/martin10101/nyc-buildability.git`.
- **This campaign's checkout**: `ctl24`, branch `control/D-024-fable-codex-loop`, synced with its
  upstream (pushed through the M0-T097 acceptance checkpoint). Single ledger lineage from D-023
  tip `7649acf`.
- **Worktrees**: ~70 registered (git worktree list). Active/meaningful: `ctl24` (this campaign);
  `ctl23` @ `7649acf` (D-023 campaign — read-only history for us; **D-023 remains active with
  M0-T080 in round-3 review** on `task/M0-T080-session-model-turnover` @ `31e6b87`, wt-m0t080);
  primary checkout `nyc-development-feasibility-claude-pack` on `control/session14-m0t055-accept`
  @ `94e243e`, **dirty with 3 paths** (backend-engineer agent memory edits + the owner's untracked
  directive file in `.claude/`) — NOT touched, per owner instruction. Remainder: historical task/
  control worktrees and ~50 `.claude/worktrees/agent-*` producer worktrees (historical, idle).
- **Local branches**: 156. Divergent-or-untracked set is small and explained:
  `control/D-023-autonomy-campaign` tracks origin/main `[ahead 41]` (in-flight campaign — by
  design, not lost work); `control/D-009-batch-close` and `control/source-027-r289-incident-
  recovery` `[ahead 1]` (historical closure branches); `task/M3-T001` `[ahead 8]`, `task/M4-T002`
  `[ahead 19]`, `task/M4-T007` `[ahead 7]` (pre-existing paused product work — untouched);
  several `[gone]` upstreams (remote branches deleted after merges); local-only wip/backup and
  ~100 historical `worktree-agent-*` branches. **No unexplained unpushed work found.**
- **Open PRs**: PR #241 exists and MUST STAY UNMERGED (owner hold; also excluded in the D-024
  manifest scope). No PR opened yet for `control/D-024-fable-codex-loop`.
- **MCP**: live session reports no MCP servers configured (Gate 0 evidence, D-024 audit_log).

## 2. Installed capabilities (measured + official docs)

Authoritative record: `tools/agent_supervisor/fixtures/capability_matrix_v1.json` (20 entries,
status/confidence vocabulary) + `capability_probe_live_2026-08-25.json` (deterministic live
probe; `python -m tools.agent_supervisor.capability_probe`). Headlines:

- `claude` **2.1.220**; dual install (`~/.local/bin/claude.EXE` wins PATH; npm shim second) —
  launch designs must pin the binary. Flags measured supported: `--strict-mcp-config`,
  `--mcp-config`, `--add-dir`, `--settings`, `--agent`, `--worktree`, `--print`,
  `--output-format`, `--resume`, `--continue`, `--name`.
- `codex` **0.146.0** (npm `.cmd` shim — bare-name CreateProcess spawns fail; execute the
  resolved path). Measured supported: `exec`, `--sandbox`, `--json`, `--output-schema`,
  `resume`, `--cd`, `--model`, `--profile` — the full §2 transport surface.
- Hooks (official docs, fetched 2026-08-25): 31 events on current docs incl. **`UserPromptExpansion`**
  (command-name matcher, blocks expansion pre-model) and **`UserPromptSubmit`** (exit 2 /
  `permissionDecision:"block"` blocks AND ERASES the prompt; reason shown to user); every
  version-gate note (≥2.1.191/195/196/205/214) is satisfied by 2.1.220.
- Status line (official docs): full primary payload schema incl. `context_window` (live-context
  semantics, input-only `used_percentage`, nullable rules) and **`subagentStatusLine`** per-task
  `id/name/type/status/description/label/startTime/model/effort/contextWindowSize/tokenCount/
  tokenSamples/cwd` (model + contextWindowSize ≥2.1.205, omitted pre-resolution).
- Agent SDK: **absent-by-policy** (not admitted; D-024 forbids installing it for this directive).
- Python: local 3.11.9, CI 3.12 — supervisor additions stay 3.11-compatible.
- Live-harness-dependent behaviors (prompt-erasure semantics, payload shapes as actually emitted)
  are recorded **unknown** in the probe fixture — documented in the matrix, proven in Phase B/F.

## 3. Compact baseline (D-024 §1 item 7)

- **Implemented + verified**: D-007 Codex bridge (phases 1–4, adversarial matrix); operator CLI
  (start/status/pause/resume/stop/emergency-stop/export-handoff/replay/doctor); Windows Job-Object
  containment; watchdog + autostart machinery (M0-T054/M0-T056); bounded-auto budgets + typed
  refusals + quota detect-and-hold (D-023 M0-T078/T079 accepted); directive-compliance registry;
  graph/context system; this task's capability fixtures.
- **Present but unproven for D-024**: session/model turnover extensions (M0-T080 — round-3 review
  in flight, reconcile before Phase D); notifications seed; resource sampling as telemetry base.
- **Missing (GAPs by phase)**: see `M0-T086-reuse-register.md` — telemetry ingestion + confidence
  labels (B); assignment/envelope split, classifier, health bands, extension gate (C); epoch
  leases + seam validation + outage backoff (D); guardrail-refusal bridge (E); ask + `/loop-*`
  zero-context channel + no-duration start alias (F); root-cause repair evidence (G); canary/
  golden-run harness (H).
- **Conflicts with D-024**: none found. The supervisor-freeze rule required amendment to recognize
  D-024-cited evidence — DONE this task (`.claude/rules/supervisor-freeze.md`, authorized by
  D-024 §1). The quota detect-and-hold policy remains authoritative and distinct from the §8
  guardrail bridge. Continuous activation remains owner-gated (§18); R595 prerequisite unchanged.
- **Safe to reuse now**: everything in the reuse register marked REUSE/EXTEND; the 860k-token
  manual-run observation stays a required runaway-test scenario (16.2), not evidence of loop
  failure.

## 4. Self-checks run this task

- `python -m pytest tools/test_agent_supervisor_capability_probe.py -q` → **16 passed**.
- `python -m ruff check` on both new files → clean.
- Full supervisor-suite baseline re-establishment (freeze §4 duty): run recorded in the G2
  self-check with its exact outcome.
- Probe determinism: two consecutive `build_record()` bodies byte-identical (also a test).
