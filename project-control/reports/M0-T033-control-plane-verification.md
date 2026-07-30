# M0-T033 — INDEPENDENT CONTROL-PLANE VERIFICATION REPORT

> **Orchestrator preservation note.** The body below is the `control-plane-verifier` return
> preserved **VERBATIM** per `.claude/rules/project-control.md` (report-preservation rule), with
> transport entity-decoding only (`&lt;`/`&gt;`/`&amp;` restored to `<`/`>`/`&`). Nothing else was
> added, removed, condensed, or reworded. The reviewer was dispatched read-only on explicit Opus 5
> under the D-004-R307 availability exception and made no writes.
>
> Orchestrator disposition of its four corrections is recorded separately in the M0-T033 progress
> log and in `M0-T033-G3-report.md` / `M0-T033-G5-report.md`; this file is the reviewer's own words.

---

**Task:** M0-T033 — Governance-orchestrator unblock-roster semantics
**Reviewer:** `control-plane-verifier` (independent; read-only)
**Model actually running:** Claude **Opus 5 (1M context)**, exact model ID `claude-opus-5[1m]`, dispatched under the D-004-R307 availability exception. No Fable 5 or Opus 4.8 involved.
**Producer:** `backend-engineer` (verified independently — see §3)
**Reviewed identity:** `1e86cd74cc0f80bd1c2bd238e088b11640b1f2a0`
**Branch:** `task/M0-T033-unblock-roster-semantics`; merge-base with `main` = `abb89b821d3cb7beacc916784c92c9d5570122e0`

## VERDICT: **PASS — with two BINDING required corrections (C1 mandatory pre-merge, C2 pre-acceptance)**

The control-plane correction itself is sound. It does not weaken any lifecycle invariant, creates no path to `accepted` without an independent gate, and its execution-proof mechanism is genuine. Two evidence-record defects were found: one is a **latent acceptance blocker** (§10 D-1) and must be fixed before merge. Neither changes the reviewed content identity, so neither invalidates this review.

---

## 1. SHA CONFIRMATION — **CONFIRMED**

```
$ git rev-parse HEAD
1e86cd74cc0f80bd1c2bd238e088b11640b1f2a0

$ git branch --show-current
task/M0-T033-unblock-roster-semantics
```

Matches the frozen reviewed identity. Proceeded.

Branch composition (6 commits above `abb89b8`):
```
1e86cd7 M0-T033 lifecycle: submitted to awaiting_gate at frozen identity 8fd0019
8fd0019 M0-T033: resolver-derived evidence map (52 applicable requirements)
6592b89 M0-T033: correct invalid_unblock_roster for orchestrator-produced governance tasks
4da0d52 M0-T033: record orchestrator containment review + rework cycle 1 in the ledger
836daef D-004 amendment 10 (R410-R420): evidence + review requirements for M0-T033
170478e M0-T033 lifecycle: G0 readiness PASS (administrative); claimed by backend-engineer
```

---

## 2. LIFECYCLE LEGITIMACY OF M0-T033 ITSELF — **CONFIRMED**

**2.1 Ordering: G0 before claim — CONFIRMED (two independent proofs).**
`project-control/gates/M0-T033-G0.json`: `reviewer="orchestrator"`, `role="administrative"`, `result="PASS"`, `reviewed_at="2026-07-30T15:39:03.226045+00:00"`, `reviewed_sha="abb89b8…"`. The task file's post-claim `updated_at` is `15:39:03.954249` — 728 ms later. Structurally, the ordering could not be otherwise: `CLAIMABLE_STATUSES = {"ready","rework"}` (`tools/project_control.py:134`) and the packet was created at `status="backlog"`; only a `G0` PASS moves `backlog → ready` (`gate()`, line 941-943). A claim before G0 is unreachable.

**2.2 Claimed by a real non-orchestrator producer — CONFIRMED.**
`producer_agent = "backend-engineer"` ≠ `"orchestrator"`. `.claude/agents/backend-engineer.md` EXISTS. The G0 gate at the moment of recording had `producer = None`, so `gate()`'s administrative self-approval guard (`if producer and producer == a.reviewer`) was satisfied honestly, not bypassed.

**2.3 No hand-set lifecycle state — CONFIRMED, by byte-level proof.**
`save()` (line 165-184) serializes with `json.dumps(data, indent=2)`. I re-serialized every committed version of the task file and compared bytes:

```
2a56e18 serializer-identical: False | first-line indent: 1
170478e serializer-identical: True  | first-line indent: 2
4da0d52 serializer-identical: True  | first-line indent: 2
1e86cd7 serializer-identical: True  | first-line indent: 2
```

