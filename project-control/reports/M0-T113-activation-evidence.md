# M0-T113 — R187/R595 limited-auto activation: executed, first cycle FAIL-CLOSED at an owner touchpoint (R260 report)

Recorded by the orchestrator 2026-08-29. The exact certified start command (item-3 shape,
`--mode limited-auto --owner-enable-bounded-auto`, all inputs named) was executed at the
green launch tip `cfc6b16` (CI 20/20) after the §5 preflight PASS. **Activation succeeded;
the first cycle stopped fail-closed exactly per the certified design** — the run halted at
an ASK-tier owner touchpoint and refused to interpret a missing checkpoint as success (S14).
Nothing was auto-approved, nothing forwarded, no repository write occurred.

## The owner's 7 report items (R260)

1. **Activation record and effective mode:** `start` JSON output (task log `b0na0bwuc`):
   `"mode": "limited-auto"`, `"limited_auto_enabled": true`, `"dispatched": true`,
   controller `0.4.0-phase4`; all 11 pre-dispatch probes PASS (task authority, branch,
   worktree, git/remote, auth, CLI capability/pinned identity, pending requests, deadlines,
   external effects, config identity via the re-recorded manifest `b07818fa…`, surviving
   children); containment = kill-on-close Job Object.
2. **Controller PID / session / run identity:** run id `run_M0_T107_unitJ`; runtime dir
   `%LOCALAPPDATA%\NYCBuildabilitySupervisor\33dfa57d54dbc5d1…`; budget digest
   `c1a51d3ad3856be8…`; started `2026-08-29T05:05:19Z`, elapsed 117 s; journal
   `supervisor_journal.sqlite3` (integrity ok, transitions recorded), audit chain head
   sequence 5. The controller process has EXITED (typed refusal exit 11 `unsafe` /
   `no_valid_checkpoint`) — no live PID; the fail-closed exit is the designed outcome of an
   unattended run that reaches a human-required decision.
3. **Selected campaign task:** M0-T107 (unit J, plugin portability plan) — claimed by
   `supervisor-loop-fable-producer`, isolated worktree `wt-m0t107`, branch
   `task/M0-T107-plugin-portability` @ `796e18f`.
4. **Evidence of the first bounded dispatch:** `provider_calls_made: 1`;
   `claude_runs_per_task: 1/12`; cycle path `START_CLAUDE → CLAUDE_RUNNING →
   PAUSED_RECOVERY`; the live Fable worker proposed THREE commands that the policy held
   (proof of a real dispatched worker under live policy):
   - `9f45b2ca` PowerShell (ASK, `unclassified_request`): list M0-T107 reports + sibling
     worktree dirs (read-only discovery)
   - `c73f9247` PowerShell (ASK, `unclassified_request`): list supervisor runtime dirs
     (read-only discovery)
   - `7e4b33d8` Bash (ASK, `undocumented_command`): compute checkout path hashes
     (read-only discovery)
   All three recorded `behavior: DEFER_TO_OWNER` (rule `S4.3/fallthrough` — unclassifiable
   is ASK, never AUTO). The worker run ended without a structured checkpoint → S14
   (`missing_checkpoint: a missing result is never interpreted as success`) → synchronous
   stop (owner-touch 1 of budget 2) → `PAUSED_RECOVERY` → typed refusal, exit 11. The
   producer worktree is CLEAN (no write happened).
5. **Operator commands** (each with `--checkout C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`):
   `python -m tools.agent_supervisor status [--json]` · `pause` / `resume` ·
   `graceful-stop --reason "<why>"` (+ `--clear`) · `emergency-stop` · `stop` (+ `--clear`) ·
   `pending-approvals` · `approve-once <request-id> <digest>` / `deny <request-id> <digest>` ·
   `clear-recovery` (audited exit from PAUSED_RECOVERY) · in-terminal: `/loop-status`,
   `/loop-pause`, `/loop-resume`, `/loop-stop`, `/loop-emergency-stop`.
6. **Telegram notification state:** `configured: no` (SUPERVISOR_TELEGRAM_BOT_TOKEN /
   _CHAT_ID absent — presence-only check, values never read); queued 0, delivered 0;
   one-way only (R242); the live send remains the owner-typed exact-command canary (R245).
