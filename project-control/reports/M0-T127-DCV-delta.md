# M0-T127 — DCV rounds 2+3 (Amendment-24 delta + clearance; independent directive-compliance-verifier, read-only) — VERBATIM agent returns (transport entity-decoding only)

Orchestrator capture note: two returns from the same independent DCV identity, 2026-08-31.
ROUND 2 (delta on R397/R398/R399 + R391/R392 re-check) verified all five rows' substance on
primary evidence but correctly REFUSED completion on two blocking items: (1) the validator
failed closed at HEAD on the orchestrator's invalid R399 classification metadata
(`owner_decision` not in the enum — an orchestrator capture error, fixed to `decision` with
an audit-log entry at `a15e595`, validator back to EXIT 0); (2) the G3/G4 delta verdicts were
not yet on file at the revised identity (both subsequently recorded PASS at `9b39f49` /
`a15e595`). ROUND 3 confirmed both items cleared and issued the final verdict: **25/25 rows
SATISFIED** (round-1 22 rows + delta rows), material identity unmoved at `2d46fb0`, ready for
verification.json + accept. Round-2 verbatim, then round-3 verbatim, below. Round 1 is in
`M0-T127-DCV.md`.

---VERBATIM-ROUND-2-BEGIN---
I have all the evidence. Journal unchanged (PAUSED_RECOVERY/22/53, PR #241 OPEN untouched — R397/R392 confirmed); all seven R391 contents intact after the rewrite; the zero-caller claim independently verified. Two blocking items surfaced. Here is my round-2 delta DCV record.

---

# DCV REPORT — Task M0-T127 ROUND 2 (D-024 Amendment 24 delta; rows R397/R398/R399 + R391/R392 re-check)

## VERDICT: **NOT ALL-PASS** — the five rows' deliverable substance is verified PASS on primary evidence, but the round-2 set cannot be certified complete due to **two blocking items**: (1) registry-integrity validator **FAILS** at HEAD on the R399 classification; (2) the R397 independent-review clause is **PENDING** (no G3/G4 delta verdict at the revised identity yet). My round-1 record (22 rows, all SATISFIED) stands for what it examined.

**Identity:** material `2d46fb0` still UNMOVED (`git diff 2d46fb0 HEAD -- tools/ .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` EMPTY — the Amendment-24 resolution is mechanical/report-only, no supervisor code change, consistent with R399's "wiring is a NEW owner decision"). HEAD = `8d7096e`; revised submit `reviewed_sha 5d7f958`. Delta diff `7478100 5d7f958` touches only registry files + reports/state/task (no code).

## Delta verdict table

| Req | Verdict | Primary evidence reproduced |
|---|---|---|
| **R397** (hold + mechanical resolution + review) | **SATISFIED (substance) — CONDITIONAL on pending G3/G4 delta** | Hold stated: stabilization §7 header (L128) "execution HELD under R397 until the owner decides section 7.4." Resolution is mechanical: §7.1 maps facts from verified code (zero-caller claim, below) and honestly re-scopes each command via a staged protocol. NO command executed: LIVE journal re-checked = `PAUSED_RECOVERY`, transitions **22**, audit **53**, effects/outbox/inbox **0**. Review clause: this delta round IS the required review, but **G3/G4 delta verdicts at the revised identity are NOT yet on file** (gate records still `reviewed_sha` 361c8d1/0df2744 from round 1; no round-2 delta reports). Per your instruction, R397 verification is **conditional on the G3/G4 delta PASS at `5d7f958`/`8d7096e`**. |
| **R398** (seven-fact mapping) | **SATISFIED** | §7.1 maps all seven R393 facts to stage/command/wiring. Zero-caller claim **independently reproduced**: `grep` over `tools/agent_supervisor/*.py` shows `select_next_packet`, `record_advancement`, `advance_and_select` have **ZERO production call sites** (only next_task.py definitions + 1 test file each); `plan_close_run` is wired at **cli.py:2687** (`_close_plan = next_task.plan_close_run(...)`). In-process CONTINUE forwarding for fact-7-in-task confirmed in `loop.py` (FORWARD_PROMPT state family, "EXACTLY-ONCE FORWARDING", next-unit launch). Unprovable facts named plainly WITH prerequisites: fact 5 "PARTIAL at Stage 1 / full needs Stage-3 wiring"; fact 6 "NOT provable live today — select_next_packet has zero production call sites; requires Stage-3 wiring"; fact 7 "in-task Stage 2 / cross-task Stage 3 only." |
| **R399** (owner-decision boundary) | **SATISFIED (report substance) — but registry-row classification defect blocks the validator (Disc. 1)** | §7.4 presents Option A (wire live dispatch → re-triggers R247), Option B (de-risk live first, recommended), Option C (hold). L179 "The orchestrator does not self-authorize either path." Grants no new authority; orchestrator executes nothing. **However** the R399 *registry row* has `classification="owner_decision"`, which is NOT in the allowed enum — this fails `validate_directive_compliance.py` (see Disc. 1); the deliverable's compliance with the owner instruction is sound, but the registry metadata is malformed. |
| **R391** (seven p8 contents, re-check) | **SATISFIED** | All seven `## ` section headers present after the rewrite: §1 what was changed, §2 full end-to-end proof, §3 every defect found proactively, §4 all remaining limitations, §5 exact frozen identity, §6 complete preflight, §7 the exact commissioning commands (now staged: Stage-1 Step 1/Step 2 give the exact commands). Content 7 (exact commands for a controlled live attempt) is preserved. |
| **R392** (owner-typed only / parse-only / journal unchanged, re-check) | **SATISFIED** | Header L5 "the orchestrator never executes them (R392)"; §7 header "OWNER-TYPED ONLY — the orchestrator NEVER runs any of these, R392." Commands dry-run validated (parse-only) per §7.2 L153-154. Journal unchanged (PAUSED_RECOVERY/22/53/0); PR #241 **OPEN**, updatedAt 2026-08-20 (untouched). No supervisor start/clear-recovery verb ran. |

## Item 6 — Amendment-24 registry integrity: **FAIL**

`python tools/validate_directive_compliance.py --check` → **exit nonzero**:
```
directive registry INVALID (1 error(s)):
  - c1 [D-024] D-024-R399 unknown classification 'owner_decision'
```

## Discrepancies (numbered)

1. **[BLOCKING] R399 registry row uses an invalid classification `owner_decision`.** The allowed classification enum — identical in `tools/validate_directive_compliance.py:445-447` and `project-control/directives/schema/v1/directive_requirements.schema.json:28-29` — is `{obligation, prohibition, hold, sequencing, dependency, decision, harness, evidence, external_fact, return, authorization}`. `owner_decision` is not in it; a valid `decision` classification already exists and is used by 3 other rows. This makes the validator FAIL CLOSED at HEAD, so your explicit item-6 check ("validator --check EXIT=0 at the new HEAD") is **not** met, and the CI-wired integrity gate is red. **Orchestrator fix required** (read-only reviewer cannot edit): change the R399 row `classification` from `owner_decision` to `decision` (or version-bump the schema+validator enum to admit `owner_decision`), append a `manifest.audit_log` entry, and re-run `--check` to EXIT 0. R399's *deliverable* substance is unaffected and already PASS; this is a registry-metadata defect only.
2. **[PENDING] G3/G4 delta reviews at the revised identity are not yet on file.** `project-control/gates/M0-T127-G3.json` / `-G4.json` still record `reviewed_sha` 361c8d1 / 0df2744 (round-1 identity); no `M0-T127-*delta*` round-2 gate reports exist. R397's "independently reviewed" clause is therefore satisfied only once the G3/G4 delta verdicts land PASS at `5d7f958`/`8d7096e`. My R397 verdict is conditional on that.
3. **(Non-blocking, informational)** The material supervisor identity did not move (empty diff), so the round-1 verdicts for the 20 carry-over rows (R372-R382, R385-R390, R393, R394, R396) remain valid; Amendment 24 changed only the section-7 presentation and added R397-R399. My round-1 checks of R391/R392 re-confirm cleanly against the rewritten section 7.

## Exact commands run (read-only)

- `git rev-parse HEAD` → `8d7096e`; `git diff 2d46fb0 HEAD -- tools/ .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` (empty); `git merge-base --is-ancestor 5d7f958 HEAD` (yes); `git log --oneline 7478100..HEAD`; `git diff --stat 7478100 5d7f958`.
- `grep -rn` for `select_next_packet` / `record_advancement` / `advance_and_select` / `plan_close_run` across `tools/agent_supervisor/*.py` (zero production callers for the first three; `plan_close_run` at cli.py:2687) and `tools/test_*.py` (1 file each).
- `grep -niE` CONTINUE/FORWARD_PROMPT/next-unit in `loop.py`.
- `python tools/validate_directive_compliance.py --check` → **exit nonzero** (R399 `owner_decision` unknown classification).
- Read-only sqlite (`mode=ro&immutable=1`): PAUSED_RECOVERY / transitions 22 / effects,outbox,inbox 0; `wc -l audit.jsonl`=53; `gh pr view 241` → OPEN / 2026-08-20.
- `Read` of source-024-amendment.md, revised stabilization-report §1-§7, requirements.json R397-R399, validator + schema enum.

No writes outside my agent-memory scope; no `project_control.py`/git-write/`gh`-write/supervisor-write verb; live journal opened read-only only.

**Recommendation to orchestrator:** do NOT record the 25-row set as complete yet. First (a) fix the R399 classification so `validate_directive_compliance.py --check` returns EXIT 0, and (b) obtain the G3/G4 delta PASS at the revised identity. Once both land, R397 becomes unconditionally SATISFIED and R398/R399/R391/R392 stand as verified here — completing the 25-row set together with my round-1 record (`project-control/reports/M0-T127-DCV.md`).
---VERBATIM-ROUND-2-END---

---VERBATIM-ROUND-3-BEGIN---
Both round-2 blocking items are fully cleared and both delta reviews are genuine, independent, and corroborate my own findings. Here is my final clearance verdict.

---

# DCV REPORT — Task M0-T127 ROUND 3 (clearance of Amendment-24 delta blockers)

## VERDICT: **ALL PASS — 25/25 rows SATISFIED. Both round-2 blocking items are CLEARED. Ready for the orchestrator to write `verification.json` and accept. Nothing blocks.**

**Identity:** HEAD = `67fc23f`; material `2d46fb0` **still UNMOVED** (`git diff 2d46fb0 HEAD -- tools/ .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` EMPTY). Commits `8d7096e..HEAD` are all control-plane (classification metadata fix + gate re-records); no supervisor code changed.

## Clearance checks

| Item | Result | Primary evidence |
|---|---|---|
| (a) Validator EXIT 0 at HEAD | **CONFIRMED** | `python tools/validate_directive_compliance.py --check` → **exit 0**. R399 `classification` is now `"decision"` (valid enum member), fixed from `owner_decision` in commit `a15e595`. My round-2 Disc. 1 is resolved. |
| (b) G3 delta record + report | **CONFIRMED PASS** | `gates/M0-T127-G3.json`: result=PASS, reviewed_sha=`9b39f49`, report=`M0-T127-G3-code-review-delta.md` (8106 B, exists). Genuine independent review: re-verified 7.1 map, zero-caller claim by git grep, in-process CONTINUE forwarding at loop.py:2806-2859, Stage-2 validates, 7.4 no self-authorization, R397 hold visible, no residual single-command all-seven claim. |
| (b) G4 delta record + report | **CONFIRMED PASS** | `gates/M0-T127-G4.json`: result=PASS, reviewed_sha=`a15e595`, report=`M0-T127-G4-qa-review-delta.md` (7665 B, exists). Genuine independent QA: own greps confirm zero production callers + plan_close_run@cli.py:2687 + CONTINUE continuation loop.py:2806/2854; Stage-2 parse-validates; seven R391 contents intact; consistency sweep = zero residual contradiction. |
| Delta reviews saw the revised content | **CONFIRMED** | Revised stabilization report is byte-stable `5d7f958..HEAD` (empty diff); `5d7f958` is an ancestor of both review SHAs (`9b39f49`, `a15e595`). Both reviewers examined the staged §7. |
| (e) Material identity unmoved | **CONFIRMED** | supervisor-path diff `2d46fb0 HEAD` empty; both delta reports independently re-verified this. |

## Updated verdicts for the Amendment-24 rows

- **R397** → now **SATISFIED (unconditional).** Hold stated (§7 header "execution HELD under R397"); mechanical resolution (7.1 map verified against code); no command executed (journal `PAUSED_RECOVERY`/22/53 — re-confirmed round 2, identity unmoved since); **AND independently reviewed** — G3 + G4 delta PASS now on file at the revised identity. The round-2 conditionality is discharged.
- **R398** → **SATISFIED** (unchanged): zero-caller claim independently reproduced; each of the seven R393 facts mapped to stage/command/wiring; unprovable facts (5-full, 6, cross-task 7) named plainly with prerequisites. Both delta reviewers independently reproduced the same code facts (incl. loop.py:2806-2859).
- **R399** → now **SATISFIED (without reservation).** Report substance (Options A/B/C presented, "orchestrator does not self-authorize either path", no new authority) was already sound; the registry classification defect is fixed (validator EXIT 0). Both concerns closed.
- **R391 / R392** (re-check post-rewrite) → **SATISFIED** (unchanged): all seven p8 contents present after the staged rewrite; commands OWNER-TYPED ONLY, parse-only validation, journal unchanged.

## Complete 25-row set status

- **Round-1 (22 rows: R372–R382, R385–R394, R396):** ALL SATISFIED at material `2d46fb0` — captured verbatim as `project-control/reports/M0-T127-DCV.md`; verdicts stand (identity unmoved).
- **Round-2/3 delta (R397, R398, R399):** ALL SATISFIED; R391/R392 re-confirmed against the rewritten §7.
- **Total: 25/25 SATISFIED.** No VIOLATED, no UNVERIFIABLE, no BLOCKING discrepancy remaining.

## Residual non-blocking observations (do not block acceptance)
1. G3 O1 (recert §5 "both commands" wording → three) — recorded fixed in commit `9b39f49`; non-blocking.
2. G4 O1 — 212 non-ASCII typographic bytes in `M0-T096-activation-package.md` prose (all command/hash tokens are pure ASCII; command/hash-safe); pre-existing, candidate normalization follow-up; non-blocking.

## Commands run (read-only)
- `git rev-parse HEAD` (`67fc23f`); `git diff 2d46fb0 HEAD -- tools/ .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` (empty); `git diff 5d7f958 HEAD -- …stabilization-report.md` (empty); `git merge-base --is-ancestor` (5d7f958→9b39f49/a15e595 yes; a15e595/9b39f49/67fc23f→HEAD yes); `git log --oneline 8d7096e..HEAD`.
- `python tools/validate_directive_compliance.py --check` → **exit 0**; Python check of R399 classification (`decision`).
- Read of `gates/M0-T127-G3.json`/`-G4.json` and both delta report files.

No writes outside my agent-memory scope; no `project_control.py`/git-write/`gh`-write/supervisor-write verb.

**Recommendation:** the orchestrator may now write `verification.json` for the 25-row applicable set (round-1 `M0-T127-DCV.md` + this round-2/3 delta record) and proceed to `accept()` M0-T127. The Amendment-22/24 window is DCV-complete: M0-T126 PASS (18/18), M0-T127 PASS (25/25), all at the one frozen material identity `2d46fb0`, with the commissioning package HELD owner-only under R397 and no autonomy declared from simulations.
---VERBATIM-ROUND-3-END---