Reading: at the **contracting** commit (`2a56e18`, on `main` via PR #131) the packet body was hand-authored (1-space indent) — structurally necessary, because `new_task()` cannot author `objective`/`inputs`/`acceptance_scenarios`/`allowed_paths` (line 580 sets `"acceptance_scenarios": []`). Its **lifecycle fields at that point were exactly the CLI defaults**: `status="backlog"`, `producer_agent=null`, `progress_percent=0`. From the moment the CLI took over, **every** version is byte-identical to `project_control.save()` output — i.e. no hand-edit occurred after contracting.

Non-lifecycle packet content digest (all keys except `status`/`producer_agent`/`progress_percent`/`updated_at`/`progress_log`):
```
2a56e18 f520c1fdad2304679b0682671c3d068a
170478e f520c1fdad2304679b0682671c3d068a
4da0d52 f520c1fdad2304679b0682671c3d068a
1e86cd7 f520c1fdad2304679b0682671c3d068a
```
The packet was **never amended** after contracting. No scope was widened mid-flight.

**2.4 Transition legality — CONFIRMED.**
`backlog →(G0 PASS)→ ready →(claim)→ claimed →(progress, message-only, 55%)→ claimed →(submit)→ awaiting_gate @85%`. Every step is legal under `PROGRESS_TRANSITIONS` (line 101-112), `CLAIMABLE_STATUSES`, and `SUBMITTABLE_STATUSES` (`claimed` is submittable, line 135). `progress` at 55% is within the `0 <= percent <= 99` bound. `awaiting_gate` was set by `submit()`, not by `progress` — correct.

**2.5 Only the authorized gate exists (D-004-R418) — CONFIRMED.** `ls project-control/gates/ | grep M0-T033` returns exactly `M0-T033-G0.json`. No premature G2/G3/G5 record.

**2.6 Directive-regime records — CONFIRMED.** The D-004 `verification.json` row for M0-T033 is `"state": "pending"` with `verified_at`/`verified_by`/`reviewed_sha` all `null`. No verification is claimed. `accept()` therefore cannot pass yet (`_directive_accept_reasons` → `task_unresolved_requirements`). Correct.

---

## 3. REVIEWER INDEPENDENCE — **CONFIRMED**

| Role | Identity | Distinct from producer? | Agent def exists? |
|---|---|---|---|
| producer | `backend-engineer` | — | EXISTS |
| reviewer | `code-reviewer` | YES | EXISTS |
| reviewer | `security-reviewer` | YES | EXISTS |
| reviewer | `control-plane-verifier` (me) | YES | EXISTS |
| reviewer | `directive-compliance-verifier` | YES | EXISTS |

All four reviewers are distinct from the producer and from each other. `"orchestrator"` does **not** appear in `reviewer_agents` — so `gate()`'s reserved-identity refusal (line 887-891) is never even reached for this task.

I did not produce any part of this work. I independently corroborated the producer's identity from the producer worktree itself: `.claude/worktrees/agent-af94933c3b313bae5` carries modifications only under `.claude/agent-memory/backend-engineer/` — the producer's own memory namespace.

**G2 is not counted as an independent gate — CONFIRMED by code, not by assertion.** `INDEPENDENT_GATES = frozenset({"G1","G3","G4","G5","G6"})` (line 117); `SELF_CHECK_GATES = frozenset({"G2"})` (line 115). `accept()` applies the role/reviewer independence checks only under `if g in INDEPENDENT_GATES` (line 995) and explicitly rejects a `self_check` record offered for an independent gate (line 997-999). M0-T033's independent gates are **G3 and G5** only. The G0 already on file is `role="administrative"` and satisfies no independent requirement — the G0 readiness report says so in its own words ("It is **not** an independent review and satisfies no independent-gate requirement").

---

## 4. THE GUARD CHANGE, FROM A CONTROL-PLANE STANDPOINT — **CONFIRMED SOUND**

**4.1 The four conditions are structurally conjunctive, and condition 3 is a *precondition*, not an alternative.**
The final `invalid_unblock_roster` (`tools/project_control.py:700-751`) evaluates in this order:

1. `producer_agent` non-string → refuse (new; fail-closed).
2. empty producer → refuse (preserved).
3. `_roster_strings(reviewer_agents)` malformed → refuse (new; fail-closed).
4. no usable reviewer (non-empty, ≠ orchestrator, ≠ producer) → refuse (preserved).
5. **only then** `if producer == RESERVED_ORCHESTRATOR: return _orchestrator_governance_exception(task)` (lines 748-749).

Because step 5 is placed *after* step 4, an orchestrator-produced task must already have satisfied the usable-independent-reviewer test before the exception is even consulted. This is the single most important structural property, and it is correct. `_orchestrator_governance_exception` then requires `task_type.strip() == GOVERNANCE_TASK_TYPE` **and** `set(gates) & INDEPENDENT_GATES` non-empty. All four conditions are AND-ed by control flow; there is no OR path.

**4.2 No path to `accepted` without an independent gate — CONFIRMED by tracing `gate()` and `accept()`.**
Both functions are **byte-unchanged**. `git diff -U0 --function-context abb89b8 HEAD -- tools/project_control.py` yields exactly three hunks:
```
@@ -28,16 +28,19 @@ GATE CLASSES (structural; no bypass flag exists)      [module docstring]
@@ -124,0 +128,6 @@ RESERVED_ORCHESTRATOR = "orchestrator"                 [new constant]
@@ -639,29 +648,103 @@ def claim(a):                                     [region after claim(); the guard]
```
`gate()` (line 859), `submit()` (line 811), `accept()` (line 974), `_directive_accept_reasons` (line 462), `_task_git_identity` (line 319) — **no diff hunk**. `claim()`'s body (606-645) is unchanged; the third hunk's `def claim(a)` label is git's nearest-preceding-function attribution for lines 648+, not a change to claim.

The invariant chain that closes the loophole:
- The exception requires ≥1 element of `required_gates` in `INDEPENDENT_GATES`.
- `accept()` (line 990-1005) demands a **PASS** record for **every** required gate, and for gates in `INDEPENDENT_GATES` demands `role != "self_check"`, `role in {None, "independent_review"}`, and `reviewer != producer_agent`.
- `gate()` (line 887-900) refuses on write: reviewer `== "orchestrator"` for any independent gate; reviewer `== producer`; reviewer not in `reviewer_agents`.
- With `producer_agent == "orchestrator"`, `accept()`'s `rec.get("reviewer") == producer` check *also* catches any legacy/roleless record whose reviewer was the orchestrator. The exception therefore **tightens** rather than loosens the accept-time posture for such tasks.
- `required_gates` is written at exactly one place — `new_task()`, line 580. **No CLI subcommand mutates it.** So the independent-gate condition asserted at unblock cannot later be silently removed through the CLI. This is what makes the exception durable rather than a point-in-time check.

**Conclusion: the guard preserves the invariant that a blocked task cannot re-enter the workflow without a producer and a genuinely usable independent reviewer, and opens no route to `accepted` without an independent gate.**

**4.3 Fail-closed analysis of the new helper.** `_roster_strings` (648-666): `None → ([], None)` (preserves the historical `or []`); non-list/tuple → explanatory error; any non-str element → explanatory error; otherwise `[item.strip() …]`. Every branch returns a string or a list — no raise. `_orchestrator_governance_exception` guards `task_type` with `isinstance(…, str)` before `.strip()`. `producer_agent` is type-checked before `.strip()`. I found no shape of `producer_agent`, `reviewer_agents`, `required_gates` or `task_type` that raises out of the guard.

**4.4 The whitespace-stripping change is monotonically tightening — proved, not assumed.** `usable` filters on `r`, `r != RESERVED_ORCHESTRATOR`, `r != producer`. Stripping can only make a name *equal* to `""`, to `"orchestrator"`, or to the (already-stripped) producer — never un-equal. So stripping can only *shrink* `usable`, never grow it. It cannot convert a refusal into a pass. **CONFIRMED SAFE.**

**4.5 Finding F-1 (pre-existing fail-open) independently confirmed as real.** At the base, `reviewers = task.get("reviewer_agents") or []` iterated a bare string `"rev-a"` into `['r','e','v','-','a']` — five truthy elements, none equal to `"orchestrator"` or the producer — so a malformed packet **passed** the roster check and unblocked. This was a fail-open in a fail-closed guard. The producer disclosed it as a defect found rather than folding it in silently, which is the correct handling. The fix closes it on **every** path, including the normal-producer path (`test_project_control.py:1750-1752`).

---

## 5. LEDGER TOTALS AND HISTORY — **CONFIRMED**

**5.1 Totals reconcile against the task files.** Recount from `project-control/tasks/*.json`:
```
FROM TASK FILES: {'accepted': 52, 'awaiting_gate': 9, 'backlog': 11, 'blocked': 3, 'claimed': 1}
CLI status     : {'accepted': 52, 'blocked': 3, 'claimed': 1, 'awaiting_gate': 9, 'backlog': 11}
total task files: 76
```
Exact match. **Accepted remains 52.** `state.json.accepted_tasks` holds exactly 52 ids and is **unchanged** across the branch — the only `state.json` deltas base→HEAD are the addition of `"M0-T033"` to `active_tasks` and `updated_at`.

**5.2 Nothing else moved.** `git diff --name-only abb89b8 HEAD` over `project-control/master_plan.json`, `project-control/checkpoints/`, `project-control/blockers/` → **empty**. `git diff --name-only abb89b8 HEAD -- project-control/tasks/` → **`project-control/tasks/M0-T033.json` only**. `git diff --name-only abb89b8 HEAD -- .claude/ CLAUDE.md .github/` → **empty**. Latest checkpoint `CP-0035.json` exists and `state.json.last_checkpoint == "CP-0035"` — consistent, not stale relative to this branch (this branch records no new checkpoint, correctly, since none is claimed).

**5.3 M0-T027 untouched (D-004-R419) — CONFIRMED four ways.**
- Blob identity: `abb89b8:project-control/tasks/M0-T027.json` = `HEAD:…` = `1d226e997866faca7a2912250984254f7251ddc8`.
- Last commit touching it is `cabf723`, *before* the merge-base.
- `grep -c "M0-T027" tools/project_control.py` → **0** (grep exit 1).
- The only occurrence anywhere in the changed code is the *negative* assertion `tools/test_project_control.py:1913`: `assert "M0-T027" not in src`.

**5.4 Ledger-wide gate integrity (independent scan of all 52 accepted tasks).**
```
ACCEPTED TASKS MISSING/BAD REQUIRED GATES: NONE
SELF-APPROVED INDEPENDENT GATES ON ACCEPTED TASKS: NONE
```
No accepted task lacks a PASS on a required gate; no independent gate on an accepted task was recorded by that task's producer; no `self_check` record is standing in for an independent gate.

**5.5 Active holds and open blockers respected — CONFIRMED.**
- Open blockers are B-001, B-004, B-010, B-011, B-012, B-013. None references M0-T033 or is affected by it (`_blocker_references` would find nothing). B-015/B-016 reference M0-T027 but are `resolved`.
- Expansion-planning owner hold (`.claude/rules/expansion-agent-dispatch-hold.md` §2): untouched — no master-plan change, no pack tasks, no GDS proposals.
- D-004-R418 (only G0/G2/G3/G5): only G0 recorded.
- D-004-R420 (no Step 5, no M0-T032, no unrelated work): the branch contains only M0-T033 lifecycle, the guard change, and amendment 10. CONFIRMED.
- M2-T014/T015/T016 survey-dispatch hold: untouched.

---

## 6. ORCHESTRATOR CLAIMS — INDEPENDENTLY VERIFIED (I took nothing on your word)

**6.1 Tree-identical port — CONFIRMED at the strongest available level.** The producer worktree **still exists** at `.claude/worktrees/agent-af94933c3b313bae5`, HEAD `4da0d524f1345c7126c8b551014359f9d5548975`. I hashed its working files directly:

```
=== PRODUCER WORKTREE blob hashes (agent-af94933c3b313bae5) ===
6b7d3ac7b52ea3444682a08d818f81541102c2a6      tools/project_control.py
1b5fe813a00cc130be95abc4e14ca803e7838d0d      tools/test_project_control.py
0e022358622e65692331b60dfa21719e9ef35bc6      project-control/reports/M0-T033-producer-report.md
=== PRIMARY CHECKOUT (reviewed identity 1e86cd7) ===
6b7d3ac7b52ea3444682a08d818f81541102c2a6
1b5fe813a00cc130be95abc4e14ca803e7838d0d
0e022358622e65692331b60dfa21719e9ef35bc6
```
Identical, and identical to `git rev-parse HEAD:<path>` for all three. The three claimed hashes are exactly right. **CONFIRMED — not merely "the committed blobs match the claim", but "the producer's actual worktree bytes match the committed blobs".**

**6.2 Containment — CONFIRMED, with one packet-bookkeeping discrepancy (§10 D-2).**
Producer-side containment, read from the producer worktree itself:
```
$ git -C .claude/worktrees/agent-af94933c3b313bae5 status --porcelain -uall
 M .claude/agent-memory/backend-engineer/MEMORY.md
 M .claude/agent-memory/backend-engineer/env-producer-sandbox-no-exec.md
 M tools/project_control.py
 M tools/test_project_control.py
?? project-control/reports/M0-T033-producer-report.md
```
Exactly the three authorized artifacts plus the producer's **own** agent-memory namespace, which `.claude/rules/project-control.md` explicitly permits for every agent. **No escape.**

Branch-side, base→HEAD:
```
M project-control/directives/D-004-agent-teams-runtime-adoption/manifest.json      [orchestrator, 836daef]
M project-control/directives/…/requirements.json                                   [orchestrator, 836daef]
A project-control/directives/…/source-011-amendment.md                             [orchestrator, 836daef]
M project-control/directives/…/verification.json                                   [orchestrator, 836daef]
A project-control/gates/M0-T033-G0.json                                            [orchestrator lifecycle]
A project-control/reports/M0-T033-G0-readiness.md                                  [orchestrator lifecycle]
A project-control/reports/M0-T033-evidence-map.json                                [orchestrator, 8fd0019]
A project-control/reports/M0-T033-producer-report.md                               [producer, 6592b89]
M project-control/state.json                                                       [orchestrator lifecycle]
M project-control/tasks/M0-T033.json                                               [orchestrator lifecycle]
M tools/project_control.py                                                         [producer, 6592b89]
M tools/test_project_control.py                                                    [producer, 6592b89]
```
Per-commit isolation is clean: `6592b89` (producer) touches exactly 3 files; `8fd0019` touches exactly 1. The directive-registry writes are the orchestrator's D-001 capture authority (correctly excluded from the producer's scope by `forbidden_paths`). See §10 D-2 for the evidence-map path discrepancy.

