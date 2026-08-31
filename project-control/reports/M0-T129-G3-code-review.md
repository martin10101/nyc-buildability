# M0-T129 - G3 report (independent code-reviewer, read-only) - VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31. VERDICT: PASS with 1 blocking correction + 2
minor notes, all report-only: C1 the commissioning protocol's fact-6 row cited
select_next_packet as the live mechanism when the actual wired selection is run_task_queue's
ordered-queue iteration + evaluate_eligibility + is_advanced (select_next_packet retains zero
production callers) - the exact Amendment-24 accuracy class, to be corrected before
presentation; N1 add the category-2 task_id-match prerequisite; N2 the "is clean" wording
overstates the eligibility engine (git-cleanliness is preparation/preflight, not an
eligibility category). Everything else reproduced: golden 42/42 in 41.27s (reviewer's own
run), suite collection 3037=3035+2, chain arithmetic, CLI identity exact, tooth 12/0,
modularity 0, both commands validate, queue format exact match, preservation intact, the
activation-package refresh accurate WITHOUT the C1 slip (isolated, not systemic).

---VERBATIM-BEGIN---
All reproductions complete. The M0-T096 seventh refresh is accurate (and notably describes the wiring correctly without citing `select_next_packet`, confirming the fact-6 citation is an isolated slip). Here is my gate report.

---

# G3 (code-reviewer) Gate Report - M0-T129 (Amendment-25 terminal recert + seven-fact commissioning protocol)

**Task:** M0-T129 - R247 recert at the post-wiring identity + R407 commissioning protocol (D-024 Amendment 25, R406-R409)
**Reviewed identity:** material `de18f27` (verified stable: `git diff de18f27 HEAD -- tools/ .github/ docs/...` empty; HEAD `9e60d05`). Report-only task (3 files) -> no modularity/source review.
**Reviewer:** code-reviewer (independent, read-only). Producer is `orchestrator-recert-runner`, so **every number below is my own reproduction or cross-check**.

## VERDICT: **PASS with 1 required correction (blocking for acceptance) + 2 minor accuracy notes**

The recert reproduces cleanly, preservation holds, and the commissioning protocol is honest about R409/R394/standing gates. **One blocking correction:** the seven-fact table's **fact-6 mechanism citation names `select_next_packet` as "now LIVE in `run_task_queue`," but `select_next_packet` has zero production callers** - the live selection is `run_task_queue`'s inline ordered-list iteration + `evaluate_eligibility` + `is_advanced`. This is precisely the `select_next_packet`-caller-status inaccuracy that triggered Amendment 24, so the R407 deliverable must state it accurately.

---

## Deliverable 1 - `M0-T129-recertification.md` - reproduces

| Claim | My reproduction | Result |
|---|---|---|
| `de18f27:tools/agent_supervisor` tree `b392100930bd...` | `git rev-parse` -> `b392100930bd4213cab90eb02aafa6d0d568f849` | **MATCH** |
| Golden pack blob `deeca07b` unchanged | `git rev-parse de18f27:...golden_run.py` -> `deeca07b...` | **MATCH** |
| Golden 42/42 sub-minute | my `pytest ...golden_run.py -q` -> **42 passed in 41.27s** | **CONFIRMED** (report 51.32s; both sub-minute) |
| Whole suite **3,035** passed / 2 skipped | `--collect-only` -> **3037 collected** (= 3035 + 2 skip) | **CONFIRMED** |
| Chain 2,990 + 35 + 10 = 3,035 | arithmetic + collection | **CONFIRMED** |
| cross-task **45 passed** | reproduced in my C1/C2 delta (45) | **MATCH** |
| CLI identity `d6f6c29a8ac6b3cf...`, 217,360,032 B | `executable_identity` -> digest `d6f6c29a8ac6b3cf`, size `217360032` | **EXACT MATCH** |
| tooth 12/0 | reran -> **exit 0** | **MATCH** |
| modularity 0 failures | reran -> selected 335 files; **failures 0** | **MATCH** |

Not independently reproduced (orchestrator-captured; write/network/provider): manifest 125-files digest `841ed11c`, verify-controller/doctor PASS, CI green, PR #241 untouched - flagged as orchestrator-captured evidence.

## Deliverable 2 - `M0-T129-commissioning-protocol.md`

