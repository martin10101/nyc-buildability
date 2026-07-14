# M0-T001 — Repository and Control-System Audit

- **Task:** M0-T001 "Repository and control-system audit" (milestone M0)
- **Auditor (producer):** progress-auditor
- **Date:** 2026-07-14 (UTC)
- **Scope:** Reconcile every claim in `project-control/` against repository evidence (git log, git status, git remote, files on disk). Read-only audit; no fixes applied.

## 1. Evidence base (commands executed)

| Command | Key output |
|---|---|
| `git remote -v` | `origin https://github.com/martin10101/nyc-buildability.git` (fetch/push) |
| `git log --oneline` | Exactly one commit: `8ba7278 Bootstrap: planning and control package for NYC Buildability` |
| `git show --stat --format=fuller 8ba7278` | AuthorDate/CommitDate `2026-07-14 17:08:24 -0400` = **21:08:24 UTC** |
| `git ls-tree -r --name-only 8ba7278` | 58 files, incl. all M0-T000 ledger records, `state.json`, `master_plan.json`, CP-0001/0002 |
| `git status --porcelain` / `git status -sb` | **10 untracked files** (list in Finding D3); zero modified tracked files |
| `git rev-parse main origin/main` | Both `8ba7278...` — local main == remembered remote ref |
| `git ls-remote origin refs/heads/main` | `8ba7278... refs/heads/main` — remote head **verified live** |
| `python tools/project_control.py status` | 1 accepted (M0-T000), 3 claimed (M0-T001/2/3) |
| File reads | All 22 files under `project-control/`, `tools/project_control.py`, `tools/enrich_bootstrap_tasks.py` |

## 2. Claim-by-claim reconciliation (S1)

### 2.1 M0-T000 "accepted" — VERIFIED (with caveat D1)
- `project-control/tasks/M0-T000.json`: `status=accepted`, `progress_percent=100`, `accepted_by=orchestrator`, `accepted_at=2026-07-14T21:07:31Z`.
- Producer submission record exists: `project-control/reports/M0-T000.json` (submitted 21:06:51Z, `requested_status=awaiting_gate`) referencing `project-control/reports/M0-T000-producer-report.json` (exists).
- Both declared required gates have PASS records (see 2.3). Producer (`progress-auditor`) ≠ reviewers (`orchestrator`, `qa-engineer`) — separation-of-duties honored.
- All of the above are committed in `8ba7278` and pushed to origin. **Caveat:** accepted without G1 despite config requiring G1 for `research` tasks — see D1.

### 2.2 Checkpoints CP-0001 / CP-0002 — VERIFIED
- `project-control/checkpoints/CP-0001.json` (21:06:51Z) and `CP-0002.json` (21:07:31Z) exist and are committed.
- Both record `commit: "none-pre-git"`. This is **accurate**: the first and only git commit `8ba7278` was created at 21:08:24 UTC, *after* both checkpoints.
- CP-0002's defect claim ("BOM-intolerant JSON load ... utf-8 -> utf-8-sig") is **verified in code**: `tools/project_control.py` line 11 uses `encoding="utf-8-sig"`, and the commit message of `8ba7278` records the same fix.

### 2.3 Gate records M0-T000-G0 / M0-T000-G3 — VERIFIED (with caveat D5)
- `project-control/gates/M0-T000-G0.json`: PASS, reviewer `orchestrator`, evidence `project-control/reports/M0-T000-G0-evidence.json` (exists).
- `project-control/gates/M0-T000-G3.json`: PASS, reviewer `qa-engineer`, evidence `project-control/reports/M0-T000-G3-pass-evidence.json` (exists).
- The intentional G3 FAIL (rejection-path test) left `project-control/reports/M0-T000-G3-fail-evidence.json` on disk, but the FAIL gate record itself was **overwritten** by the later PASS (single file per task+gate) — see D5.

### 2.4 state.json — PARTIALLY VERIFIED (D2)
- `last_checkpoint=CP-0002` matches newest checkpoint on disk. `current_milestone=M0` matches `master_plan.json`. `project_status=active` plausible.
- **Not verified / misleading:** `accepted_tasks=[]` and `active_tasks=[]` contradict task-file reality (1 accepted, 3 claimed). `updated_at=21:07:31Z` is stale relative to ledger activity at 21:10–21:12Z. See D2.