**6.3 `docs/GATES_AND_CHECKPOINTS.md` byte-identical — CONFIRMED.**
```
$ git diff --exit-code abb89b8 HEAD -- docs/GATES_AND_CHECKPOINTS.md ; echo exit=$?
exit=0
$ git rev-parse abb89b8:docs/GATES_AND_CHECKPOINTS.md HEAD:docs/GATES_AND_CHECKPOINTS.md
b250643ac1291b47ec4462c39ff18a4fafeb5a7f
b250643ac1291b47ec4462c39ff18a4fafeb5a7f
```
I independently agree with the producer's judgment that no invariant there is contradicted: the document states nothing about `producer_agent`, the reserved orchestrator as producer, or the unblock roster. Its line-5 "No producer approves its own work" and line-163 "Producer and G3 reviewer must be different agent identities" are **reinforced**, not weakened — condition 3 requires a reviewer ≠ producer *before* the exception applies, and `gate()` re-checks it independently. The conditional edit was correctly not taken.

**6.4 Negative-control residue — CONFIRMED ZERO.**
```
$ grep -n "if False" tools/project_control.py tools/test_project_control.py ; echo exit=$?
exit=1
$ grep -rn "NEGATIVE CONTROL" tools/ ; echo exit=$?
exit=1
$ git hash-object tools/project_control.py
6b7d3ac7b52ea3444682a08d818f81541102c2a6   (= claimed pre-injection blob)
```
0 hits, 0 hits, guard blob identical. **All three residue claims CONFIRMED.**
*Scope note:* the NC-1/NC-2/NC-3 **transcripts** themselves are stored evidence I cannot re-execute (I am read-only and the injections were reverted). I verify them as stored evidence, and I explicitly **do not require a re-run**: the guard blob is byte-identical to the pre-injection state, I re-ran the full suite at the reviewed identity myself, and I independently read the assertion mechanism (§8) which is strong enough to stand without the NCs.

