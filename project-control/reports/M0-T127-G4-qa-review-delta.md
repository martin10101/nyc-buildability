# M0-T127 — G4 DELTA report (independent qa-engineer, read-only + read-only pytest) — VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31 by the same independent qa-engineer identity,
re-verdicting the Amendment-24 staged-protocol revision. DELTA VERDICT: PASS — every section
7.1 code claim independently reproduced by grep (zero production callers; plan_close_run at
cli.py:2687; in-process same-task CONTINUE continuation at loop.py:2806/2854); Stage-2 command
parse-validated; all seven R391 contents intact; package-wide consistency sweep found zero
residual single-command-proves-seven claims; the reviewer candidly records that its own prior
PASS missed the contradiction. Non-blocking O1: pre-existing typographic non-ASCII prose in
the activation package (command/hash-safe; candidate normalization follow-up).

---VERBATIM-BEGIN---
All duties complete. Here is my delta re-verdict.

---

# G4 (QA) Delta Re-Verdict — M0-T127 (Amendment-24 staged-protocol revision)

**Task:** M0-T127 (same task; section-7 rewritten as a staged commissioning protocol after Amendment 24 found the single-command contradiction)
**Reviewed identity:** branch tip `8d7096e1adbf74b8082a1471c8895fea8dbb5767`. **Material stability verified:** stabilization report at HEAD == `5d7f958` (empty diff); supervisor code/tests at HEAD == certified `2d46fb0` (empty diff). The rework is report-only.
**Reviewer:** qa-engineer (independent, read-only + read-only pytest). No writes outside `.claude/agent-memory/qa-engineer/`; live journal never opened (R374).

## DELTA VERDICT: PASS — the Amendment-24 correction is code-accurate; the staged protocol maps every fact honestly; no residual contradiction. No new defects (one pre-existing, non-blocking observation).

The revision fixes a real contradiction my own prior M0-T127 PASS did not catch: I verified the two commissioning commands *parse-validated* and flagged the D9 "simulation-only" scope, but I did not connect that a `--max-cycles 1` command therefore *cannot prove* R393 facts 6 and cross-task 7. The external review caught it; my re-verification confirms the correction is substantively right.

## (1) Code claims in §7.1 — verified by my own greps

| §7.1 claim | Verification | Result |
|---|---|---|
| `select_next_packet` / `record_advancement` / `advance_and_select` have ZERO production call sites | Grep across `tools/agent_supervisor/**`: the only references are the three **definitions** in `next_task.py` plus `advance_and_select`'s own **internal** calls to the other two (next_task.py:357/361). No external caller anywhere; `advance_and_select` itself has no caller. | CONFIRMED |
| Only `plan_close_run` is live-wired (cli.py:2687) | Grep `plan_close_run`/`close_after_complete`: single production wiring at `cli.py:2687` (`next_task.plan_close_run(machine.current_state)`); `close_after_complete` has no production caller. | CONFIRMED |
| In-process multi-cycle continuation on CONTINUE exists in loop.py (in-task fact-7 mechanism) | `run()` iterates `for index in range(start_index, max_cycles+1)` (loop.py:2806); on a continuing/forwarded cycle it sets `prompt = result.forward.sent_prompt` (2854) — the reviewed **same-task** forwarded prompt — and drives the next cycle in-process with the between-cycle owner-intent seam as the only stop (2818). It never calls the cross-task selection functions. | CONFIRMED |

The in-task vs cross-task split in the §7.1 fact map is code-accurate: fact 7 in-task is driven by same-task forward continuation (Stage 2, `--max-cycles 3`); facts 6 and cross-task 7 depend on the unwired selection machinery (Stage 3 only); fact 5 is partial at Stage 1 (`plan_close_run` closes to IDLE) and full only with the unwired `record_advancement` (Stage 3). Section 4 limitation 2 restatement matches this exactly.

## (2) Stage-2 command (§7.3) parse-validation

`start … --max-cycles 3 …` via `command_docs.validate_command(build_parser())` → **verb=`start`, ok=True, code=`ok`** (all five pinned load-bearing flags present; `dispatch_inputs_missing` empty). No execution. (The Stage-1 Step-1 `clear-recovery` and Step-2 `--max-cycles 1` commands were already validated OK in my prior M0-T127 gate; they are unchanged.)

## (3) R391 integrity — all seven p8 contents present

Section headers at the revised identity: §1 What was changed · §2 The full end-to-end proof · §3 Every defect found proactively · §4 All remaining limitations · §5 The exact frozen identity · §6 The complete preflight · §7 The STAGED commissioning protocol. The rewrite **staged** §7 but dropped none of the seven required contents. The commissioning-commands content is present (now as Stage-1/Stage-2 commands + the Stage-3 owner-decision options).

## (4) Internal consistency sweep (stabilization + recert + activation package)

**No residual contradiction found.** Every "seven-fact" reference in the stabilization report is properly staged/qualified: line 6 "full autonomy NOT declared from tests/simulations"; line 132 the honest correction ("could not prove all seven … zero production call sites"); line 148 "fact 6 … NOT provable live today … Stage 3 only"; line 186 "ONE seven-fact live journey becomes presentable" only **after** Option A wiring; lines 195-196 "full autonomy declarable ONLY after the complete seven-fact live proof." The old single-attempt framing ("ONE controlled live commissioning attempt", "the live journey must prove … the next bounded task is selected") is fully removed. The recertification report has **zero** hits for any single-command/seven-fact claim. The activation package (M0-T096) correctly defers: "the exact commissioning commands are in `M0-T127-stabilization-report.md` … the live journey remains a SEPARATE [owner step]; seven-fact proof burden; R394 on failure" — no claim that one command proves seven facts, and no readiness-without-Stage-3 claim.

## (5) ASCII

Revised stabilization report: **0 non-ASCII bytes**. (Recert report unchanged, previously verified 0.)

## New findings

- **O1 (non-blocking, pre-existing, out of delta scope):** `M0-T096-activation-package.md` (in M0-T127's allowed_paths but **not** touched by this rework) contains **212 non-ASCII bytes** — typographic punctuation only (45 em-dashes, 8 en-dashes, 6 ellipses, 5 middle-dot bullet separators, 5 section-signs, 5 arrows), all in **prose**. Every executable command token (inside backticks) is pure ASCII — the middle-dot separators sit *between* backtick commands, not inside them; no hash/digest is affected. This is inconsistent with the pure-ASCII discipline of the two authored M0-T127 reports and is a candidate for normalization, but it is pre-existing, command/hash-safe, and does not affect this delta verdict.

No defects. The Amendment-24 rework is an honest, code-accurate strengthening of the package: the contradicted single-command claim is retracted, each R393 fact is mapped to the exact stage/command/wiring that proves it, and cross-task autonomy is correctly gated behind a new owner decision (Stage 3, Options A/B/C) that re-triggers R247.

**Requested gate result:** **PASS** at the revised identity (branch tip `8d7096e`; report content `5d7f958`; certified material `2d46fb0`). Full report captured verbatim as the M0-T127 G4 delta record.

Note for the orchestrator: reviewed via `git checkout --detach 8d7096e` in my own isolated worktree (clean tree restored first; my untracked memory index and a local memory edit were set aside and re-applied). The orchestrator owns this worktree's post-review lifecycle.
---VERBATIM-END---
