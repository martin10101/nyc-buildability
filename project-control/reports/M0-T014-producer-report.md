# M0-T014 Producer Report — project-control CLI hardening (owner code-audit P0)

- **Task ID:** M0-T014
- **Producer:** backend-engineer
- **Date:** 2026-07-17
- **Requested status:** `awaiting_gate`
- **Report path:** `project-control/reports/M0-T014-producer-report.md`

## 1. Status summary

All seven packet scenarios (S1–S7) implemented and proven by an executable
suite. Full suite green locally on Windows (Python 3.11.9), twice, exit code 0.
One real defect was found by the new concurrency test during self-check and
fixed (section 7, D1). Stdlib-only maintained; nothing installed.

## 2. Files changed

| File | Change |
|---|---|
| `tools/project_control.py` | Rewritten/hardened (same CLI surface + one new optional flag). 687 diff lines. |
| `tools/test_project_control.py` | Extended from the 15-check suite to 9 test groups covering S1–S7 + docs honesty. 860 diff lines. |
| `project-control/reports/M0-T014-producer-report.md` | This report. |

No other paths touched. `git status --short` in the worktree:
```
 M tools/project_control.py
 M tools/test_project_control.py
```

## 3. Contracts / schema changed (additive only)

1. **Gate records** written by the hardened tool now carry a `role` field:
   `self_check` (G2), `administrative` (G0/G7), or `independent_review`
   (G1/G3/G4/G5/G6). History entries preserve `role`. Records without `role`
   are treated as pre-hardening history and are never retro-rejected.
2. **Task records:** `progress_log` entries now also record the resulting
   `status` (previously only percent/message).
3. **Report/gate `report_file` values** are stored as normalized POSIX
   relative paths (`project-control/reports/<name>`); stored legacy values
   (backslashes, `docs\research\...`) are untouched and tolerated on read.
4. **New optional CLI flag:** `new-task --reviewers a,b` populates
   `reviewer_agents` (needed because independent gates now validate against
   the roster).

## 4. Design decisions implemented (per owner constraints)

1. **Gate classes (no bypass path).** G2 = self-check class: recorded only by
   `--reviewer orchestrator`, stored honestly as `role: self_check`, and can
   never satisfy an independent gate at accept time. G1/G3/G4/G5/G6 =
   independent class: reviewer must be in the task's `reviewer_agents` AND
   differ from `producer_agent`. G0/G7 = administrative class (derived from
   ledger evidence: all 21 accepted tasks' G0 records have reviewer
   `orchestrator`): recorded only by the orchestrator, rejected if the
   producer is literally named `orchestrator`. Every gate id G0–G7 has exactly
   one class; there is no flag or default branch that skips validation
   (asserted by test: no `--force/--skip/--override/--no-check` on `gate`).
2. **Progress transition enum** (docs/GATES_AND_CHECKPOINTS.md lifecycle):
   - forward chain: `backlog→ready`, `claimed→in_progress`,
     `in_progress→self_check`
   - failure/recovery: `awaiting_gate→rework`, `rework→in_progress`
   - block: any non-terminal state `→blocked`; cancel: any non-terminal
     `→canceled`
   - unblock: `blocked→{backlog, ready, in_progress, awaiting_gate}` (the
     ledger has real pre-claim blocked tasks M0-T007/M0-T008 with
     `producer_agent: null`, so pre-claim block/unblock paths are required)
   - `claimed` is set only by `claim` (from `ready`/`rework` only — claim
     from `backlog` is no longer allowed; G0 or an explicit
     `backlog→ready` progress must come first)
   - `awaiting_gate` is entered only via `submit`/`gate` (submit allowed from
     `claimed/in_progress/self_check/rework`), except the `blocked→awaiting_gate`
     unblock return path
   - `accepted` is NEVER settable by progress (argparse choices exclude it +
     in-code defense); percent restricted to 0–99; `accepted`/`canceled` are
     terminal — claim/progress/submit/gate all refuse to touch terminal tasks
     (this also closes a pre-existing demotion hole where `submit`/`gate`
     could knock an accepted task back to `awaiting_gate`/`rework`).