**6.5 Evidence map and content identity — INDEPENDENTLY RECOMPUTED.** Using the canonical resolver read-only:
```
identity at reviewed SHA : cd8f93b76116c1e43b84bb0aa54f5ad621ddc16ae5e0a932cdfe86f65a8e1665
resolved_sha             : 1e86cd74cc0f80bd1c2bd238e088b11640b1f2a0
err                      : None
directive refs ok        : True   reasons: []
resolver applicable count: 52
submit-record identity   : cd8f93b76116c1e43b84bb0aa54f5ad621ddc16ae5e0a932cdfe86f65a8e1665
identity match           : True
applicable == submit list: True
evidence-map covered     : 52
missing                  : []
extra                    : []
```
The 52-requirement set is genuinely resolver-derived, exactly covered, with zero omissions and zero extras. The identity stamped at submit (`8fd0019`) is still valid at the reviewed identity `1e86cd7` because `_MANIFEST_EXCLUDE_PREFIXES = ("project-control/",)` (line 311) excludes lifecycle churn. `D-004-R420`'s exclusion is correct — it is scoped to the OPTION-B sentinel, not to this task. OQ-4 is genuinely RESOLVED.

---

## 7. COMMANDS I RAN — VERBATIM, UNTRUNCATED

### 7.1 `python tools/test_project_control.py` (exit code 0)
```
OK: original 15-check workflow preserved
OK: S1 transition enum (legal chain passes; every prohibited jump rejected)
OK: S2 accept preconditions (status, gates, dependencies, blockers)
OK: S3 gate classes (independent/self_check/administrative; no bypass)
OK: S4 containment (task ids, report paths, gate ids, checkpoint ids)
OK: S5 atomic writes (concurrent invocations, interrupted write, serialization failure)
OK: S6 spoofing attempts all rejected
OK: S7 backward compatibility (357 real ledger files parse; legacy records accepted; validation is write-time only; zero-backlog composition survived via synthesized exemplar)
OK: S8 hardening follow-up (orchestrator roster prohibition, --gates enum, blocked-task roster precondition)
OK: S10 governance-orchestrator unblock semantics (4 conjunctive conditions, preserved defaults, fail-closed malformed data, gate() unchanged, source-level generality proofs)
    S10 [D-004-R413/R414]: 10/10 blocks executed, 118 assertion cases
    S10 per-block case counts: 1-non-governance-orchestrator-refused=32, 2-governance-orchestrator-unblocks=9, 3-governance-orchestrator-no-reviewers-refused=2, 4-orchestrator-only-roster-refused=3, 5-governance-no-independent-gate-refused=6, 6-malformed-fails-closed=31, 7-normal-producer-unchanged=12, 8-cancel-and-message-only-ungated=12, 9-gate-unchanged=8, 10-source-level-generality-proofs=3
OK: docs honesty (--agent disclaimed in --help and module docstring)
OK: S9 directive claim enforcement (refs required, selective citation refused, governance-path guard)
OK: S9 submit git-canonical identity (clean-required, dirty fails closed, stale on edit)
OK: S9 accept requires independent per-task verification at the git identity
OK: S9 regime-bypass closed + migration table (9 adversarial proofs)
OK: all 15 project-control test groups passed
```
**15/15 groups, exit 0, `10/10 blocks executed`, 118 assertion cases — CONFIRMED.** Byte-for-byte identical to the producer report §6.1 transcript.

