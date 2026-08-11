# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA here as still-current.** This
file is orientation only. Rules/gates/workflow routes live in `CLAUDE.md`. Old blocks via
`git log -p docs/SESSION_HANDOFF.md`. Keep CURRENT-ONLY: the `context-budget` CI check fails > ~4000 tok.

## SESSION 17 — supervisor safety fixes P1/P6/P2 ACCEPTED; P3 + follow-ups + go-live remain

Refreshed **2026-08-11 (session 17; `claude-opus-4-8`)**. **Accepted = 81.** Integration branch is
**PR #220 `control/session15-acceptance`**, worktree `.claude/worktrees/session15-acc`, HEAD ≈ `a80e718`
(verify live; pushed). Owner go-live authorization = **D-011 amendment-004** (R030/R031/R032): full Codex
go-live AUTHORIZED but **strictly sequenced after** P1/P2/P3/P6 accepted + follow-ups + #220→main. Do
control-plane accept work HERE. The ledger wins.

### Done this session (all on #220, pushed)
- **M0-T058 (P1) ACCEPTED (79)** at `9239cc3` — honest `child_record_unwritable_orphan_live` reason code
  (captures terminate_all() bool + bounded process.wait(10s); closes the unverified-termination double-launch).
- **M0-T061 (P6) ACCEPTED (80)** at `fd7d9fa` — dispatched-but-silent reviewer → one re-dispatch → hard
  fail-closed STOP (`SILENT_NO_VERDICT_CODES`; `schema_retry_exhausted`/validation correctly excluded).
- **M0-T059 (P2) ACCEPTED (81)** at `a80e718` — `clear_child_record` removes only `(pid, start_token)`, not
  whole-key (closes the R347 fail-open; + `recorded_start_token_for`; companion 2-line spy fix in
  `test_start_reentry` under an orchestrator-authorized scope expansion).
- Each: G0/G2/G3/G5 all PASS at reviewed_sha==HEAD + independent DCV (empty D-010 set — honest, see below).
  Freeze baseline re-established at each accept (now **1188** 20-module unittest / **1506** full pytest, 0 fail).

### NEXT — runway (ordered; D-011 amendment-004)
1. **P3 M0-T060** — the LAST supervisor safety fix (achieved per-cycle containment `!= job_object` must STOP,
   not merely record). depends_on M0-T058 (accepted). **Shares claude_runner.py with P2 → build off post-P2
   HEAD.** Producer confirms exact file (loop.py likely; claude_runner.py/state_machine.py) at G0. Full gate
   wave (G0/G2/G3/G5 + DCV + accept), supervisor-freeze, ≥1165 baseline + full-pytest parity.
2. **Follow-ups:** drain M0-T056 from `_EMPTY_IDENTITY_GRANDFATHERED` (inert — gained real paths); add the
   M0-T057 O1 empty/whitespace `path_free_justification` unit assertion; run **M0-T047/#219** (nanoid 3.3.17)
   through its full G0/G2/G3/G5 + **D-009** DCV + accept, then merge #219 to main.
3. **Merge PR #220 → main** (Tier A, after required checks green). Note: #220's `web-dependency-security`
   stays red on nanoid until #219's fix reaches this branch (known non-required; D-011 item 1).
4. **M0-T056** (R595 production actuation) — **AUTHORIZED**: build + full gate wave (G0/G2/G3/G5 + DCV) + accept.
5. **Activate R595 + add the accept allowlist** — **AUTHORIZED** — supervisor live end-to-end. ONLY after
   M0-T056 accepted. Verify default_mode flips off shadow + the live proof host satisfies the C1 Job-Object
   gate (P8: POSIX/Render hard-refuses `start`). Steps 4-5 STRICTLY after 1-3 (R031, safety bar NOT waived).

### Carried M0-T056 pre-actuation residuals (do not assume closed)
P1/P6/P2/P3 ARE the pre-M0-T056 corrections (activation-checklist §2026-08-11 pin). Now landing. Plus **G5 LOW
advisory (M0-T059)**: if M0-T056 adds a concurrent recorder settling the same pid, use an atomic read-modify-write
in `clear_child_record`/`recorded_start_token_for` (two `get_state` reads today; benign single-threaded, fails
closed). M0-T056 also: adds a 2nd spawner (`turnover_adapters.py make_subprocess_command_runner`) + removes the
human — the reason these residuals matter.

### Session-17 accept mechanics (proven; reuse)
- **Producers auto-isolate off origin/main** (lags #220 by ~40 commits). Instruct each producer, in ITS OWN
  `agent-<id>` worktree, to `git reset --hard <post-dep-accept-sha>` first (lossless — main is an ancestor);
  extract the fix as `git diff <sha>..HEAD` and cherry-pick onto #220. Guard EVERY producer prompt: before any
  git write, `git rev-parse --show-toplevel` must contain `.claude/worktrees/agent-` (else STOP — a git write in
  the primary checkout corrupts orchestrator state; happened + self-restored session 17).
- **NEVER resume a TaskStop-KILLED producer** (its worktree is torn down → resume lands in the primary checkout).
  Natural-completion resume via SendMessage is safe (worktree persists). Dispatch fresh instead.
- **Read-only reviewers run IN `session15-acc` at HEAD** (not isolated); their safety guard correctly refuses the
  reset — so review at the current HEAD directly (`git show/diff <sha>`), no reset instruction needed.
- **These new supervisor tasks have an EMPTY D-010 applicable set** (`derive_applicable → []`): D-010 rows are
  task_ids-scoped to prior tasks (R347→M0-T056, not the fix task). Record an empty-set `task_verifications` row
  (verifier=directive-compliance-verifier ≠ producer) so accept()'s cited-directive check passes; substance is G3+G5.
- Keep accept evidence UNCOMMITTED until after accept (reviewed_sha==HEAD); material identity stable across
  control-plane commits; gates stamped at HEAD. `project-control/**`+`directives/**` explicit LF; stage exact
  paths. **CI ruff runs only in `services/api`** (tools/ not linted); the CI `supervisor-bridge` job runs the FULL
  `pytest tools/test_agent_supervisor_*.py` (all 36 modules) — the 20-module freeze list is a SUBSET, so confirm
  full-pytest parity too. Reviewer/orchestrator model `claude-opus-4-8` xhigh; producers UNNAMED.

### Still in force
deployment/G6/Graphify/expansion holds; `default_mode=shadow` until R595 flips; a failed gate / reproduced defect
/ unresolvable contradiction STOPS and returns to the owner. Codex model-fallback RESOLVED (tries main model first,
non-sticky).
