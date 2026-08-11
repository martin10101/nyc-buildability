# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA here as still-current.** This
file is orientation only. Rules/gates/workflow routes live in `CLAUDE.md`. Old blocks via
`git log -p docs/SESSION_HANDOFF.md`. Keep CURRENT-ONLY: the `context-budget` CI check fails > ~4000 tok.

## SESSION 17 — ALL FOUR supervisor safety fixes ACCEPTED (P1/P6/P2/P3); follow-ups + go-live remain

Refreshed **2026-08-11 (session 17; `claude-opus-4-8`)**. **Accepted = 82.** Integration branch is
**PR #220 `control/session15-acceptance`**, worktree `.claude/worktrees/session15-acc`, HEAD ≈ `94844a9`
(verify live; pushed). **Runway step 1 (the 4 pre-M0-T056 supervisor safety fixes) is COMPLETE.** Owner go-live authorization = **D-011 amendment-004** (R030/R031/R032): full Codex
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
- **M0-T060 (P3) ACCEPTED (82)** at `94844a9` — achieved per-cycle containment `!= job_object` is a fail-closed
  STOP (→ PAUSED_RECOVERY, `containment_degraded`), not merely recorded; placed AFTER the S14 checkpoint/effect
  reconciliation so no paramount stop is masked; `job_object` proceeds unchanged.
- Each: G0/G2/G3/G5 all PASS at reviewed_sha==HEAD + independent DCV (empty D-010 set — honest, see below).
  Freeze baseline re-established at each accept (now **1191** 20-module unittest / **1509** full pytest, 0 fail).

### NEXT — runway (ordered; D-011 amendment-004). Step 1 (P1/P6/P2/P3) DONE.
1. **Follow-ups:** (a) drain M0-T056 from `_EMPTY_IDENTITY_GRANDFATHERED` (inert — gained real paths;
   control-plane-verifier flagged it) — do at the next control-plane touch; (b) add the M0-T057 O1
   empty/whitespace `path_free_justification` unit assertion (code already fails closed); (c) run **M0-T047/#219**
   (nanoid 3.3.17 override + CI-regenerated lock exist on `task/M0-T047-nanoid-lock`; #219 mergeable but
   M0-T047 is backlog with ZERO gates) through its full G0/G2/G3/G5 + **D-009** DCV + accept, THEN merge #219 to
   main (merging un-gated code is NOT permitted). (a)+(b) are small orchestrator/test edits — still gate them.
2. **Merge PR #220 → main** (Tier A, after required checks green). Note: #220's `web-dependency-security`
   stays red on nanoid until #219's fix reaches this branch (known non-required; D-011 item 1).
3. **M0-T056** (R595 production actuation) — **AUTHORIZED**: build + full gate wave (G0/G2/G3/G5 + DCV) + accept.
4. **Activate R595 + add the accept allowlist** — **AUTHORIZED** — supervisor live end-to-end. ONLY after
   M0-T056 accepted. Verify default_mode flips off shadow + the live proof host satisfies the C1 Job-Object
   gate (P8: POSIX/Render hard-refuses `start` → the live proof likely runs on the owner's Windows host w/
   elevated config ACL; stop + hand the owner the exact command at that step). Steps 3-4 STRICTLY after 1-2
   (R031, safety bar NOT waived).

### Carried M0-T056 pre-actuation residuals (do not assume closed)
P1/P6/P2/P3 ARE the pre-M0-T056 corrections (activation-checklist §2026-08-11 pin) — ALL ACCEPTED now. Two
non-blocking G5 advisories carried into M0-T056 hardening: **(M0-T059)** if M0-T056 adds a concurrent recorder
settling the same pid, use an atomic read-modify-write in `clear_child_record`/`recorded_start_token_for` (two
`get_state` reads today; benign single-threaded, fails closed); **(M0-T060)** optionally also gate the achieved
`job_object` branch on `ContainmentReport.verified_in_job` (the guard checks kind only; near-impossible kernel
edge). M0-T056 also: adds a 2nd spawner (`turnover_adapters.py make_subprocess_command_runner`) + removes the
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