### 7.2 `python tools/validate_directive_compliance.py --check`
```
(no output)
EXIT=0
```
**Exit 0 — CONFIRMED.** `--check` is quiet-on-success.

---

## 8. EXECUTION-PROOF INTEGRITY (D-004-R413 / R414) — **CONFIRMED CORRECTED**

The earlier rejection was justified and the correction is real, not cosmetic. I verified the mechanism line by line rather than trusting either the code comment or the report.

**8.1 All ten blocks register.** `_rec("…")` appears at exactly ten sites: `1673, 1697, 1710, 1723, 1740, 1778, 1811, 1839, 1879, 1922`. The previously-uncovered blocks (6-malformed, 7-normal-producer, 8-cancel, 9-gate-unchanged, 10-source-proofs) — which are precisely the ones proving R352/R367, R368, R369, R370 and R345/R346 — are **now all wired**.

**8.2 `executed` is genuinely READ.** `tools/test_project_control.py:1931-1947`:
```python
        expected_blocks = [
            ("1-non-governance-orchestrator-refused", 32),   # 8 task types x 4 targets
            ("2-governance-orchestrator-unblocks", 9),       # 5 gate ids + 4 targets
            ...
            ("10-source-level-generality-proofs", 3),        # 3 guard functions parsed
        ]
        assert executed == expected_blocks, \
            ("S10 did not execute every mandatory block, in order, with every "
             f"case.\n  expected: {expected_blocks}\n  actual:   {executed}")
        total = sum(cases for _, cases in executed)
        assert total == 118, f"S10 total executed cases changed: {total}"
```
This is **list equality on the complete ordered `(label, count)` sequence** — not a length check, not a floor. A skipped, reordered, duplicated, short-circuited, or case-losing block fails here. The comment's claim now matches the code exactly; the earlier version's overstatement is gone.

**8.3 `10/10` cannot print unless every block registered — CONFIRMED.** The print at `:1951` is **after** the `assert` at `:1943`. It is computed as `len(executed)/len(expected_blocks)`. Both must be 10 and the sequences must be equal for control flow to reach the print at all.

**8.4 Counts are measured, not asserted.** In blocks 1-8 the counter `n` is incremented **inside** the loop body after every case's assertions, so `n` is a genuine execution count. `_rec` additionally refuses a zero count: `assert cases > 0, f"S10 block {label!r} reached its end having executed ZERO cases"`. Block 9 uses `n` from a 5-iteration loop plus a literal `n += 3` covering three straight-line assertion groups that must have executed to reach `_rec`; block 10 uses `len(guard_names)` guarded by `assert set(bodies) == set(guard_names)`. Both are acceptable — minor, and disclosed.

**8.5 Registration in the real runner — CONFIRMED.** `ALL_TESTS` is declared at `:1959`, `test_s10_governance_orchestrator_unblock` is entry 10 at `:1969`, the runner iterates at `:1979-1980`, and the summary at `:1981` is `print(f"OK: all {len(ALL_TESTS)} …")` — **computed from `len(ALL_TESTS)`, not a hardcoded literal**. `grep -c "^    test_"` = **15**. So the "15 groups" line cannot be faked by editing a constant.

**8.6 Pre-existing tests were not weakened — CONFIRMED by the strongest possible evidence.** The entire `tools/test_project_control.py` diff base→HEAD contains **zero `-` lines**:
```
$ git diff abb89b8 HEAD -- tools/test_project_control.py | grep "^-" | grep -v "^---"
(empty)
```
It is a pure addition (3 hunks: header prose, the S10 function, the `ALL_TESTS` entry). S8 — the pre-existing unblock-roster regression group at `:938-1086` — is literally unmodified and green. AS-1's "unmodified in substance" is satisfied in the strictest possible sense: unmodified in bytes.

**8.7 The producer's honest disclosure of its own failed instrumentation** (an invented `total >= 120` floor that failed against the real 118, replaced with measured exact counts rather than a lowered threshold) is preserved in report §5A.3. Correct handling under R411/R412.

