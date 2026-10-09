# M0-T079 G5 security review (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the read-only reviewer agent's return channel
(report-preservation rule). Reviewer: t079-g5-reviewer (independent; reviewer ≠ producer ≠
verifier). Verdict FAIL — blocks acceptance; drives the consolidated T079 correction round.

---

# G5 SECURITY REVIEW — M0-T079 (commit e830c4b) — FINAL

## VERDICT: FAIL — 2 must-fix, 6 important, 12 minor.

The activation gate held under sustained attack. The budget did not. Both must-fix items are in the new evidence/persistence plumbing, not in the gates. Suite and modularity claims verify.

---

## MUST-FIX

### M1 — A supervised run can reset its own budget by nulling one JSON field

`RunBudgetLedger.start()` takes the resume branch only when `isinstance(existing, Mapping) and existing.get("started_at_epoch") is not None` (run_budget.py:277). Every other shape falls through to the fresh-start path at line 298, which mints a new `started_at_epoch`, zeroes `elapsed_high_water_seconds`, empties `counters`, and NEVER reaches the `budget_conflict` digest check at lines 280-287.

Proven end to end. Control case: a run 3000s into a 3600s budget, relaunched honestly with a 10-hour budget, is correctly refused with `budget_conflict`. Same relaunch after setting `started_at_epoch` to null:

```
ACCEPTED. resumed=False  elapsed=0s  exhausted=False
new budget in force : 36000.0s (was 3600s)
high-water wiped to : 0.0
breaker tallies now : {}
=> budget_conflict was NEVER evaluated; the run reset its own clock.
```

Deleting the record does the same silently. Neither raises BudgetError, emits an audit event, or sets `resumed`. Three distinct corruptions all mint a fresh unbounded budget: record deleted, record not a Mapping, record intact but `started_at_epoch: null`. No test covers any of them.

This bypasses every other monotonicity guarantee at once — `persist_counters`'s max(), `restore`'s max(), the elapsed high-water clamp — because the record they defend is simply replaced. It contradicts the module docstring verbatim: "the persisted record wins", "a run can never extend, shrink, or reset its own bounds", "none of which a run can talk its way out of."

ATTACK/CONSEQUENCE: the supervised worker runs as the same OS user on the same host as the supervisor and can write the journal sqlite DB. One field edit gives it an unlimited run with fresh model-call, external-write, restart, and livelock allowances. For an unattended controller whose entire purpose is bounding that worker, this is a containment break.

FIX SHAPE: treat present-but-malformed as BudgetError, distinguish "no record" from "unreadable record", audit both.

### M2 — New probe evidence leaks credentials to stdout, bypassing the package's own mandatory redaction

`cmd_start` attaches the full probe report to the emitted payload (cli.py:2966). `ProbeResult.to_dict()` is `dataclasses.asdict`, carrying `evidence` and `detail` verbatim, and `probe_git_and_remote_state` puts raw `git remote get-url` output into both (recovery_probes.py:363, 385-390). `_emit` (cli.py:1742) prints it with a bare `json.dumps`.

Proven: with a remote of `https://x-access-token:ghp_...@github.com/o/r.git`, the token appears in the emitted payload in both the `remote_url` evidence field and the human-readable detail string. The same structure through the package's own `redact_structure` masks it cleanly — 4 substitutions, labels `basic_auth_url` and `github_pat`.

The mitigation exists, is declared mandatory by redaction.py's header ("Everything the supervisor persists or transmits passes through here FIRST"), is correctly applied by audit_log.append (:194), evidence.py, and ephemeral_review.py — and is simply not called on the one path T079 newly routes external-tool output into. A routine gh/CI remote leaks a PAT to scheduled-task logs on every `start --json`.

---

## IMPORTANT — including adjudication of all seven named items

### I1 — Watchdog argv-prefix replay of the enable flag (ADJUDICATED: important, not must-fix)
`turnover_adapters._orchestrator_argv` (:414-431) splats the operator-supplied `orchestrator_argv_prefix` verbatim. `assert_argv_safe` (process.py:133-171) denies only permission/sandbox/hook-bypass tokens and effort flags — `--owner-enable-bounded-auto` is in neither set and passes straight through. `cmd_orchestrator_watchdog` is designed to be invoked BY the Windows Task Scheduler, so a watchdog task whose stored prefix contains the flag replays the enable on every trigger. Does NOT falsify "only the CLI flag sets it" — it IS the flag, owner-typed at install time; it DOES dent "per-launch". The real defect is the asymmetry — `resume_scheduler` guards its argv with `assert_fixed_action` exact-list-equality, this path has no equivalent. No such recipe exists in the repo today. Cheap fix: add the enable to a deny set for synthesized argv.

