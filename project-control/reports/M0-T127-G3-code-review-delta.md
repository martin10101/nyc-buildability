# M0-T127 — G3 DELTA report (independent code-reviewer, read-only) — VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31 by the same independent code-reviewer identity,
re-verdicting the Amendment-24 revision (staged commissioning protocol). DELTA VERDICT: PASS —
the 7.1 seven-fact map verified accurate against the code (zero-caller advancement machinery
re-confirmed; in-process CONTINUE forwarding verified at loop.py:2806-2859), the Stage-2
command validates, 7.4 self-authorizes nothing (R399), the R397 hold is visible at the point
of use, and no residual single-command-proves-all-seven claim remains. Non-blocking O1 (the
recert report's "both commands" wording — corrected by the orchestrator to name all three in
the same control batch as this capture) and O2 (fact-5 partial wording adjudicated honest).

---VERBATIM-BEGIN---
All checks complete. The revision accurately resolves the contradiction I first surfaced (M0-T126 O2). Here is my delta gate report.

---

# G3 (code-reviewer) DELTA Gate Report — M0-T127 (Amendment-24 commissioning revision)

**Task:** M0-T127 — stabilization report §7 rewritten as a staged commissioning protocol + §4 limitation 2 restated (Amendment 24, R397/R398/R399)
**Reviewed identity:** material `2d46fb0` (verified stable: `git diff 2d46fb0 HEAD -- tools/ .github/ docs/…` empty; HEAD `8d7096e`, report-only change). Delta: `git diff 7478100 5d7f958 -- …M0-T127-stabilization-report.md`. Report-only → no modularity/source review.
**Reviewer:** code-reviewer (independent, read-only). All code facts re-verified against the frozen tree.

## DELTA VERDICT: **PASS**

The revision honestly and accurately resolves the real contradiction (which builds directly on my own M0-T126 Observation O2). Every fact in the 7.1 map is correct against the code I re-verified; the Stage-2 command validates; Stage-3 is presented as an owner decision without self-authorization; the R397 hold is visible; and no residual claim that the single `--max-cycles 1` command proves all seven facts remains.

---

## Findings by review point

### 1. 7.1 seven-fact provability map — ACCURATE (re-verified against code)
Root fact re-confirmed at `2d46fb0`: `select_next_packet`/`record_advancement`/`advance_and_select` have **zero production call sites** (`git grep` finds them only inside `next_task.py` itself); the only wired next_task surface is `plan_close_run` at **cli.py:2687**. Per-fact:

| Fact | Map's stage | My verification |
|---|---|---|
| 1 over-ceiling session never contacted | Stage 1 (pre-dispatch shed) | Correct — the launch-seam ceiling shed/fresh-launch path is wired; a fresh Stage-1 start does not resume the parked session |
| 2 fresh worker in wt-m0t107 | Stage 1 | Correct — `evaluate_packet_worktree_binding(wt-m0t107, wt-m0t107, ctl24)` → binds (verified prior gate) |
| 3 valid checkpoint reaches Codex | Stage 1 | Correct — one cycle exercises checkpoint→forward |
| 4 Codex completes review | Stage 1 | Correct — CODEX_REVIEW is within the cycle |
| 5 M0-T107 advances exactly once | **Stage 1 partial / Stage 3 full** | Correct split — unit-close via wired `plan_close_run` (COMPLETE→IDLE on next start); the AUDITED `record_advancement` CAS has no live caller → Stage 3. Honestly labels the partial |
| 6 next bounded task selected | **Stage 3 only** | Correct — `select_next_packet` has zero callers; plainly named not-provable-today (R398) |
| 7 multiple successive units, no owner touch | **Stage 2 in-task / Stage 3 cross-task** | Correct — verified against loop.py:2806-2859: `for index in range(start_index, max_cycles+1)` continues in-process on a CONTINUE forward (`prompt = result.forward.sent_prompt`), between-cycle seams are budget/intent/rotation only (no owner touch in limited-auto). In-task multi-unit at `--max-cycles 3` is real; cross-task correctly deferred to Stage 3 |