---

## 9. EXPLICIT RULINGS ON THE OPEN QUESTIONS

D-004-R415 requires an **explicit independent-review ruling** on OQ-1. As one of the four independent reviewers I record mine here. It is a reviewer ruling, not an orchestrator or producer resolution.

**OQ-1 — the `required_gates`/`task_type` validation asymmetry (R352 vs R368): RULE FOR R368. LEAVE AS BUILT.**
Reasoning, on control-plane merits:
1. R352's subject is *"malformed **roster** data fails CLOSED."* The roster is `producer_agent` + `reviewer_agents`. **Both** fail closed on **every** path after this change, including the normal-producer path (`:1750-1752`). R352 is fully satisfied on its own terms.
2. `required_gates` is a gate-requirement field. On the normal-producer path the guard has **never** consulted it. Validating it there would flip previously-unblockable packets to refused — which R368 forbids in terms ("normal non-orchestrator producer behavior remains unchanged").
3. Decisively: leaving it creates **no fail-open**. On the orchestrator path a malformed `required_gates` REFUSES. On the normal path the task may unblock, but it cannot then be **accepted** — `accept()` iterates `sorted(set(t.get("required_gates") or []))` (line 990) and a malformed value yields either nonsense gate names with no PASS record (refusal) or a `TypeError` (a fail-**loud**, not a fail-open). The invariant "cannot reach `accepted` without an independent gate" survives either ruling. The asymmetry is therefore a stylistic exposure, not a security hole, and R368's explicit prohibition on behavior change dominates.
4. Behavior is pinned by tests either way, so the ruling costs nothing in future reversibility.

**OQ-2 — whitespace stripping: ACCEPT.** Proved monotonically tightening in §4.4 — it can only remove names from `usable`, never add. It closes a genuine whitespace evasion of the reserved identity (`" orchestrator "` previously counted as a usable independent reviewer). It moves strictly in the fail-closed direction and no existing test depended on the old behavior.

**OQ-3 — the AS-11 literal-grep interpretation: ACCEPT the producer's reading.** R345's binding text is *"Do not hard-code M0-T027 anywhere in the guard fix."* Verified: **0** occurrences of `M0-T027` in the entire module. The retained citations (`M0-T014 G3 OBS-3`, `M0-T007/M0-T008`, and the new `M0-T033`) live only in docstrings, are provenance required by CLAUDE.md permanent principle 2, and are excluded by the ast test that strips docstrings before asserting no `M\d+-T\d{3}` in executable code (`:1881-1899`). AS-11's stricter literal reading would require destroying the trace to why the guard exists — subordinate to a permanent principle. The owner requirement is satisfied literally; the packet's paraphrase is not the governing text.

**OQ-4 — 42-vs-52 derivation: RESOLVED and independently reconfirmed** (§6.5). The producer correctly caught that D-004-R420 is not applicable to this task, against the orchestrator's own looser "R410–R420" prose. That is a producer catching an orchestrator error, and it is right.

---

## 10. FINDINGS

### D-1 — **DEFECT (must fix before merge): the CLI submit record is not committed.**
`project-control/reports/M0-T033.json` — the machine record written by `submit()` — **exists on disk but is untracked at the reviewed identity**.
```
$ git ls-files --error-unmatch project-control/reports/M0-T033.json
error: pathspec 'project-control/reports/M0-T033.json' did not match any file(s) known to git
$ git log --oneline -- project-control/reports/M0-T033.json
(empty — never committed)
$ git check-ignore -v project-control/reports/M0-T033.json ; echo exit=$?
exit=1   (NOT gitignored)
$ git ls-files project-control/reports/ | grep -cE "M[0-9]-T[0-9]+\.json$"
47       (47 peer submit records ARE tracked)
```
This is **not** a lifecycle-legality defect — the transition genuinely happened through the CLI (task file at 85%/`awaiting_gate`, byte-identical to `save()` output, record present on disk with a valid resolver-derived 52-id set). It is an **evidence-completeness defect with a material consequence**: `_directive_accept_reasons` (line 481-490) reads `report_path(task_id)` **from disk**. After merge, on any fresh checkout, `rep` is `None` and acceptance fails with *"frozen-evidence identity mismatch"*. Left uncorrected this becomes a latent acceptance blocker for M0-T033 — and therefore, by D-004-R419, a permanent block on M0-T027.

This is an exact recurrence of the M0-T028 defect the orchestrator itself fixed in `14ed27f "M0-T028 lifecycle: add the CLI submit record missed from PR #122"`.

**Identity-neutral:** `_MANIFEST_EXCLUDE_PREFIXES = ("project-control/",)`, so committing this file does **not** change `content_manifest_sha256` (`cd8f93b7…`) and does **not** invalidate this review or any concurrent gate.

### D-2 — **DISCREPANCY (packet bookkeeping): `M0-T033-evidence-map.json` is outside `allowed_paths`.**
The packet's `allowed_paths` are exactly five entries; `project-control/reports/M0-T033-evidence-map.json` is **not** among them, and is not in `forbidden_paths` either. AS-12 as literally worded ("git diff --name-only against the frozen base shows no file outside them") is therefore **not satisfied** at the reviewed identity.

Assessment: **non-material against the owner's text.** D-004-R342 authorizes *"M0-T033's own packet **and reports**"* — the evidence map is one of M0-T033's own reports. It is also **structurally mandatory**: `_directive_submit_check` (line 437-439) refuses an in-regime submit without `--evidence-map`. It was produced by the orchestrator (commit `8fd0019`), not smuggled by the producer — it is absent from the producer worktree entirely — and this matches established precedent (M2-T018, M4-T008, M0-T028 evidence maps were all committed in orchestrator lifecycle commits). The `allowed_paths_note` already anticipates this class of entry for `tasks/M0-T033.json`; the evidence map was simply omitted from the same enumeration. **Recommendation: record the reasoning explicitly rather than letting AS-12 pass silently, and list the evidence-map path in future in-regime packets.**