3. **Accept preconditions (all enforced, all failures listed at once):**
   status == `awaiting_gate`; every required gate has a PASS record (for
   independent gates: record must not carry `role: self_check` or any other
   non-independent role, and its reviewer must differ from the producer;
   role-less legacy records are tolerated); every dependency accepted
   (`dependencies: null` legacy shape tolerated — ledger has M0-T013/M1-T001
   stored as null); zero open blockers referencing the task.
4. **Blocker scan rule:** blocking iff `status == "open"` (case-insensitive)
   or status missing/empty (fail-closed). Ledger statuses `resolved`,
   `resolved_temporary` (B-002), `closed` (B-003) do not block — matching
   observed ledger semantics. Reference = word-bounded regex match of the
   task id in `affects` entries or `detail`
   (`(?<![A-Za-z0-9])<id>(?!\d)`); a base id also matches its rework
   mentions (`M0-T005` matches `M0-T005-R1`) — deliberately conservative,
   can only block, never allow. Unreadable blocker JSON = fail-closed reason.
5. **Containment.** Task id pattern `^M\d+-T\d{3}(-R\d+)?$` — derived from
   the ledger: 30/30 task files match (M0-T000…M2-T004 + rework id
   M0-T005-R1); verified by scan (section 6, C0). Applied on every
   subcommand taking `--task-id` and on `--depends` ids; `task_path()`
   refuses to build a path from an unvalidated id. Report paths must be
   relative, both `/` and `\` treated as separators, no `.`/`..` components,
   no drive (`C:\`, drive-relative `C:x`), no UNC (`\\srv\...`), no POSIX
   absolute; must normalize into `project-control/reports/` (bare filename =
   inside reports/); resolved-path containment double-check via
   `is_relative_to`. Gate ids restricted to G0–G7 via argparse choices
   (the old free-form `--gate-id` could address arbitrary files). Checkpoint
   ids restricted to `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$` (existing ids
   CP-0001…CP-0017 conform; the old code allowed traversal via cp id).
6. **Atomic writes.** `save()` serializes first, writes a unique
   `tempfile.mkstemp` file in the destination directory, then `os.replace`
   (atomic on POSIX and Windows); bounded retry on Windows sharing
   violations; temp file unlinked on any failure. `load()` retries transient
   Windows `PermissionError` reads during a concurrent replace (defect D1).
   Concurrency model is last-writer-wins (no merge/lock) — documented.
7. **Honest documentation.** Module docstring section "IDENTITY IS
   PROCEDURAL, NOT CRYPTOGRAPHIC" + argparse epilog + per-argument help state
   that `--agent`/`--reviewer` are caller-provided labels and enforcement is
   procedural (ADR-005) plus these validations. Asserted by test.
8. **Backward compatibility.** Validation on write only. Proven by test
   S7: the full real ledger copied to a temp project — 115 JSON files parse,
   `status` exits 0 with the 21 accepted tasks visible, a message-only
   `progress` against a copied real task succeeds (also exercising
   `sync_state` across every real task file), and a legacy-shaped task
   (role-less G0/G2-by-orchestrator + G3 by an unrostered legacy reviewer +
   `reviewer_agents: []` + `dependencies: null`) still accepts.

## 5. Acceptance scenarios created (executable)

All in `tools/test_project_control.py`; each maps to a packet scenario:

| Packet | Test group | Coverage highlights |
|---|---|---|
| S1 | `test_s1_transitions` | 15 legal transitions pass; 25 prohibited pairs rejected with status proven unchanged; `--status accepted` and unknown statuses rejected; percent −1/100 rejected, 99 passes; message-only update; terminal immutability; claim allowed only from ready/rework (9 statuses swept); submit allowed only from claimed/in_progress/self_check/rework (10 statuses swept); needs_split→rework, blocked submit |
| S2 | `test_s2_accept_preconditions` | accept rejected on (a) wrong status even with all gates PASS, (b) missing gates, (c) unaccepted/missing-file dependency, (d) open blocker via `affects` and via `detail`; passes when all four hold; `resolved`/`resolved_temporary` do not block; missing blocker status fail-closed; null dependencies tolerated; word-boundary non-matches proven |
| S3 | `test_s3_gate_classes` | per-gate loop over G1/G3/G4/G5/G6: unrostered reviewer rejected, producer rejected, rostered reviewer passes with stored `role: independent_review`; rostered-producer packet mistake still rejected; empty roster rejected; G2 by non-orchestrator/producer rejected, by orchestrator stored `role: self_check`; G7/G0 administrative; forged `self_check` (and `administrative`) record can never satisfy G3 at accept; no bypass flags in help |
| S4 | `test_s4_containment` | 12 malformed task ids × 6 subcommands rejected, task dir byte-identical; malformed `--depends` rejected; 11 bad report paths rejected on submit and gate; 3 valid report forms accepted and stored normalized; bad gate ids rejected; bad checkpoint ids rejected, valid one lands in checkpoints/ |
| S5 | `test_s5_atomicity` | 8 concurrent subprocess progress invocations all rc 0, file valid, no `*.tmp` leftovers; interrupted-write simulation (patched `_replace_with_retry` raising) leaves previous bytes intact and cleans temp; non-serializable payload never touches the file |
| S6 | `test_s6_spoofing` | producer accepting own task, producer gating own task, renamed unrostered `--reviewer`, percent 100, `--status accepted`, and terminal-task demotion via submit/gate/claim — all rejected with state proven unchanged |
| S7 | `test_s7_backward_compatibility` + `test_original_workflow` | real-ledger copy parse + status + write probe; legacy-record acceptance; the original 15 checks preserved (inputs updated to valid ids/rostered reviewers/relative paths — semantics identical, marked check-by-check in comments) |
| docs | `test_docs_honesty` | `--help` contains the caller-provided/cryptographic disclaimer; module docstring contains "NOT CRYPTOGRAPHIC" |

## 6. Commands run and exact results (G2 self-check evidence)

Environment: owner PC, Git Bash `$?` exit codes, Python 3.11.9
(`python --version` → `Python 3.11.9`). CI equivalent: `python3
tools/test_project_control.py` on ubuntu-latest (unchanged invocation, line
143 of `.github/workflows/ci.yml`).

**C0 — validation-rule derivation scan (read-only, real ledger):**
```
$ python - <<scan over project-control/>
TASK IDS: 30 all match ^M\d+-T\d{3}(-R\d+)?$: True
REVIEWERS BY GATE: {'G0': ['orchestrator'], 'G1': ['data-contract-verifier'],
 'G2': ['orchestrator'], 'G3': ['code-reviewer', 'human-journey-reviewer',
 'orchestrator', 'qa-engineer', 'security-reviewer'],
 'G4': ['orchestrator', 'qa-engineer'], 'G5': ['security-reviewer']}