### 2.5 master_plan.json — VERIFIED
- M0 `active`, M1–M7 `planned` with a coherent dependency chain. No tasks exist for milestones other than M0, consistent with plan state. Committed and pushed.

### 2.6 Post-commit ledger records (M0-T001/T002/T003) — EXIST BUT UNCOMMITTED (D3)
- Task packets, G0 readiness gates (all PASS by `orchestrator`), and readiness reports for M0-T001/T002/T003 exist on disk and are internally consistent (each gate references an existing report; each packet has S1–S3 scenarios; statuses/percent match `claimed`/10 per config markers).
- Claims recorded: M0-T001 → progress-auditor (21:11:56Z, this audit), M0-T002 → official-source-researcher (21:12:09Z), M0-T003 → cloud-architect (21:12:24Z).
- None of these 9 files is in git; no checkpoint covers them. See D3.
- Expected outputs for T002 (`docs/research/M0-T002-geoclient-address-resolution.md`) and T003 (`project-control/reports/M0-T003-bootstrap-review.md`) do **not** exist yet — consistent with `claimed` at 10% (no premature completion claims; no orphan outputs).

## 3. Discrepancies (S2/S3 — numbered, with evidence paths)

**D1 — Under-gated acceptance vs config (S2: unsupported progress).**
`project-control/config.json` requires `research` tasks to pass `[G0, G1, G3]`. Yet `project-control/tasks/M0-T000.json`, `M0-T001.json`, and `M0-T003.json` (all `task_type=research`) declare `required_gates=[G0, G3]` — G1 (official-source verification) omitted, with no recorded waiver. M0-T000 was **accepted with no G1 gate record** (no `project-control/gates/M0-T000-G1.json` exists). Code cause: `accept()` in `tools/project_control.py` (lines 88–95) validates only the packet's own `required_gates`, never the config; `new_task()` allows `--gates` to override config defaults silently. M0-T002 correctly declares `[G0, G1, G3]`. G1 is arguably N/A for control-plane lifecycle tasks, but the deviation is undocumented.

**D2 — state.json aggregate fields are dead/stale (S3: ledger vs repo mismatch).**
`project-control/state.json` shows `accepted_tasks=[]`, `active_tasks=[]`, `blocked_tasks=[]`, `failed_gates=[]` while task files show M0-T000 accepted and M0-T001/2/3 claimed, and a G3 FAIL occurred during T000. Code cause: only `checkpoint()` writes `state.json` (`tools/project_control.py` lines 97–101); `claim/progress/submit/gate/accept` never update it. `updated_at=2026-07-14T21:07:31Z` predates task creation (21:10:20Z) and all three claims (21:11–21:12Z). Any consumer trusting these arrays gets a false picture; `tasks/*.json` is the only reliable source.

**D3 — 10 untracked files: post-commit ledger not committed, not checkpointed (S3).**
`git status` shows untracked: `project-control/tasks/M0-T001.json`, `M0-T002.json`, `M0-T003.json`; `project-control/gates/M0-T001-G0.json`, `M0-T002-G0.json`, `M0-T003-G0.json`; `project-control/reports/M0-T001-G0-readiness.json`, `M0-T002-G0-readiness.json`, `M0-T003-G0-readiness.json`; `tools/enrich_bootstrap_tasks.py`. All created ≥21:10:19Z, after commit `8ba7278` (21:08:24Z) and after the last checkpoint CP-0002 (21:07:31Z). The remote (`origin/main`) therefore has **no record** that tasks T001–T003 exist. A session loss would orphan the entire current work wave.

**D4 — Out-of-band ledger mutation by orphan script (S3).**
`tools/enrich_bootstrap_tasks.py` (untracked, not an output of any task packet) directly rewrote `project-control/tasks/M0-T001/2/3.json` (scope, scenarios, reviewers) bypassing the CLI. Those same packets list `project-control/tasks/**` under `forbidden_paths`. The mutation is real (packets contain the enrichment fields, e.g. `producer_hint`, scenarios) but is recorded nowhere — no CLI log entry, no checkpoint, no commit. Presumably orchestrator-authored, but there is no evidence trail proving that.