### I2 — Per-day tally decay (ADJUDICATED: important, real, fail-closed)
`persist_counters` is monotonic by max() (run_budget.py:435), but `check()` evaluates the PERSISTED record against limits that include per-day counters (`_exhausted_counters`, :410). The live breaker rolls per-day counters to 0 on a new day; the record keeps the peak. Proven: day 1 hits the 2000 `model_calls_per_day` cap → exhausted; day 2 the breaker correctly rolls to 1, the record still reads 2000, `check()` still returns exhausted. A daily cap silently becomes a permanent cap on that `--run-id`. Owner recovery = new run id. This will strand exactly the long-running 10-hour R011 case.

### I3 — run_live_probes aborts on the first raising probe; exception escapes as a traceback
Docstring claims "the report always carries every answer"; all eleven probes are arguments to one tuple literal (recovery_probes.py:667-688), so the first raise kills the rest. Three probes guard journal access and return `_unknown`; two do not — `probe_cli_capability_manifest:439` and `probe_scheduled_deadlines:533`. Verified: with a raising journal, JournalError propagates out of `run_live_probes`; `cmd_start` catches only `(LoopError, IllegalTransitionError)` and `BudgetError`, and `main()` has no handler — traceback plus exit 1, the generic code refusals.py says it started at 10 to avoid. Fails closed, but reintroduces the defect the task set out to fix.

### I4 — Corrupt-budget ValueError (ADJUDICATED: important, folded into I3)
`RunBudget.from_dict` does a bare `float(raw)` (run_budget.py:194), so a corrupt persisted `wall_clock_seconds` raises ValueError/TypeError, not BudgetError — uncaught, traceback. `BreakerError` from `restore_counters` (unknown tally name in the record) escapes identically: `persist_counters` validates names on write, `restore_counters` does not on read. Same root cause as I3: the typed-refusal contract covers only three exception classes.

### I5 — Unaudited budget_conflict and breaker-trip audit gap (ADJUDICATED: important, one finding)
The entire commit adds exactly ONE `audit.append` (`run_budget_exhausted`, loop_breakers.py:173). Not audited: (a) `budget_conflict` — the canonical "a run tried to change its own bounds" tamper signal, with `audit` in scope at cli.py:3045; (b) circuit-breaker trips where `breaker_stop` is called with `trigger=""` (e.g. `supervisor_cycles_per_task`, loop.py:1659), which reach the chain only via the state-machine transition detail, so a trip with no trigger leaves no record at all; (c) `refused_mode`, because `bounded_mode_gate` runs before `_open_runtime`, so attempted bounded-mode launches under the active R033 hold leave no trace. Compare cli.py:3013 where the containment refusal IS audited with an explicit "safety condition, not a passing remark" comment. Consequence: the three events a security reviewer would most want in a tamper-evident log are the three that aren't in it.

### I6 — An owner-enabled bounded run with a missing input exits 0
The `if not dispatchable:` branch (cli.py:2971) sets `stopped_because` but never assigns a `refusal`, so `cmd_start` returns 0. The code says so: `# Missing-input stops still exit 0.` (cli.py:3110). A drifted argv, moved config, or renamed executable reports SUCCESS to an unattended launcher that never ran a cycle. Pre-existing, but the bounded mode is what makes it dangerous. G4 filed this too; confirmed from the code independently.

### I7 — deadline_restored refuses on an already-expired deadline
`recover_boot` stamps it whenever `resume_not_before_utc` is merely non-empty, with no clock comparison (recovery.py:519-527); T079 makes that refuse with exit 13. Nothing clears the key on expiry — `mark_consumed` touches only TRIGGER_KEY; sole clearer is `ResumeScheduler.cancel` (resume_scheduler.py:968). NOT bricking: `stop`, `emergency-stop`, `cancel-scheduled-resume` all reach it (cli.py:1996, 2021, 2115). The tightening itself is correct. Narrow gap: `probe_scheduled_deadlines` already computes `outstanding` correctly against the clock (recovery_probes.py:542-547) but always returns `_ok`, and the refusal ignores it.

### JOURNAL ACL THREAT MODEL (ADJUDICATED: not a separate finding — it is M1's enabling condition)
`state_kv` is unchained and unversioned; `integrity_check` (durable_state.py:342-350) only verifies the table exists, so a rewritten `run_budget` row passes `require_healthy()` clean. The journal DB is not ACL-hardened — `harden_controller_config.ps1` covers config.toml only, `os_acl.py` is read-only probing. Protection is code discipline, not structure. Declined as its own must-fix: hardening the DB ACL is reasonable defence-in-depth but not the defect — M1 is, because the code has an explicit fail-closed contract for exactly this case and does not honour it. Recommend M1 now, ACL hardening as a separate scoped item (owner checkpoint — host act). Note also `DurableJournal.restore_from` (:653-666) is an unvalidated whole-DB `shutil.copyfile` — latent, currently only reachable against a scratch probe path.

---

## WHAT HELD UNDER ATTACK

