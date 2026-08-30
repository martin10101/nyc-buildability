# M0-T107 — Amendment-20/21 live journey: DISPATCHED, counted stop `no_valid_checkpoint` after exactly 12/12 turns — eight-point proof 5 PASS / 1 FAIL / 2 not reached; full system-level assessment (R361)

Recorded by the orchestrator 2026-08-30 (session `session_01SfXcRw7emzdojCDJmKxNTM`).
The owner executed the Amendment-21 corrected start at ~19:35:20Z. The run **DISPATCHED**
(cycles=1) and stopped: `stopped=no_valid_checkpoint`, final_state **PAUSED_RECOVERY**,
exit 11. Per R361/R371: **no restart, no retry, no clear-recovery, no repair window; the
journal rests at PAUSED_RECOVERY; everything is preserved.** Per R362 no autonomy claim is
made: the complete journey did NOT succeed. All evidence below is primary (audit chain,
journal sqlite read-only, the worker CLI's own session transcript).

## 1. The eight-point proof (R352–R359) — recorded honestly

| # | Row | Verdict | Primary evidence |
|---|---|---|---|
| R352 | Old 640k session never contacted again | **PASS** | Audit seq 48 `over_ceiling_session_shed`: `shed_provider_session_id 798d2f00-a346-49b4-9a95-8d746b617e22`, "NEVER resumed (D-024-R333)", `pending_flag_consumed: true`; no resume of that id anywhere in the chain |
| R353 | Rotation/shedding BEFORE worker provider launch | **PASS** | Shed at 19:35:20.436Z (seq 48) → preflight_pass → worker's first transcript event 19:35:22.293Z |
| R354 | Distinct fresh Fable 5 session identity | **PASS** | New session `0835bb80-0f2e-451f-882d-0b37df6d77d5` ≠ `798d2f00…`; transcript `model: claude-fable-5`, CLI 2.1.251; genuinely fresh context — final live context ≈ 72k (cache_read 67,935 + creation 3,962) |
| R355 | Worker inside `wt-m0t107`, never the primary checkout | **PASS** | Transcript `cwd: C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t107`, `gitBranch: task/M0-T107-plugin-portability`, stored under the `wt-m0t107` project slug; the seam live-refused the unbound shape hours earlier (exit 11 `cwd_primary_checkout`) |
| R356 | Task, checkpoint lineage, budgets, audit history, exactly-once preserved | **PASS** | `run_budget_resumed` resumes=2, same `run_33dfa57d54db`, `started_at 2026-08-30T03:01:47Z` preserved; owner-touch ledger carried (2 counted touches: 05:44:12Z + 19:37:48Z, "the budget is a measurement and authorizes nothing"); audit chain verified head 53; `duplicate_events: 0`; shed flag consumed exactly once; no journal edits |
| R357 | Valid structured checkpoint reaches the independent Codex reviewer | **FAIL** | `claude_unit_completed` `error_category: missing_checkpoint`, returncode 1; NO checkpoint JSON anywhere in the 97-event transcript |
| R358 | Codex completes its independent review | **NOT REACHED** | No checkpoint existed to review; Codex was never contacted this cycle |
| R359 | M0-T107 actually advances | **NOT ACHIEVED** | `wt-m0t107` unchanged, clean at `796e18f`; no commits, no checkpoint |

## 2. Root cause of the counted stop (from the worker's own transcript)

The worker ran **exactly 12 distinct assistant API turns — the `--max-turns 12` unit
bound (`claude_runner.py:306`)** — over 2m24s (19:35:22→19:37:46Z), and was cut off
**mid-tool-use** (final assistant `stop_reason: tool_use`, a Grep; a `max_turns_reached`
terminal marker is present). The unit instruction was "Report a structured checkpoint for
the current authorized stage" + the S8.3 contract (`checkpoint_contract_appended: true` —
the contract WAS delivered). A fresh-context worker (by design of the certified shed) must
re-orient from zero; this one spent all 12 turns exploring the repository (supervisor
sources among them) and never emitted the required JSON. S14 correctly treats the missing
checkpoint as a counted synchronous stop (audit seq 52/53, `counted: true`).

**This is the SAME terminal class as the cycle-2 stop** (max_turns_reached →
missing_checkpoint). Then it was entangled with the resume-path defects; now those are
fixed and live-proven (§1 R352–R356), isolating a distinct structural defect:

> **The fixed 12-turn unit bound makes no reservation for the mandatory checkpoint
> emission, and a fresh-context worker's re-orientation can consume the entire bound.**
> Nothing in the unit design forces early or incremental emission; turn exhaustion
> therefore converts "needed more turns" into a counted unsafe stop.

Secondary observations (recorded, not causal): (a) `native_tools_guidance_appended:
false` — the digest-bound prompt predates M0-T120 on this RESUMED run lineage; the worker
nevertheless routed natively (Grep observed), so guidance absence did not cause the stop.
(b) `provider_session_continuity.context_tokens = 694,251` is CUMULATIVE usage across the
12 turns (repeated cache reads), not live context (~72k) — a metric-semantics note, not a
shed failure. (c) The runner's transitions journaled transactionally at unit end
(claude_process_started recorded at 19:37:48 with the completion) — cosmetic ordering,
chain intact.

## 3. What this attempt PROVED live (first time, all five previously-failed mechanisms)

The M0-T123 repair is live-validated end to end: pre-first-dispatch over-ceiling shed
fired; a genuinely fresh Fable 5 session launched; the worker ran inside the packet
worktree (never the primary checkout); lineage/budgets/audit/exactly-once all carried; and
the T123 seam had earlier fail-closed refused the unbound certified command. Every
protection built in the Amendment-16..19 arc behaved exactly as certified. What failed is
a bound never before reached in isolation.

## 4. Standing state and the NEW owner decision (nothing below is executed or prepared)

Journal at **PAUSED_RECOVERY** (transitions 22, audit 53, 0 asks, 0 effects); owner-touch
measurement now carries a second counted stop; `wt-m0t107` clean at `796e18f`; the
Amendment-20/21 single attempt is **consumed by dispatch**. Options for a NEW owner
decision, none begun: **(A)** a bounded defect task on the unit-turn structure (e.g., a
checkpoint-reserved turn, a raised bound, or an emit-first/incremental-checkpoint unit
design) — touches `tools/agent_supervisor/**` → R247 recertification consequences apply;
**(B)** packet/prompt restructuring only (front-load orientation into the unit prompt so a
fresh worker need not rediscover it) if achievable without supervisor-source change;
**(C)** close this line and hold. The orchestrator recommends nothing is lost by (A)+(B)
together as ONE owner-authorized window, but takes no step without the decision.