### D-3 — **DEFECT (documentation accuracy): stale line citations in the producer report.**
Every `tools/test_project_control.py` line citation in report §§2-5 points at unrelated content in the committed file:

| Report says | Claim | Actual location |
|---|---|---|
| `:1837-1854` | ast source proof | **1881-1899** |
| `:1868-1869` | `assert "M0-T027" not in src` | **1913-1914** |
| `:1805-1815` | `gate()` regression proofs | **1841-1879** |
| `:1764-1775` | normal producer + varied `required_gates` | **1802-1810** |
| `:1718-1722` | malformed roster on the normal path | **1750-1752** |
| `:1958` / `:1968` / `:1980` | `ALL_TESTS` / S10 entry / summary print | **1959 / 1969 / 1981** |

Every cited assertion **does exist** — I located each one — so no claim is false in substance; the pointers are stale (§§2-5 were carried over from the first, rejected return without re-anchoring after the file grew). Note the contrast: all `tools/project_control.py` citations (`648-666`, `748-749`, `887-891`, `892-893`) are **exact**, and §5A.3's ten `_rec` line numbers are **exact**. Under D-004-R413, evidence offered as proof should resolve when followed; these do not. **Non-blocking, correction required.**

### OBS-1 — Administrative gates become unrecordable once `producer_agent == "orchestrator"`.
`gate()`'s administrative branch refuses when `producer and producer == a.reviewer` (line 879-880), and G0/G7 **require** `reviewer == "orchestrator"` (line 876). So a task admitted by the new exception can never obtain a **new** G0 or G7 record. Pre-existing `gate()` logic, unchanged by M0-T033, but the exception makes it reachable through a new route.
**Materiality for OPTION B: none.** I verified M0-T027 concretely: `required_gates = ['G0','G2','G3','G5']`, no G7; `M0-T027-G0.json` already exists with `result=PASS`, `role=administrative`; G2 is recordable (the self-check branch has no producer check); G3/G5 are recordable by its three rostered reviewers, none of which is the orchestrator. **OPTION B is structurally completable.** Flagged so it is not discovered later: if a G3/G5 ever FAILs and a re-recorded administrative gate is needed, that task would deadlock.

### OBS-2 — `claim()` still permits `--agent orchestrator` for any task type.
`claim()` (606-645) sets `producer_agent = a.agent` with no reserved-identity check. So `producer_agent == "orchestrator"` was **already** reachable pre-change on the `ready → claimed` path, for *any* `task_type`, with none of the four conditions. The new exception is therefore **stricter** than the pre-existing claim path, and the guard was never the sole defense. Not a regression and out of M0-T033's scope (D-004-R343); recorded so the asymmetry is a known, chosen state rather than an assumed invariant.

### OBS-3 — `accept()` can raise `TypeError` on a non-iterable `required_gates`.
`sorted(set(t.get("required_gates") or []))` (line 990) raises on e.g. `7`. Fail-**loud**, never fail-open, and pre-existing. Explicitly out of scope here (R343 forbids touching `accept()`); noted as a candidate follow-up if the orchestrator later takes the R352-dominant reading I ruled against in §9.

### OBS-4 — Reserved-identity comparisons remain case-sensitive.
`producer == RESERVED_ORCHESTRATOR` is exact equality, so `"Orchestrator"` would not enter the exception path. Unchanged from the base (the old code used the same exact comparison), and `gate()`'s `reviewer == producer` check still catches the case-variant at gate time. No regression; recorded for completeness.

---

## 11. CHECK-BY-CHECK SUMMARY