ACTIVATION SURFACE — clean, and structurally so. No software path to the enable. Six `LoopConfig(` sites, five are doctor self-tests; the one production site (cli.py:2846) reads `args.owner_enable_bounded_auto` explicitly. No `LoopConfig(**...)`, no `setattr(args, ...)`, no `vars(args)`. config.py has no such field — its only dict-splat is `Limits.from_mapping` (:222) which rejects unknown keys first (:203-207), and `default_mode` is barred from limited-auto at load (:339-344) and reaches only a diagnostic print. No env var touches mode/enable/budget. Two independent checks: `bounded_mode_gate` is the first statement of `cmd_start`, refusing exit 16 before the lock, recovery, or any provider contact; `LoopConfig.__post_init__` re-checks at construction. Both refuse a stray enable on a non-gated mode rather than ignoring it. Durable-resume injection blocked by construction: original argv never persisted, action args are the constants `--resume-scheduled-wake`/`--recover-boot`, `assert_fixed_action` enforces exact list equality. `model_change_ipc` handles model names only; broker.py:391-398 records model-proposed `setMode` as REJECTED; broker and remote_approvals write the durable `limited_auto_enabled` flag only ever False. Nothing in any .ps1/.cmd/.xml/.yml/doc carries the flag.

BUDGET DEFENCES OTHER THAN M1 — sound. Conflict digest is SHA-256 over canonical JSON of the NORMALIZED dict (both sides pass `__post_init__`), so serialization variance cannot slip through and collision needs a SHA-256 break. run_budget.py:333 is the sole writer of `run_budget/*` across ~60 set_state sites, all literal or literal-prefixed keys. `durable_state` has NO delete/clear/purge API — zero hits for DELETE FROM, VACUUM, DROP TABLE. retention.py deletes files only and is never constructed in production. `broker.revoke_all`'s all_state() rewrite is guarded by `startswith("approval/")`. `restore` rejects unknown names and negatives, only ever raises a tally. Clock seam defaults to `system_clock` with no CLI or config override. Emergent strength: config breaker limits are folded into the digest, so an owner LOOSENING config.toml mid-run cannot silently grant a resumed run more allowance — it surfaces as budget_conflict.

CONTAINMENT — zero behavioral change, diff-verified. process.py untouched. The M0-T060 enforcement block in loop.py is BYTE-IDENTICAL between e830c4b^ and HEAD. The `elif not containment_ok:` gate is unchanged; only a `refusal = ...unsupported_platform` assignment added inside it, and the new safe_but_forbidden/deadline_restored branch sits BEFORE it, which can only refuse earlier.

AUDIT CHAIN — no bypass. audit_log.py:226 is the only writer of audit.jsonl; `append` always advances sequence/prev_digest and digests the record, and refuses to extend a damaged chain. Other `append()` methods are delegating wrappers or target a different file. The one new event goes through it.

R595 — untouched. Every R595/activation string in the diff is prose reaffirming the prerequisite. Only new code is a per-launch operator flag structurally identical to the pre-existing R595-gated `--authorize-turnover-actuation`. No new or expedited approval path. Supervisor-freeze rule section 4 satisfied.

SUITE: 2261 passed, 3 skipped, 0 failed (43m56s, exit 0) — above the >=1165 freeze floor. New modules alone: 116 passed. `modularity_check --check`: failures 0, 5 pre-existing warnings. Producer claims verify.

---

## MINOR

`probe_cli_capability_manifest` self-pins on first use (trust-on-first-use once a pin is deleted). `probe_auth` asserts file presence only (honestly documented). `tick_daily` no-ops without a ledger (per-day counters unenforced for direct SupervisedLoop callers). `tick_event`'s "must not go unrecorded" message lands in `warning` and is discarded (both counters still tick). `_previous_checkpoint_id` not persisted (first cycle after crash-resume cannot trip `consecutive_no_progress`). `probe_scheduled_deadlines` compares ISO strings lexicographically behind a regex anchoring only `^\d{4}-\d{2}-\d{2}T` (gates nothing today; load-bearing once I7 consumes `outstanding`). AuditLog holds chain head in memory (one injected duplicate-sequence line freezes further appends; documented, fail-closed). recovery.py:71/98/107 defines a dormant durable `limited_auto_enabled` key no production code writes True and that does not feed LoopConfig (inert latent lever). start_gate.py:122 annotates `journal: DurableJournal` without importing it (harmless under PEP 563). Stale docs: remote_approvals.py:308-309 and README.md:11/:269 still say limited-auto is "not implemented at all, in any form."

---

REVIEWED IDENTITY: c52613f28732d73085efa71114cddde7a1468614
Current HEAD 73f5b85 (one evidence-only ledger commit); `git diff --stat c52613f..HEAD -- tools/` is EMPTY, so all findings hold at both.

COMMANDS RUN: git rev-parse/log/status/show (full + scoped + e830c4b^ diffs of the containment block), git grep for the enable flag, extensive grep/sed reads under tools/agent_supervisor/, three read-only scratchpad Python probes (probe_failclosed_check.py, probe_leak_check.py, budget_tamper_check.py — nothing written to the repo), pytest of the two new modules, full-suite pytest -p no:randomly, modularity_check --check. No repo writes, no git mutations, no tools/project_control.py. Read-only throughout.