**(a) Seven-fact table code-accuracy:** facts 1-5 and 7 citations are accurate against the code I reviewed - fact 3 (orientation/sized-turns/reserved-turn injection, M0-T126 OK), **fact 5** (`record_advancement` CAS advance-before-select - verified at next_task.py:855, called before the next iteration's selection OK), fact 7 (in-task CONTINUE forwarding at loop.py:2806-2859 + cross-task `run_task_queue` under `--max-tasks` OK). **Fact 6 is INACCURATE (-> Required Correction C1):** it cites "`evaluate_eligibility` + `select_next_packet` - now LIVE in `run_task_queue`," but `run_task_queue` (lines 807-867) does **not** call `select_next_packet` (grep confirms `select_next_packet` appears only inside `next_task.py` docstrings and its own body / `advance_and_select`, neither of which the driver invokes - it remains a **zero-production-caller** function). `evaluate_eligibility` **is** live; the live selection is the ordered-list iteration + `is_advanced` skip. The functional claim (fact 6 provable) is TRUE, but the named mechanism is not the wired one.

**(b) Dry-run of both section-4 commands (my own `command_docs.validate_command` + `build_parser()`):** Step 1 `clear-recovery` -> `ok=True, code=ok`; Step 2 `start ... --max-cycles 3 --max-tasks 3 --packet-queue ...` -> `verb=start, ok=True, code=ok` (all five pinned flags + the two new flags present; `dispatch_inputs_missing` empty).

**(c) Queue-file format vs `load_task_queue` (next_task.py:461):** the doc's `{"tasks":[{"task_id","packet_path","worktree","branch","repo"}...]}` matches exactly - `load_task_queue` requires an object with a list `tasks`, each mapped by `TaskQueueEntry.from_mapping` reading those five fields. **MATCH.**

**(d) Per-successor prerequisites vs the eleven eligibility categories - 2 minor notes:** the list covers cats 1 (packet parses), 3 (status `claimed`), 4a/4b (blockers/owner-gate), 5a/5b (dependency accepted), 6a/6b/6c (worktree exists/not-primary/binds), 7 (content unchanged). It **omits category 2** (queue entry `task_id` must match the packet's own `task_id`, enforced at next_task.py:578) and lists "**is clean**" (worktree git-cleanliness), which `evaluate_eligibility` does **not** enforce (it checks `os.path.isdir` + not-primary + launch-seam binding, not git-cleanliness). Minor accuracy fixes.

**(e) No-execute + R394 + standing gates:** the header states "the orchestrator never executes any command below (R409)"; the R394 failure protocol (stop without retry, preserve, one assessment) and the standing gates (never merge PR #241; autostart/canary/Telegram/production/credentials/legal owner-only) are present. No autonomy claim beyond the owner-run journey. **PASS.**

**(f) Command facts:** `wt-m0t107` branch `task/M0-T107-plugin-portability` OK, repo = nyc-development-feasibility-claude-pack OK, operative `project-control/tasks/M0-T107.json` status=**claimed**, worktree=**wt-m0t107** OK. **MATCH.**

## Deliverable 3 - `M0-T096` seventh refresh - accurate, no overclaim

Item 10 "SEVENTH refresh at M0-T129" cross-checks with every reproduction (de18f27, tree b3921009, golden deeca07b, CLI d6f6c29a, suite 3035/2, tooth 12/0, journal PAUSED_RECOVERY/22/53). It states "All seven R393 facts are now provable by ONE owner-typed command ... the orchestrator never executes it (R409); the live journey remains the owner's decision (R393/R394)" - no overclaim. Prior history intact (the M0-T127 sixth refresh preserved as "10-prior-b"). Notably, this refresh describes the wiring correctly ("`run_task_queue` ... eleven-category fail-closed eligibility; audited exactly-once CAS advancement BEFORE selection") **without** citing `select_next_packet` - confirming C1 is an isolated slip in the commissioning protocol, not systemic. **PASS.**

## Deliverable 4 - R401/R403 preservation (my own read-only reads)

Journal sqlite (`mode=ro&immutable=1`, no mutation): `current_state="PAUSED_RECOVERY"`, `transitions`=**22**, `effects`/`inbox`/`outbox`=**0**; `audit.jsonl`=**53** records; `wt-m0t107` clean at `796e18f`. R403: no supervisor-path change in-window (material stable de18f27->HEAD). PR #241 non-merge is orchestrator-attested (not gh-verifiable by a read-only reviewer). **PASS.**

## Required correction (blocking) + minor notes
- **C1 (blocking):** Commissioning-protocol section 1 fact-6 must cite the **actual** live selection mechanism - `run_task_queue`'s ordered-queue iteration + `evaluate_eligibility` + `is_advanced` skip (record_advancement drives exactly-once) - and **not** `select_next_packet`, which has zero production callers even after the M0-T128 wiring. This restores the R407/R408 code-accuracy the owner has been sensitive to (the exact class of claim that triggered Amendment 24).
- **N1 (minor):** section 3 per-successor prerequisites should add category 2 (queue `task_id` must equal the packet's own `task_id`).
- **N2 (minor):** section 3 "is clean" is not enforced by `evaluate_eligibility` (worktree git-cleanliness is a preflight/first-task check, not a per-successor eligibility category) - reword to avoid implying the eligibility engine checks it.

---

**Requested gate result: PASS with 1 blocking correction (C1) + 2 minor notes (N1/N2).** The R247 recert reproduces at the frozen identity `de18f27` (golden 42/41.27s, suite 3035, CLI/tooth/modularity/preservation all verified), the commissioning commands validate, and the package honors R409/R394/standing gates - but the fact-6 `select_next_packet` citation must be corrected to the actual wired mechanism before the R407 package is accepted/presented. All three fixes are report-only (no material identity change). I made no writes outside `.claude/agent-memory/code-reviewer/` and ran no `project_control.py`/git-write/`gh`/supervisor write verb; my journal read created no side-files.
---VERBATIM-END---