ROLE FIELDS SEEN: {None}
BLOCKER STATUSES: ['closed', 'open', 'resolved', 'resolved_temporary']
TASKS WITH dependencies=None: ['M0-T013', 'M1-T001']
ACCEPTED COUNT: 21
```

**C1 — first full suite run (found defect D1):**
```
$ python tools/test_project_control.py; echo "EXIT=$?"
OK: original 15-check workflow preserved
OK: S1 transition enum (legal chain passes; every prohibited jump rejected)
OK: S2 accept preconditions (status, gates, dependencies, blockers)
OK: S3 gate classes (independent/self_check/administrative; no bypass)
OK: S4 containment (task ids, report paths, gate ids, checkpoint ids)
AssertionError: concurrent progress failed: ...
PermissionError: [Errno 13] Permission denied: '...\\project-control\\state.json'
EXIT=1
```
Expected: all green. Actual: S5 exposed a REAL Windows race — a reader
(`load`) hit a transient sharing violation while another process
`os.replace`d `state.json`. Fixed by bounded read retries (D1).

**C2 — full suite after fix (authoritative self-check run):**
```
$ python tools/test_project_control.py; echo "EXIT=$?"
OK: original 15-check workflow preserved
OK: S1 transition enum (legal chain passes; every prohibited jump rejected)
OK: S2 accept preconditions (status, gates, dependencies, blockers)
OK: S3 gate classes (independent/self_check/administrative; no bypass)
OK: S4 containment (task ids, report paths, gate ids, checkpoint ids)
OK: S5 atomic writes (concurrent invocations, interrupted write, serialization failure)
OK: S6 spoofing attempts all rejected
OK: S7 backward compatibility (115 real ledger files parse; legacy records accepted; validation is write-time only)
OK: docs honesty (--agent disclaimed in --help and module docstring)
OK: all 9 project-control test groups passed
EXIT=0
```

**C3 — byte-compile + stability re-run:**
```
$ python -m py_compile tools/project_control.py tools/test_project_control.py && echo "COMPILE OK"
COMPILE OK
$ python tools/test_project_control.py > /tmp/run2.log 2>&1; echo "RUN2 EXIT=$?"
RUN2 EXIT=0
```

**C4 — concrete rejection-message demo (throwaway temp project, never the
real ledger); expected = reject with rc 2 unless noted:**
```
$ progress --percent 95 --status accepted --message spoof
  rc=2 err="argument --status: invalid choice: 'accepted' (choose from 'backlog',
  'ready', 'claimed', 'in_progress', 'self_check', 'awaiting_gate', 'rework',
  'blocked', 'canceled')"