The map satisfies R398 (each fact → exact stage/command/wiring; every not-yet-provable fact named plainly with the prerequisite work).

### 2. Stage-2 command (7.3, `--max-cycles 3` sole delta) — VALIDATES
My own `command_docs.validate_command` + `build_parser()`: `verb='start', ok=True, code=ok` → parses, carries all five pinned flags (`--checkout --repo --branch --worktree --max-cycles`), and passes `dispatch_inputs_missing`. The only delta from Stage-1 Step 2 is `--max-cycles 1`→`3`, as stated.

### 3. 7.4 options — ACCURATE scope, NO self-authorization (R399)
- Option A scope is accurate: the machinery (`advance_and_select` + exactly-once CAS + crash matrix) is already built and simulation-proven at this identity (verified in my M0-T126 review); wiring it into the live post-COMPLETE path is a `tools/agent_supervisor/**` change that re-triggers R247 under the supervisor-freeze rule. Correctly stated as "behind the EXISTING bounded-mode owner gate."
- No self-authorization: 7.4 opens "The orchestrator does not self-authorize either path" and presents A/B/C as a NEW owner decision. Option B is "recommended" (advisory ordering only — every stage stays owner-typed; Option A still needs a separate owner decision). "What no option changes" reaffirms R393 (autonomy only after the full seven-fact live proof) and R394. Satisfies R399.

### 4. R397 hold visibility — ADEQUATE
The §7 header states the hold explicitly: "execution HELD under R397 until the owner decides section 7.4," reinforced by the §7 intro (the honest mechanics + "NO currently-presentable command can prove R393 facts 6 and cross-task 7") and by §4 limitation 2 (restated to name the Amendment-24 consequence). The hold is visible at the point of use, not buried.

### 5. Consistency — no residual single-command all-seven claim
The old block ("What the live journey must prove … the next bounded task is selected; multiple successive units …") attached to the single command is **removed** in the delta. Package-wide scan: the remaining "seven fact" mentions are all correct framings — the general R393 requirement (report intro L8, M0-T096 L22), the map heading, Option A's post-wiring "ONE seven-fact live journey becomes presentable," and "full autonomy declarable ONLY after the complete seven-fact live proof." None asserts the `--max-cycles 1` command proves all seven. §2 (end-to-end proof) correctly frames its evidence as tests/simulations (R388 "consecutive **simulated** advancements").

## New findings
- **None blocking.**
- **O1 (minor, non-blocking, cross-report):** `M0-T127-recertification.md` §5 still reads "Both presented commissioning commands … were dry-run validated" — the revised package now presents **three** (`clear-recovery`, Stage-1 `--max-cycles 1`, Stage-2 `--max-cycles 3`). The recert report was outside this revision's scope, and I independently validated all three commands (all `ok`), so the substance holds; recommend updating the recert §5 count to match the staged package. Non-blocking.
- **O2 (nuance, non-blocking):** fact 5's Stage-1-partial rests on "the unit completes and the run closes via plan_close_run" — a deliberately weaker claim than campaign "advancement," which the map correctly defers to Stage 3. The wording "advances exactly once … PARTIAL at Stage 1" is honest given the explicit Stage-3 deferral of the audited record; no change required.

---

**Requested gate result: PASS.** The Amendment-24 revision mechanically and honestly resolves the commissioning contradiction: the 7.1 map is accurate against the verified code (zero-caller advancement machinery, wired `plan_close_run`, in-process CONTINUE forwarding at loop.py:2806-2859), the Stage-2 command validates, Stage-3 is an owner decision with no self-authorization, and the R397 hold is visible. Commands run (all read-only): `git diff/rev-parse/grep`, `command_docs.validate_command`+`build_parser()` on the Stage-2 command, and a package-wide consistency grep. I made no writes outside `.claude/agent-memory/code-reviewer/` and ran no `project_control.py`/git-write/`gh`/supervisor write verb.
---VERBATIM-END---