7. **Awaiting owner approval:** YES —
   (a) the three ASK requests above (`approve-once`/`deny` with request-id + digest;
   answers are an owner touchpoint per the runbook §12);
   (b) the resume decision out of `PAUSED_RECOVERY`: after the asks are dispositioned,
   `clear-recovery` + an explicit re-`start` (same certified command; recovery never
   self-resumes and never broadens limited-auto — restart_attempts 0/3,
   claude_runs 1/12, all budgets healthy).

## Operational note (for the resume decision)

The three held commands are read-only discovery the worker could equally do with its
native in-scope file tools; `approve-once` grants are bound to the DEAD run's request ids,
so the practical resume is: deny (or leave-and-revoke) the stale asks → `clear-recovery` →
re-run the certified start. If ASK-stops recur on routine read-only discovery, the durable
fix is packet enrichment (documented commands, M0-T063 precedent) — a control-plane change
to propose separately, never a policy loosening from inside the loop (S16.7: the touch
budget authorizes nothing).

## ADDENDUM — owner-directed restart (Amendment 11 R268/R269): STOPPED SAFELY on a restart-blocking seam defect

Executed per the owner's instruction (capture `871cab8`, rows R268–R271, validator EXIT=0;
CI 20/20 on that tip before acting):

1. **Denials (R268):** all three stale asks denied via the documented
   `deny <request-id> <digest>` — digests echoed back exactly
   (`5637335f…`, `56cbd282…`, `ae36645d…`); `pending-approvals` then reported
   **"no pending approvals"**; status showed "resolved history: 3 … not actionable".
2. **Recovery cleared (R268):** `clear-recovery` → "recovery pause cleared by an explicit
   operator command; the journal now rests at PREFLIGHT … `start` may now resume this run".
3. **Restart (R268):** the IDENTICAL certified start command re-ran at the green tip
   `871cab8`. Outcome: **pre-dispatch REFUSAL — `UNSAFE_OR_DRIFTED`, revalidation failed
   for `['pending_requests']`, `dispatched: false`, `provider_calls_made: 0`, exit 11.**
   No worker launched; the journal parked back in PAUSED_RECOVERY; nothing forwarded,
   nothing written. The command policy was NOT loosened or bypassed at any point.
4. **Root cause (primary evidence, code + journal):** the S11.5
   `probe_pending_requests` reads raw `journal.open_asks()` (rows with
   `answered_at_utc = ''`) — it lacks the M0-T070 read-time broker-reconciliation that the
   STATUS command applies (`cli.py` ~1487). And on the write side,
   `ApprovalBroker.deny_request` (and `approve_once`) mark the approval record answered but
   never call `resolve_ask` on the linked `ask_<request_id>` row — the exact omission
   M0-T070 fixed in `revoke_all` ONLY (`broker.py:684`). `revoke-all` cannot clear the rows
   either (it skips DENIED records). Net: after ANY owner deny, restart is permanently
   blocked by ask rows no documented surface can answer. The journal's three rows show
   `answered_at_utc: ""` while their approval records are `denied` — the two certified
   surfaces disagree.
5. **Disposition per the owner's standing rule (R270/R271):** NO further restart attempts;
   NO hand-editing of the runtime journal (that would be improvisation on durable state);
   the loop is stopped safely (no live process, no pending effects, worktree clean). A
   bounded SEPARATE correction is PROPOSED as ledger packet **M0-T115** (deny/approve
   resolve their ask rows exactly as revoke_all does + probe read-time reconciliation so
   pre-fix journals — including this live one — become truthful without journal edits +
   removal-sensitive regression tests + H2 RepairRecord). Because the fix touches
   `tools/agent_supervisor/**`, it INVALIDATES the R247 certification: the full
   re-certification cycle must run before autonomous operation resumes (R271). The owner
   may optionally schedule M0-T114 (residuals) into the same recert window — owner
   decision, kept separate by default.
6. **R269 confirmation set:** new run identity — none was minted (the refusal is
   pre-dispatch; run `run_M0_T107_unitJ` remains the identity, restart_attempts consumed:
   the refused start does not count a claude run: counters still 1/12); live Fable 5
   dispatch — DID NOT occur this attempt (0 provider calls); current task — M0-T107
   (claimed, worktree clean at `796e18f`); first-checkpoint progression — NOT REACHED;
   blocked by the seam defect above, not by policy or by the worker.