$ gate --gate-id G2 --reviewer orchestrator --result PASS --report ev.json
  rc=0  stored record:
  { "task_id": "M9-T900", "gate_id": "G2", "reviewer": "orchestrator",
    "role": "self_check", "result": "PASS",
    "report_file": "project-control/reports/ev.json", ... }

$ gate --gate-id G3 --reviewer backend-engineer-independent --result PASS ...
  rc=2 err="Reviewer 'backend-engineer-independent' is not in this task's
  reviewer_agents ['code-reviewer', 'security-reviewer']; independent gate G3 rejected."

$ gate --gate-id G3 --reviewer backend-engineer --result PASS ...   (producer)
  rc=2 err="Producer cannot independently gate own task."

$ submit --report ../../../etc/passwd --requested-status awaiting_gate
  rc=2 err="Report path may not contain '.' or '..' components: '../../../etc/passwd'"

$ accept --task-id M9-T900 --agent orchestrator   (awaiting_gate, G0/G2/G3 all
  PASS, deps [], one open blocker referencing the task)
  rc=2 err="Cannot accept M9-T900:\n- open blocker B-900 references this task"
```
All actual results matched expectations.

## 7. Defects found and fixed during self-check

- **D1 (real, found by the new S5 threaded test on Windows):** concurrent
  invocations could crash a reader with `PermissionError` while another
  process `os.replace`d the same JSON file (Windows sharing violation).
  Fix: `load()` now retries transient `PermissionError` (bounded,
  20 × 0.05 s), symmetric with the existing replace-side retry. Re-run
  green twice (C2, C3). This defect existed in the old tool too (unretried
  reads); it simply had no concurrency test to expose it.

## 8. Assumptions and defaults (disclosed for the reviewer)

1. **G0/G7 "administrative" class** is my structural interpretation for the
   two gates the owner's constraint left unclassified; it matches 100% of
   ledger history (every G0 recorded by `orchestrator`). If the orchestrator
   wants G7 treated as independent instead, it is a one-line set change plus
   tests.
2. **Accept-time independence check** = record is not self_check/other
   non-independent role AND reviewer != producer. Roster membership is
   enforced at WRITE time only — enforcing it at accept time would
   retro-reject history (ledger G3/G4 records exist by `orchestrator` and
   `qa-engineer` for tasks whose rosters differ).
3. **Unblock paths** `blocked→{backlog, ready, in_progress, awaiting_gate}`
   are not spelled out in docs/GATES_AND_CHECKPOINTS.md (it defines only
   entry into blocked). Without them, ledger tasks M0-T007/M0-T008 (blocked,
   never claimed) could never resume. Chosen as the minimal return-to-origin
   set; each is individually tested.
4. **Blocker "open" rule**: only status `open` (or missing/unparseable =
   fail-closed) blocks. `resolved_temporary` (B-002) intentionally does not
   block, matching how the ledger has been operated.
5. **Checkpoint-id rule** is a safe-filename constraint, not `CP-\d{4}`
   exactly, to avoid breaking future orchestrator naming habits while still
   preventing traversal.
6. The suite copies the real ledger into a temp directory for S7 —
   the tool is never executed against the real ledger (ADR-005 compliant);
   the copy is deleted in `finally`.

## 9. Known limitations

1. `--agent`/`--reviewer` remain caller-provided labels; a dishonest caller
   can still pass `--agent orchestrator`. This is inherent to a CLI without
   authentication and is now stated honestly in the tool itself. Enforcement
   remains procedural (ADR-005) + these structural rails.
2. Concurrency is last-writer-wins: parallel writes to one task never corrupt
   the file but may drop a progress-log entry. No file locking added
   (out of scope; single-orchestrator operation).
3. Blocker referencing is substring-based (word-bounded) over
   `affects`/`detail`; prose mentioning a task id incidentally will block its
   acceptance until the blocker is resolved or reworded — conservative by
   design.
4. `resolve()` containment uses lexical + resolved checks; exotic symlink
   layouts inside `project-control/reports/` are not further analyzed.

## 10. Behavior changes the ORCHESTRATOR must know before merge

These are intended consequences of the owner constraints, but they change
current muscle memory; flagged so the merge does not surprise mid-session
ledger operations (packet risk #2):

1. **G4 now requires a rostered independent reviewer.** Ledger history shows
   some G4 records by `orchestrator`. Going forward the packet's
   `reviewer_agents` must contain the G4 reviewer (e.g., add `qa-engineer`),
   including for THIS task (M0-T014 requires G4; its roster is
   `code-reviewer, security-reviewer` — one of them must run G4, or the
   orchestrator amends the packet roster before gating).
2. **Report paths must live in `project-control/reports/`.** The M0-T002
   precedent (`docs/research/...` as submit report) is no longer accepted
   for new submits; reference research docs from a report file inside
   reports/ instead. Absolute paths are no longer accepted either
   (historically the test suite itself passed absolute paths).
3. **Claim requires `ready` (or `rework`)** — claim directly from `backlog`
   is rejected; record G0 first (current practice anyway) or use
   `progress --status ready`.
4. **`submit` must originate from `claimed/in_progress/self_check/rework`;**
   `progress` can no longer hand-set `awaiting_gate` from the forward chain.
5. **Terminal tasks are immutable** — late gate recordings or progress notes
   on accepted tasks are rejected (previously they silently demoted the
   task; post-acceptance notes belong in checkpoints).
6. **Accept now also verifies dependencies + blockers + awaiting_gate
   status.** E.g., future `M1-T009` cannot be accepted before `M2-T003` is
   accepted; a task named in an open blocker's affects/detail cannot be
   accepted until that blocker is resolved.

## 11. Security / provenance impact

Positive: closes the P0 audit items — status forgery via `progress`,
self-approval via unrostered/renamed reviewers, self_check records
masquerading as independent review, acceptance without dependencies/blockers
checks, path traversal via task-id/gate-id/checkpoint-id/report arguments,
and torn JSON writes. Gate records now carry an honest actor-role dimension,
strengthening the audit trail. No secrets touched; no network use; stdlib
only; temp artifacts cleaned (low-storage policy respected — peak temp usage
a few hundred KB, deleted in `finally`).

## 12. New risks / dependencies

- Merge-order risk: the orchestrator should merge this only at a quiet point
  in ledger operations and re-read section 10 first (the tool is the
  orchestrator's own control plane).
- CI: the control-plane job command is unchanged
  (`python3 tools/test_project_control.py`); the suite now also requires the
  repo checkout to contain `project-control/` (it does, in CI and locally).

## 13. Recommended next tasks

1. Orchestrator: decide whether M0-T014's own G4 reviewer comes from the
   existing roster or a packet amendment (section 10.1) — before dispatching
   gates for this task.
2. Optional follow-up (not contracted): a `blocked_reason`/`unblock` audit
   subcommand so unblock transitions carry a mandatory reference to the
   resolved blocker.
3. Optional: extend `.claude/rules/project-control.md` with the section-10
   operating notes once this task is accepted, so future sessions inherit
   them.

## 14. Producer worktree disclosure

The task prompt assigned worktree `.claude/worktrees/M0-T014` (branch
`task/M0-T014-control-hardening`), but the harness enforces write isolation
to `.claude/worktrees/agent-ac468b57e58cb4969` (branch
`worktree-agent-ac468b57e58cb4969`, base commit d61c9b6 — ahead of the
M0-T014 worktree base; `tools/project_control.py`,
`tools/test_project_control.py`, and the M0-T014 packet were verified
byte-identical between the two worktrees before starting). All work and
evidence live in the agent worktree; the orchestrator integrates onto the
task branch per ADR-005. I did not run the control CLI against the real
ledger, did not push, and did not commit.
