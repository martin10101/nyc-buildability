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

## ADDENDUM 2 — the R276 RERUN (2026-08-30): DISPATCH + FIRST CHECKPOINT ACHIEVED; certified fail-closed halt at the independent-review gate

Executed after the complete Amendment-13/14 window (M0-T117/T118/T120/T119 all accepted;
2.1.251 admitted per R282) and a fully green R276 preflight. Two owner-typed start
attempts via the `!` prefix:

* **Attempt 1** (bash stripped the unquoted backslash paths): every path-dependent S11.5
  probe refused fail-closed — `UNSAFE_OR_DRIFTED`, dispatched false, 0 provider calls,
  exit 11, journal stayed at PREFLIGHT. An orchestrator command-formatting error, and a
  live demonstration that corrupt inputs cannot dispatch.
* **Attempt 2** (forward-slash paths): **ALL 12 PROBES PASS → DISPATCHED.**

**The R276 item-7 confirmation set — ALL CONFIRMED:**

1. **Run identity:** `run_M0_T107_unitJ` RESUMED (resumes=1) under the byte-identical
   run-budget digest `c1a51d3a…`; the pre-fix journal's 3 denied asks reconciled at both
   seams (`pending_requests` PASS) — **the R274 end-to-end restart proof is COMPLETE.**
2. **One-time repin (R285):** executed and recorded with provenance — `cli_capability_manifest`
   PASS: "an operator re-pinned ['claude'] to their current identity"; the pinned digest
   is the admitted `d6f6c29a8ac6b3cf…` (2.1.251). Drift detection re-armed against the new pin.
3. **Routing tooth (M0-T120) live:** `shell_routing` PASS — measured evidence matched the
   pinned identity, verdict `native_preferred`.
4. **Live Fable 5 dispatch:** worker session `02b014ee…`, `observed_models:
   ["claude-fable-5"]`, `model_mismatch: false`, returncode 0, 143 stream events,
   2 provider calls this start (run counters: claude_runs 2/12, codex_reviews 1/3).
5. **FIRST-CHECKPOINT PROGRESSION — ACHIEVED:** structured checkpoint
   `M0-T107-ready-2026-08-29-01` returned, parsed, validated, and correlated (digest
   `2ac59818…`); a bounded evidence packet assembled (46,025 bytes, digest `5539a2be…`);
   **`permission_decisions: []` — the worker completed the whole run with ZERO brokered
   command requests and zero ASK-stops** (the original shell-first stall did not recur;
   routine discovery reached a structured checkpoint, satisfying the R276 proof goal).
   Note recorded honestly: `native_tools_guidance_appended: false` — the resumed run
   reuses its original digest-bound prompt (appending the M0-T120 guidance would break
   the prompt digest); the 2.1.251 worker routed natively regardless, exactly as the
   M0-T120 measurement predicted. Fresh runs minted after this one carry the guidance.
6. **Certified fail-closed halt (cycle 1):** path START_CLAUDE → CLAUDE_RUNNING →
   CHECKPOINT_RECEIVED → COLLECT_EVIDENCE → CODEX_REVIEW → VALIDATE_DECISION →
   POLICY_CHECK → **HALTED**. The independent Codex reviewer (`gpt-5.6-sol`) returned
   exactly one schema-valid decision: **HALT_UNSAFE** — finding: *"The mandatory fresh,
   independent repository review was not completed, so issuing CONTINUE would rely on the
   untrusted worker checkpoint."* Nothing was forwarded; a synchronous S9 stop was counted
   (owner-touch 2 of budget 2, within budget); exit 10. The system refused to advance on
   the worker's self-report — the exact review-independence principle this platform is
   built on, exercised live.
7. **Rotation pending:** the worker session crossed the 400k rotation threshold
   (604,772 tokens); per S11.2 the in-flight unit was not interrupted — the NEXT start
   rotates at the seam (the certified rotation crossing, to occur live on continuation).
8. **State at rest:** journal HALTED → operator-startable; 0 open asks; 0 pending
   effects; audit chain intact (31 events); worktree `wt-m0t107` clean at `796e18f`;
   no external writes.

**Resolution path:** the HALT_UNSAFE stop is a certified human touchpoint. Continuation is
an explicit operator start of the SAME certified command WITHOUT `--repin-cli-identity`
(the one-time repin is consumed); cycle 2 re-runs the Codex review (1/3 used) after the
pending rotation. The owner decides when.