**D5 — Gate FAIL history overwritten (S2/S3).**
`gate()` writes one file per (task, gate): `project-control/gates/M0-T000-G3.json` now shows only the final PASS. The earlier FAIL survives only as the orphan evidence file `project-control/reports/M0-T000-G3-fail-evidence.json` plus prose in CP-0001/CP-0002 summaries; `state.json.failed_gates` is empty. Rejection-path history is not independently reconstructible from gate records.

**D6 — Evidence is assertion-grade, not transcript-grade (S2).**
All gate/producer evidence files are one-line JSON assertions. Example: `project-control/reports/M0-T000-producer-report.json` claims "init/status/new-task/claim/progress commands executed **with recorded outputs**" — but no recorded command outputs exist anywhere in the repository. G3's "lifecycle reproduced from clean state" (`M0-T000-G3-pass-evidence.json`) likewise has no captured transcript. The lifecycle conclusion is corroborated by file timestamps and code behavior, but the evidence files themselves would not survive an adversarial review.

**D7 — Progress-log gaps (minor).**
`project-control/tasks/M0-T000.json` `progress_log` holds only two 75% entries; the 85 (submitted) / 95 (gates passed) / 100 (accepted) transitions defined in `config.json.progress_markers` are applied to `progress_percent` but never logged (only the `progress` subcommand appends to the log). Expected given code, but reduces auditability.

**D8 — Checkpoint `commit` field unvalidated (minor).**
`checkpoint()` accepts free text (`"none-pre-git"`). Correct here, but nothing prevents a future checkpoint from recording a wrong or nonexistent commit hash.

## 4. What checked out clean

1. Remote is real and current for all committed work: `git ls-remote origin` returns `8ba7278` = local `main`. No unpushed commits, no tracked-file modifications, no ignored-file surprises (`git status --ignored` empty).
2. Checkpoints' `none-pre-git` commit references are truthful (both predate the first commit).
3. CP-0002's defect-fix claim is verifiably in code and in the commit message.
4. No premature completion claims: T002/T003 outputs absent and their packets honestly say `claimed`/10%.
5. Separation of duties held for M0-T000 (producer ≠ gate reviewers ≠ blocked self-acceptance; `accept` is orchestrator-gated in code, line 90).
6. `project-control/blockers/` exists and is empty — consistent with zero declared blockers.
7. `master_plan.json`, `config.json`, and milestone/task alignment are internally consistent.

## 5. Recommended corrections (for orchestrator; not applied — read-only audit)

1. **Commit and push** the 9 untracked ledger files (and decide whether `tools/enrich_bootstrap_tasks.py` should be committed or deleted), then cut a checkpoint (CP-0003) recording the T001–T003 wave. (D3)
2. Either make the CLI maintain `state.json` arrays on claim/accept/gate, or delete those fields so no consumer trusts them. (D2)
3. Reconcile `required_gates` with config for research tasks, or record an explicit G1 waiver for control-plane tasks in the task packets/checkpoint. (D1)
4. Make `gate()` append (e.g., timestamped gate files) instead of overwriting, to preserve FAIL history. (D5)
5. Require gate/producer evidence to include captured command output or file diffs, per `docs/GATES_AND_CHECKPOINTS.md` intent. (D6)
6. Prohibit direct edits to `project-control/tasks/**` outside the CLI, or add a CLI `edit-task` subcommand so mutations are logged. (D4)

## 6. Acceptance-scenario self-check

- **S1 (normal):** every ledger claim (M0-T000 accepted, CP-0001/2, gates M0-T000-G0/G3, state.json, master_plan.json) matched to concrete file/git evidence or flagged — sections 2 and 3.
- **S2 (missing-data):** missing G1 gate for accepted research task flagged as unsupported progress (D1); assertion-only evidence flagged (D6).
- **S3 (conflict):** explicit discrepancy list with file paths — D1–D8.

*Audit performed read-only. Only file written: this report.*
