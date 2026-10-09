# Commissioning Step-2 start REFUSED pre-dispatch: `task_authority` ledger corroboration failed — one consolidated assessment (D-024-R394)

Recorded by the orchestrator 2026-08-31 (session `session_01SfXcRw7emzdojCDJmKxNTM`).
The owner personally typed both section-4 commands (R409 honored). Step 1
(`clear-recovery`) succeeded: transition seq 23 `owner_cleared_pause`,
PAUSED_RECOVERY -> PREFLIGHT — the R374-era preservation ENDED by owner decision. Step 2
(the seven-fact limited-auto start, typed exactly as presented) was **REFUSED
PRE-DISPATCH**: classification `UNSAFE_OR_DRIFTED`, failed probe `['task_authority']`,
exit 11, **NOT DISPATCHED, no provider contacted**. Per R394: no retry, no restart, no
journal edit; this is the one consolidated assessment for a new owner decision.

## 1. Exactly what happened (primary evidence)

- CLI stderr: `revalidation failed for ['task_authority']`; every other probe passed.
- Journal (read-only sqlite): `current_state` **remains `PREFLIGHT`** — the refusal wrote
  only `last_recovery_outcome` (classification UNSAFE_OR_DRIFTED, resume_permitted
  false); **no new transition** (still 23), no pending effects, no surviving children.
- **Not a counted stop**: the owner-touch ledger is unchanged (still the two 2026-08-30
  S14 stops); nothing was dispatched, 0 provider calls (cycle-2 exit-13 precedent).
- The cross-task driver never ran: **no `task_queue/queued_digest/*` and no
  `task_advancement/*` keys exist** — the queue was never even snapshotted. The
  commissioning journey remains entirely unconsumed.
- The owner ran the command via the session's `!` (Git Bash) rather than PowerShell.
  **This made no difference**: the command parsed, the config/manifest/model-selection
  loaded (their probes passed), and the same refusal would occur from any shell.

## 2. Root cause (proven, read-only)

`start_gate.live_revalidation` (start_gate.py:172-178) passes `repo_root = args.repo` to
`probe_task_authority` (probe_control_plane.py:32), which corroborates the task packet
against the ledger record at `<args.repo>/project-control/tasks/M0-T107.json` and fails
closed if that record is missing or disagrees. The presented Step-2 command says
`--repo C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack` —
a checkout parked on `control/session14-m0t055-accept` (`94e243e`, reflog shows HEAD
unmoved since 2026-08-11), which **predates M0-T107 entirely: its
`project-control/tasks/M0-T107.json` does not exist** -> `ledger_record_missing`
(an UNKNOWN, which fails closed) -> UNSAFE_OR_DRIFTED.

**Why this was invisible until the live keystroke:**

1. The R408 duty is mechanical validation against the **CLI contract** (`build_parser`
   + pinned flags + `dispatch_inputs_missing`) — it cannot see probe semantics, and the
   probe gauntlet only runs on a real `start`, which R409 rightly forbade the
   orchestrator from ever executing.
2. The last DISPATCHED journeys (2026-08-30) used `--repo` = the primary checkout
   `ctl24`, whose ledger record for M0-T107 exists and says `claimed` — so
   `task_authority` passed then. That shape was the M0-T125 survey's **defect D2**
   ("evidence/Codex bind to the primary checkout"), and the accepted M0-T126 fix
   (`evaluate_repo_binding`) now refuses it. The presented command therefore moved
   `--repo` to the pack path — which cures D2 but breaks the ledger corroboration.
   No live start has run since the D2 fix landed; this keystroke was the first
   execution of the new shape.

**Structural finding:** for an isolated-worktree task, one `--repo` value feeds two
validators that want different things — `probe_task_authority` wants the **control-plane
ledger root**, while `evaluate_repo_binding` (D2, correct) forbids the primary control
checkout and wants the **worker's tree**. The only shape satisfying both is a
**non-primary checkout whose `project-control/` mirrors the live ledger** — i.e. the
task's own worktree brought current. `wt-m0t107` as preserved (`796e18f`) carries a
stale ledger copy (M0-T107 `backlog`) and would fail `ledger_status_mismatch`.

## 3. Verified outcome of every candidate `--repo` (static, read-only, live code)

| `--repo` | `evaluate_repo_binding` | `probe_task_authority` | Verdict |
|---|---|---|---|
| pack checkout (presented) | allowed | FAIL `ledger_record_missing` | what happened |
| `ctl24` (primary) | **REFUSED** `repo_primary_checkout` (D2) | would pass | refused later in `_run_loop` |
| `wt-m0t107` as-is (`796e18f`) | allowed (repo == worktree) | FAIL `ledger_status_mismatch` (`backlog` vs `claimed`) | refused |
| `wt-m0t107` **fast-forwarded to `1c06957`** | allowed (repo == worktree) | **PASS** (verified: "claimed in both, no open blocker") | **the clean shape** |

Supporting facts, all verified this session: `796e18f` IS an ancestor of `1c06957`
(pure fast-forward; the worktree is clean, so no content is at risk); no OPEN blocker
names M0-T107 or M0-T109; `enforce_launch_bindings(wt-m0t107, wt-m0t107, wt-m0t107,
ctl24)` -> ALLOWED; `probe_task_authority` against the tip-content ledger -> PASS
(byte-identical to what wt-m0t107 will contain after the fast-forward).

## 4. The new owner decision (nothing held was touched; nothing retried)

**OPTION A (recommended — no supervisor code change, no R247 re-trigger):**
1. The owner authorizes a **narrow, one-time lift of the R413 hold on `wt-m0t107`**
   solely to fast-forward its checked-out branch `task/M0-T107-plugin-portability`
   from `796e18f` to the control tip `1c06957` (`git -C ... merge --ff-only`; the
   worktree is clean; this moves only that branch ref, never the control branch; the
   task's deliverable files do not exist yet, so no producer content moves).
2. The orchestrator performs the fast-forward, re-runs the full section-2 preflight,
   and re-presents the Step-2 command **corrected in exactly one value**:
   `--repo C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107` (everything else verbatim).
3. The owner re-types Step 2. (Step 1 does NOT need re-typing: the journal already
   rests at PREFLIGHT; the refused start consumed nothing.)

**OPTION B (structural, larger):** a bounded AD-093 defect task making the
`task_authority` ledger read use the control-plane root (`--checkout`) instead of
`args.repo` — arguably the honest fix (the probe's own docstring says it reads "the
control plane's record", and `--checkout` IS the control plane), but it is a
supervisor change: R247 recertification re-triggers. Can follow later as a
defect-lane candidate regardless of Option A.

Already done under existing Tier A authority (not part of the decision):
`wt-m0t109` (the successor worktree this session created — not under R413)
fast-forwarded `6d2e816` -> `1c06957` so its ledger copy carries the claimed M0-T109
state; the queue entry re-verified **ELIGIBLE** afterward; queue file and packet
digest unchanged.

## 5. Preservation statement

`wt-m0t107` untouched, clean at `796e18f`. PR #241 untouched (OPEN). Journal: the only
state change is the owner's own Step-1 clear-recovery (seq 23); the refusal added no
transition, no touch, no effect. No section-4 command was ever executed by the
orchestrator; both keystrokes were the owner's (R409/R414). No supervisor file changed
(certification `de18f27` / tree `b3921009...` stands; no R247 re-trigger).