| # | Check | Result |
|---|---|---|
| 1 | HEAD == frozen reviewed identity | **CONFIRMED** `1e86cd74cc0f80bd1c2bd238e088b11640b1f2a0` |
| 2 | G0 recorded before claim | **CONFIRMED** (timestamps + structural impossibility of the reverse) |
| 3 | Claimed by a real non-orchestrator producer | **CONFIRMED** `backend-engineer` |
| 4 | Every transition legal per `PROGRESS_TRANSITIONS` | **CONFIRMED** |
| 5 | No hand-set lifecycle state | **CONFIRMED** (byte-identical to `save()` at 170478e/4da0d52/1e86cd7) |
| 6 | Packet never amended after contracting | **CONFIRMED** (content digest constant across all 4 commits) |
| 7 | Producer ≠ every reviewer; reviewers mutually distinct | **CONFIRMED** |
| 8 | G2 not counted as an independent gate | **CONFIRMED** (`INDEPENDENT_GATES` excludes G2; `accept()` line 997-999) |
| 9 | Blocked task still needs producer + usable independent reviewer | **CONFIRMED** (reviewer test precedes the exception, lines 741-749) |
| 10 | No path to `accepted` without an independent gate | **CONFIRMED** (`required_gates` immutable post-`new_task`; `accept()` line 990-1005) |
| 11 | `gate()` / `submit()` / `accept()` unchanged | **CONFIRMED** (no diff hunk) |
| 12 | Accepted count remains 52 | **CONFIRMED** (task files 52 == `state.json` 52 == CLI 52) |
| 13 | Ledger totals match task files | **CONFIRMED** 52/3/1/9/11 = 76 |
| 14 | Master plan / checkpoints / blockers untouched | **CONFIRMED** (empty diff) |
| 15 | No other task file altered | **CONFIRMED** (only `M0-T033.json`) |
| 16 | M0-T027 untouched; absent from `project_control.py` | **CONFIRMED** (identical blob; `grep -c` = 0) |
| 17 | No accepted task lacks a required-gate PASS | **CONFIRMED** (52/52 scanned, NONE) |
| 18 | No self-approved independent gate anywhere | **CONFIRMED** (NONE) |
| 19 | Tree-identical port (3 claimed blob hashes) | **CONFIRMED** against the live producer worktree |
| 20 | Containment held | **CONFIRMED** producer-side; see D-2 for the packet-list discrepancy |
| 21 | `GATES_AND_CHECKPOINTS.md` byte-identical | **CONFIRMED** (`exit=0`; blob `b250643a…`) |
| 22 | Zero negative-control residue | **CONFIRMED** (0 `if False`, 0 `NEGATIVE CONTROL`, blob match) |
| 23 | Full suite 15/15, `10/10 blocks executed`, exit 0 | **CONFIRMED** (ran it myself) |
| 24 | `validate_directive_compliance.py --check` exit 0 | **CONFIRMED** |
| 25 | R413/R414 execution proof genuinely covers all 10 blocks | **CONFIRMED** |
| 26 | Complete expected `(label, count)` sequence really asserted | **CONFIRMED** (`:1943` list equality) |
| 27 | `10/10` cannot print unless every block registered | **CONFIRMED** (assert precedes print) |
| 28 | Evidence map = 52 resolver-derived, exactly covered | **CONFIRMED** (recomputed) |
| 29 | Content identity valid at reviewed SHA | **CONFIRMED** `cd8f93b7…` |
| 30 | Only authorized gate G0 recorded (R418) | **CONFIRMED** |
| 31 | Owner holds + open blockers respected | **CONFIRMED** |
| 32 | Submit record committed | **VIOLATED** — see D-1 |
| 33 | AS-12 changed-file set within `allowed_paths` | **VIOLATED (non-material)** — see D-2 |
| 34 | Report line citations resolve | **VIOLATED (non-material)** — see D-3 |
| 35 | Negative-control transcripts reproducible by me | **INDETERMINATE** — accepted as stored evidence; residue independently confirmed; no re-run required |

---

## 12. VERDICT AND BINDING CORRECTIONS

### **PASS — with required corrections**

The control-plane correction is **sound and correctly scoped**. It preserves every stated default, makes the four conditions genuinely conjunctive with the independent-reviewer test as a precondition rather than an alternative, fails closed on every malformed shape, closes a real pre-existing fail-open, hard-codes no task id, adds no bypass, and leaves `gate()`, `submit()`, `accept()`, directive verification, evidence identity, and producer-versus-reviewer separation byte-unchanged and fully enforcing. The R413/R414 execution proof, which was rightly rejected once, is now genuine. I found **no self-approval, no missing gate, no out-of-order transition, no stale checkpoint, and no held/dispatched conflict.**

Recorded per `.claude/rules/project-control.md` gate-verdict semantics: PASS, with the following corrections **BLOCKING for the next gate and for acceptance**.

**C1 (MANDATORY, before merge — blocking).** Commit `project-control/reports/M0-T033.json`. It is the CLI submit record, is not gitignored, has 47 tracked peers, and its absence will make `accept M0-T033` fail on any fresh checkout with "frozen-evidence identity mismatch" — permanently blocking M0-T027 through D-004-R419. Committing it is **identity-neutral** (`project-control/` is excluded from the content manifest) and does not require re-review. Precedent: `14ed27f`.

**C2 (MANDATORY, before acceptance).** Correct the stale `tools/test_project_control.py` line citations in `project-control/reports/M0-T033-producer-report.md` §§2, 3, 4, 5, 5A.1, 5A.2 (D-3 table above), **or** record an orchestrator note that the citations are stale-but-substantively-verified with the corrected anchors. Evidence offered under R413 should resolve when followed.

**C3 (RECORD, not a code change).** Record explicitly that `project-control/reports/M0-T033-evidence-map.json` is authorized by D-004-R342's *"M0-T033's own packet and reports"* and is structurally required by `_directive_submit_check`, so AS-12 is met on the owner's text despite the packet's `allowed_paths` array omitting it. Add the evidence-map path to `allowed_paths` in future in-regime packets.

**C4 (CARRY FORWARD to the orchestrator, no action in M0-T033).** OBS-1 (administrative gates unrecordable once `producer_agent == "orchestrator"` — harmless for M0-T027, verified) and OBS-2 (`claim()` still accepts `--agent orchestrator` for any task type, so the reserved-producer rule is enforced only at the blocked-exit). Neither is in M0-T033's authorized scope (D-004-R343).

**R415 ruling recorded (§9):** **R368 dominant — leave the validation asymmetry as built.** OQ-2 accepted (monotonically tightening, proved). OQ-3 accepted (R345 satisfied literally; provenance protected). OQ-4 resolved and reconfirmed. Negative-control re-run at the advanced base: **not required**.

---

### Files relevant to this report (absolute paths)

- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\project_control.py` — the guard: `_roster_strings` 648-666, `_orchestrator_governance_exception` 669-698, `invalid_unblock_roster` 700-751; unchanged `gate()` 859-956, `accept()` 974-1052
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\test_project_control.py` — S10 1609-1956, execution proof 1931-1954, `ALL_TESTS` 1959-1975
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\tasks\M0-T033.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\gates\M0-T033-G0.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T033.json` — **UNTRACKED (D-1)**
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T033-producer-report.md` — **D-3 stale citations**
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T033-evidence-map.json` — **D-2**
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T033-G0-readiness.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\state.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\tasks\M0-T027.json` — verified untouched
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\agent-af94933c3b313bae5` — live producer worktree used to verify the tree-identical port

I made no writes of any kind — no `project_control.py` subcommand, no git or gh mutation, no ledger edit, and no agent-memory file.
