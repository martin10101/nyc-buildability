# M0-T033 — G3 INDEPENDENT CODE REVIEW

> **Orchestrator preservation note.** The body below is the `code-reviewer` return preserved
> **VERBATIM** per `.claude/rules/project-control.md` (report-preservation rule), with transport
> entity-decoding only (`&lt;`/`&gt;`/`&amp;` restored to `<`/`>`/`&`). Nothing was added, removed,
> condensed, or reworded. The reviewer was dispatched read-only on explicit Opus 5 under the
> D-004-R307 availability exception.
>
> Orchestrator disposition of C1/C2/C3 is recorded in the M0-T033 progress log; this file is the
> reviewer's own words. C1 is an orchestrator packet-drafting defect, not a producer defect.

---

# Gate Report

- **Gate ID:** G3 (independent code review)
- **Task ID:** M0-T033 — Governance-orchestrator unblock-roster semantics
- **Reviewer:** `code-reviewer` (independent; read-only). **Model actually running: Opus 5, exact model id `claude-opus-5[1m]`**, under the D-004-R307 availability exception. No Fable 5 claimed.
- **Producer:** `backend-engineer` (distinct from this reviewer; its report was treated as claims to reproduce, never as proof)
- **Result: PASS** — with 3 required corrections (ledger/report hygiene, no code change) and 5 non-blocking observations.
- **Clean environment/worktree used:** primary checkout at the frozen reviewed identity; branch `task/M0-T033-unblock-roster-semantics`.

## Identity verified first

```
$ git rev-parse HEAD
1e86cd74cc0f80bd1c2bd238e088b11640b1f2a0

$ git branch --show-current
task/M0-T033-unblock-roster-semantics
```

Matches the frozen reviewed identity `1e86cd74cc0f80bd1c2bd238e088b11640b1f2a0`. Review proceeded.

Working tree carries only untracked/modified `.claude/agent-memory/**` files (other agents' own memory), no in-scope dirt.

**Frozen content identity independently recomputed** (`_task_git_identity` over `allowed_paths`, excluding `project-control/`):

```
reviewed_sha=1e86cd74cc0f80bd1c2bd238e088b11640b1f2a0   identity=cd8f93b76116c1e43b84bb0aa54f5ad621ddc16ae5e0a932cdfe86f65a8e1665 err=None
stamped in submit record: cd8f93b76116c1e43b84bb0aa54f5ad621ddc16ae5e0a932cdfe86f65a8e1665
```

The stamped submit identity recomputes exactly at HEAD. The lifecycle commit `1e86cd7` did not stale the identity because `_MANIFEST_EXCLUDE_PREFIXES = ("project-control/",)` (`tools/project_control.py:311`).

Branch composition: `6592b89` (producer code + report), `8fd0019` (evidence map), `1e86cd7` (orchestrator lifecycle).

## Acceptance criteria reviewed

All 12 packet scenarios, judged against primary evidence (code, executed tests, my own differential and mutation runs) — not against the producer's narrative.

| AS | Verdict | Independent basis |
|---|---|---|
| **AS-1** (R362) non-governance + orchestrator still refused | **PASS** | S10 block 1 = 32 cases (8 task types × 4 active targets, incl. `"Governance"`, `"gov"`, `""`). Refusal asserts on `"governance"` in stderr, a string only the task_type branch emits — well-targeted. Pre-existing S8 blocked-roster group (`tools/test_project_control.py:1021`) is **unmodified**: the test diff has **0 deleted lines** (pure addition). My mutant B (task_type condition disabled) fails here. |
| **AS-2** (R363) the one narrow case unblocks | **PASS** | S10 block 2 = 9 cases: all five independent gate ids **and** all four active targets. `PROGRESS_TRANSITIONS["blocked"] = {backlog, ready, in_progress, awaiting_gate, canceled}` — target coverage is complete. My mutant A fails here. |
| **AS-3** (R364) empty roster refused | **PASS** | S10 block 3 covers `[]` and `None`. |
| **AS-4** (R365) orchestrator-only roster refused | **PASS** | S10 block 4 covers `["orchestrator"]`, duplicated, and `["", "orchestrator"]`. My mutant E (usable-reviewer filter removed) fails here. |
| **AS-5** (R366) no independent gate refused | **PASS** | S10 block 5 covers `[]`, `["G0"]`, `["G2"]`, `["G7"]`, `["G0","G2","G7"]`, `None`, and asserts all five gate ids appear in the refusal. My mutant D fails here. |
| **AS-6** (R367) malformed fails closed, no traceback | **PASS** | S10 block 6 = 31 shapes. Independently: **zero raises across 143,640 input shapes** (below). My mutant C (reinstating the original fail-open) fails here. See OBS-1 for a precision gap. |
| **AS-7** (R368) normal producer unaffected | **PASS** | S10 block 7 = 12 cases. My differential proves the stronger property: for well-formed rosters the new usable-reviewer set is a **subset** of the old, so **no** non-orchestrator producer newly passes. |
| **AS-8** (R369) blocked→canceled always permitted | **PASS** | S10 block 8 = 12 cases (6 cancel shapes incl. malformed, + 6 message-only). Call site `tools/project_control.py:778-779` gates only `cur == "blocked" and target != "canceled"`. |
| **AS-9** (R370) reviewer ≠ producer; gate() unweakened | **PASS** | S10 block 9 = 8 cases. Independently: `gate` is **byte-identical** to base by AST extraction. |
| **AS-10** (R371) full suites green | **PASS** | Both run by me; verbatim output below. 15/15 groups, exit 0; validator exit 0. |
| **AS-11** (R345/R346) no task-id literal, no bypass | **PASS on the controlling requirement** | See **OQ-3 ruling**. Literal packet wording ("any `M0-T0` pattern in the changed region") is **not** met — docstring prose retains `M0-T007/M0-T008`, `M0-T014`, `M0-T033`. Ruled over-broad drafting; R345's actual text is satisfied absolutely. |
| **AS-12** (R343/R361) containment + control paths byte-unchanged | **PASS on the behavioural half; literal containment half not met** | 33 of 34 shared functions byte-identical; `gate`/`submit`/`accept`/`claim`/`progress`/`_directive_claim_check` all byte-identical. Two files in the branch diff fall outside `allowed_paths` — **both orchestrator-lifecycle/CLI-mandated, neither a producer escape**. Recorded as required correction **C1**. |

## Directive/requirement verification

I re-derived the applicable set myself through the canonical resolver rather than trusting the producer's table:

```
DERIVED applicable count: 52
unresolved reasons      : NONE
EVIDENCE-MAP row count  : 52
MISSING from evidence map: NONE
EXTRA in evidence map    : NONE
set equality             : True
```

Reviewed SHA for every row below: `1e86cd7…` / content identity `cd8f93b7…`.

| Requirement ID | Verdict | Reproduced evidence |
|---|---|---|
| D-004-R332 | PASS | Option B implemented as a narrow guard correction; `tools/project_control.py:669-750`. Neither option (a) false producer nor (c) abandonment appears. |
| D-004-R335 | ATTESTED (not G3-verifiable) | Spawn-time model is not observable from the tree. This reviewer is explicit Opus 5. |
| D-004-R336 | PASS | Report header lines 6-7 disclose Opus 5 / `claude-opus-5[1m]`. |
| D-004-R337 | PASS | `project-control/tasks/M0-T033.json` well-formed, CLI-authored. |
| D-004-R338 | PASS | `.claude/agents/backend-engineer.md` exists; producer ≠ each of the four reviewers. |
| D-004-R339 | PASS | Packet `reviewer_agents` = the exact four; all five agent definition files verified present. |
| D-004-R340 | PASS | Packet `required_gates` = `["G0","G2","G3","G5"]`. |
| D-004-R341 | PASS | **Re-derived by me**: 52 == 52, no extras, no omissions (output above). |
| D-004-R342 | PASS w/ C1 | Producer commit `6592b89` touched exactly 3 files, all in `allowed_paths`. Two further files enter via orchestrator lifecycle / CLI mandate — see C1. `docs/GATES_AND_CHECKPOINTS.md` byte-identical (`git diff --exit-code` = 0). |
| D-004-R343 | PASS | AST diff: only `invalid_unblock_roster` changed; `_roster_strings`/`_orchestrator_governance_exception` added; import set identical (6 lines both sides); no hooks/settings/agents/product/deployment files touched. |
| D-004-R344 | PASS | Correction is shape-driven. Proven general, not special-cased: across all 76 real ledger tasks the verdict flips for **three** — M0-T023, M0-T024 (both `accepted`, i.e. terminal and inert) and M0-T027 — purely by packet shape. |
| D-004-R345 | PASS | `"M0-T027"` occurs **0** times in the whole module (my own count). Guard executable code (AST, docstrings stripped): **zero** task ids. |
| D-004-R346 | PASS | No `getenv`; `os.environ` absent; no `--force/--bypass/--override/--skip`; `progress -h` exposes exactly the six pre-existing options (asserted at `test_project_control.py:1919-1923`). The one `environ` substring is the word "environment" in a docstring (line 723). |
| D-004-R347 | PASS | Missing/blank producer refused — S10 block 7; differential confirms. |
| D-004-R348 | PASS | S10 block 1 (32 cases) + differential: 0 non-governance shapes newly pass. |
| D-004-R349 | PASS | S10 block 3. |
| D-004-R350 | PASS | S10 block 4; **strengthened** — `" orchestrator "` no longer evades (see OQ-2). |
| D-004-R351 | PASS | S10 block 7; `[" backend-x "]` vs producer `backend-x` also now refused. |
| D-004-R352 | PASS | Roster fields fail closed on **every** path — verified across 143,640 shapes, 0 raises. Scope judgment ruled at **OQ-1**. |
| D-004-R353 | PASS | S10 block 8; guard not reached for `canceled` (`tools/project_control.py:778`). |
| D-004-R354 | PASS | `gate` byte-identical; `INDEPENDENT_GATES` unchanged at line 117. |
| D-004-R355 | PASS | Exactly one new branch, `tools/project_control.py:748-749`, reached only after the general roster check. |
| D-004-R356 | PASS | `tools/project_control.py:683` — exact match after strip against `GOVERNANCE_TASK_TYPE`; `"Governance"`/`"gov"` rejected. |
| D-004-R357 | PASS | `tools/project_control.py:691` — `set(gates) & INDEPENDENT_GATES`. |
| D-004-R358 | PASS | Shared general check at `tools/project_control.py:742-747` **precedes** the exception — structurally conjunctive. |
| D-004-R359 | PASS | Guard confined to the blocked-exit; `accept()` byte-identical and still enforces gate roles, producer≠reviewer, and directive verification. |
| D-004-R360 | PASS | M0-T027 admitted by shape alone; zero task-id literals. |
| D-004-R361 | PASS | 33/34 shared functions byte-identical; the changed one is the guard itself. |
| D-004-R362…R371 | PASS (each) | S10 blocks 1-10 all executed; I re-ran the suite myself and additionally proved each condition load-bearing by mutation. |
| D-004-R372 | Orchestrator scope | Lifecycle in progress; G0 recorded, G2/G3/G5 pending. |
| D-004-R373 | Orchestrator scope | Merge/accept gate — not yet due. |
| D-004-R387 | PASS | Two STOPs preserved in report §0(a),(b) rather than smoothed over. |
| D-004-R389 | Orchestrator scope | Branch/worktree cleanup. |
| D-004-R410 | PASS | Work continued at corrected base `4da0d52`; §0(e). |
| D-004-R411 | PASS | §0 preserves the named-spawn denial, the attestation STOP, and the corrected resume — including the admission that the producer *could* have proceeded and stopped anyway. |
| D-004-R412 | PASS | Neither item waived: S10 instrumentation reworked (not accepted); asymmetry preserved as OQ-1. |
| D-004-R413 | PASS | S10 registered in `ALL_TESTS` (`tools/test_project_control.py:1969`); my own run prints `10/10 blocks executed, 118 assertion cases` with per-block counts; exact `(label, count)` sequence asserted at `tools/test_project_control.py:1931-1945`. |
| D-004-R414 | PASS | Producer's NC-1/2/3 reproduced **and exceeded** — I ran 6 independent mutants (below). |
| D-004-R415 | PASS | Explicit independent ruling supplied below; producer correctly did not settle it. |
| D-004-R416/R417/R418 | Orchestrator scope | Containment/port/gate-scope are orchestrator duties; port blob hashes match what I read at HEAD. |
| D-004-R419 | PASS | M0-T027 absent from the changed-file set; `project-control/tasks/M0-T027.json` byte-identical to base (`git diff --exit-code` = 0). |

## Steps independently executed

### 1. Full suite (verbatim, untruncated)

```
$ python tools/test_project_control.py; echo "EXITCODE=$?"
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
EXITCODE=0
```

### 2. Directive registry validator

```
$ python tools/validate_directive_compliance.py --check; echo "EXITCODE=$?"
EXITCODE=0
```

### 3. Exhaustive old-vs-new differential (the core correctness proof)

I loaded the HEAD module and the base-commit module side by side and compared verdicts over a cartesian product of `producer_agent` × `reviewer_agents` × `required_gates` × `task_type`:

```
total shapes exercised: 143640
NEW raises (must be 0): 0
OLD raised on 41580 shapes (base fail-by-traceback surface)

=== NEWLY PASSING (new PASS, old not PASS): 756 shapes ===
  distinct producer values : [" orchestrator ", "\torchestrator\n", "orchestrator ", "orchestrator"]
  distinct task_type values: [" governance ", "\tgovernance\n", "governance"]
  distinct required_gates  : [("G3",), [" G3 "], ["G0","G2","G3","G5"], ["G0","G3"], ["G1"], ["G3"], ["G4"], ["G5"], ["G6"]]
  distinct old outcomes    : ["REFUSE"]
  shapes whose producer is NOT orchestrator (must be 0): 0
  shapes whose task_type is NOT governance (must be 0): 0
  shapes with NO independent gate (must be 0): 0
```

**This is the answer to "is there ANY input shape that newly passes other than the intended case?" — No.** Every one of the 756 newly-passing shapes has producer ≡ `orchestrator`, task_type ≡ `governance`, at least one independent gate, and (necessarily, since it clears the general check) a usable independent reviewer. The four conditions are genuinely conjunctive.

The structural reason, confirmed by reading `tools/project_control.py:731-750`: the orchestrator branch sits at line **748**, *after* the producer check (736), the roster shape check (739-741) and the usable-reviewer check (742-747). It cannot be reached without all of them passing. And for well-formed rosters, `usable_new(r) ⟹ usable_old(r)`, so the new guard is never more permissive than the old one on any non-orchestrator path.

### 4. Mutation testing — does S10 bind, or could it pass vacuously?

Six mutants built in the scratchpad (repo untouched), S10 run against each:

```
=== NEGATIVE CONTROLS: does S10 bind the new guard code? ===
  A-revert-orchestrator-refused      S10 FAILED  line 1668: refusal must explain the governance condition
  B-drop-task_type-condition         S10 FAILED  line 1665: task_type 'engineering' + orchestrator producer must not unblock to backlog
  C-reopen-F1-failopen-roster        S10 FAILED  line 1769: malformed reviewer_agents {... 'reviewer_agents': 'rev-a'} must fail closed, not unblock
  D-drop-independent-gate-condition  S10 FAILED  line 1732: required_gates [] has no independent gate
  E-drop-usable-reviewer-filter      S10 FAILED  line 1718: roster ['orchestrator'] has no usable independent reviewer
  Z-control-unmutated                S10 PASSED
```

**S10 genuinely binds the new code.** Every one of the four conditions plus the fail-closed helper is load-bearing; disable any one and S10 fails in the covering block. The execution recorder is real: `_rec` fires for all 10 blocks and the exact `(label, count)` sequence *is* asserted (`tools/test_project_control.py:1931-1945`), not merely appended — I confirmed by reading it and by watching mutants fail before reaching it.

### 5. Real-ledger impact scan

```
real ledger task files scanned: 76
=== tasks whose guard verdict CHANGED (old vs new) ===
   M0-T023.json  accepted  governance  orchestrator  [4 reviewers]  [G0,G2,G3,G4,G5]  REFUSE -> PASS
   M0-T024.json  accepted  governance  orchestrator  [4 reviewers]  [G0,G2,G3,G4,G5]  REFUSE -> PASS
   M0-T027.json  blocked   governance  orchestrator  [3 reviewers]  [G0,G2,G3,G5]     REFUSE -> PASS
=== currently BLOCKED tasks ===
   M0-T007.json  database  None  []  [G0,G2,G3,G4,G5]  REFUSE -> REFUSE
   M0-T008.json  database  None  []  [G0,G2,G3,G4,G5]  REFUSE -> REFUSE
   M0-T027.json  governance  orchestrator  [3 reviewers]  [G0,G2,G3,G5]  REFUSE -> PASS
```

M0-T023/M0-T024 are `accepted` (terminal — `progress` refuses to modify them), so the verdict flip is inert. The original M0-T014 G3 OBS-3 purpose is fully preserved: M0-T007/M0-T008 remain blocked.

### 6. AST byte-invariance of the control plane

```
added funcs  : ['_orchestrator_governance_exception', '_roster_strings']
removed funcs: []
CHANGED funcs: ['invalid_unblock_roster']
unchanged funcs: 33 of 34 shared

  gate / submit / accept / claim / progress / _directive_claim_check /
  _blocker_references / _regime / _task_in_regime / new_task / checkpoint /
  sync_state / save / load_task / fail   -- all byte-identical: True
```

(Note for reproducibility: comparing the base blob via `subprocess` with `text=True` on Windows decodes as cp1252 and corrupts an em-dash in two unrelated functions, producing false positives. Decode the blob explicitly as UTF-8.)

## Expected versus actual

Everything the packet requires behaviourally is present, and every claim I could reproduce, reproduced. The only expected-vs-actual gaps are documentary:

- **Expected (AS-12):** `git diff --name-only` against the frozen base shows no file outside `allowed_paths`. **Actual:** two files outside it — `project-control/reports/M0-T033-evidence-map.json` and `project-control/state.json`.
- **Expected (AS-11):** no `M0-T0…` pattern in the changed region. **Actual:** three prose citations remain in docstrings.

Both are analysed and ruled on below.

## Evidence paths

- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\project_control.py` (guard: lines 648-666, 669-697, 700-750; call site 778-779; constant 132)
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\test_project_control.py` (S10: 1613-1955; source proofs 1882-1923; sequence assertion 1931-1945)
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T033-producer-report.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T033-evidence-map.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T033.json` (submit record; stamped identity)
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\tasks\M0-T033.json`

## THE FOUR EXPLICIT RULINGS

### OQ-1 — the `required_gates`/`task_type` validation asymmetry: R352 vs R368

**RULING: D-004-R368 dominates. The asymmetry is CORRECT. Leave the code exactly as built. Nothing must change.**

Reasoning, in order of weight:

1. **R352's subject really is roster data, and roster data really does fail closed everywhere.** I did not take this on the producer's word. Across 143,640 shapes, `producer_agent` and `reviewer_agents` fail closed on *every* path — including the non-orchestrator path, where malformed rosters that previously **passed** are now refused (the 22 tightening shapes I enumerated). R352 is satisfied in full, not partially. `required_gates` is a gate-requirement field; the guard is literally named `invalid_unblock_roster`, and the directive's own mandated test row R367 scopes malformed-data testing to "*malformed reviewer data*". The narrow reading is the textually supported one.

2. **There is no reachable fail-open to close.** `new-task` validates `--gates` against `GATE_IDS` with no normalization (`tools/project_control.py:538-541`), so a CLI-authored packet can never hold a malformed `required_gates` — even `--gates "G0, G3"` is rejected because `" G3"` is not in the enum. Malformed values require hand-editing the ledger. And downstream, `accept()` consumes `set(t.get("required_gates") or [])` (`tools/project_control.py:539` region): a malformed value makes acceptance *strictly harder* (it demands PASS records for gate ids that cannot exist) or raises. Validating it at the unblock transition would buy **zero** additional safety.

3. **Tightening would cause the exact harm R368 forbids.** Packets that unblock today for ordinary producers would begin to fail — that is a change to normal-producer behaviour, which R368 prohibits in terms, and it exceeds R344's mandate (a semantic correction of the *orchestrator* case).

4. **The producer was directed to preserve it.** D-004-R415 says "PRESERVE the … asymmetry … for an EXPLICIT independent-review ruling". Preserving it was compliance, not a unilateral judgment.

If a future owner wants uniform packet-field validation, it belongs in its own packet-schema task with its own regression baseline — not folded into this correction.

### OQ-2 — the whitespace-stripping tightening

**RULING: ACCEPTABLE and IN SCOPE. No change required.** But the producer's framing is **understated** and must be corrected (see C3).

- It is **not** an optional flourish. Once `_roster_strings` exists to satisfy R352, comparison without normalization would leave `" orchestrator "` counting as a usable independent reviewer — which would violate the *substance* of R350 ("a roster containing only orchestrator remains invalid"). Stripping is what makes R350 hold.
- It restores **symmetry with pre-existing behaviour**: the base already stripped `producer_agent` (`(task.get("producer_agent") or "").strip()`). Reviewers were the anomaly.
- Direction is uniformly fail-closed, and real-world impact is **nil**: of 76 real ledger tasks, zero verdicts change for whitespace reasons.
- **Correction to the producer's account:** report §3 says the effect is that `" orchestrator "` is now refused. My enumeration shows the tightening is broader — it also newly refuses `[" backend-x "]` when the producer is `backend-x` (a whitespace evasion of the **producer**-identity check, not just the reserved identity) and whitespace-only names like `[" "]` and `["  ", ""]`. Same direction, wider than stated.

### OQ-3 — the AS-11 literal-grep interpretation

**RULING: ACCEPT the producer's reading. AS-11 passes on its controlling requirement.**

- The binding owner text is **D-004-R345: "Do not hard-code M0-T027 anywhere in the guard fix."** I verified independently: `"M0-T027"` appears **0 times in the entire module**, and the guard's executable code (AST-parsed, docstrings stripped) contains **zero** ledger task ids, zero bare gate-id literals, zero bare `"governance"` literal, and reuses `INDEPENDENT_GATES`, `GOVERNANCE_TASK_TYPE`, `RESERVED_ORCHESTRATOR`. R345 is satisfied absolutely, not arguably.
- AS-11's extra clause ("any `M0-T0` task-id pattern in the changed region") is **over-broad drafting**. The ids it would catch — `M0-T007`, `M0-T008`, `M0-T014` — were **already in the base docstring at lines 42-43** and appear in the diff only because the surrounding prose was re-wrapped. Satisfying AS-11 literally would require **deleting pre-existing provenance** that explains why the guard exists, violating CLAUDE.md permanent principle 2, and would be an unauthorized unrelated change.
- Only `M0-T033` is genuinely new prose, and it is a docstring cross-reference, not logic.
- Hard-coding is an **executable-behaviour** property. The AST-based proof is the correct operationalization and is strictly stronger than a text grep; I re-derived it myself rather than trusting the test.

### The negative-control question (re-run after base advanced 170478e → 4da0d52?)

**RULING: NOT required. The producer's reasoning is sound, and I verified its premise rather than accepting it — and the point is moot because I ran my own controls at HEAD.**

Premise verified by blob hash:

```
tools/project_control.py       170478e: 70a5a865b2f13f841b33adeb73ce6fa2156caf41
                               4da0d52: 70a5a865b2f13f841b33adeb73ce6fa2156caf41   IDENTICAL
tools/test_project_control.py  170478e: 14a145e1a79bebec31d84f32e89a782e179f6d97
                               4da0d52: 14a145e1a79bebec31d84f32e89a782e179f6d97   IDENTICAL

files changed across the advance: only project-control/directives/** (+ state.json, M0-T033.json)
```

Both inputs to the negative controls are byte-identical across the advance; the advance touched only the directive registry and control-plane bookkeeping. A re-run could not have produced a different result. Independently, I executed **six** mutation controls at the frozen HEAD, superseding all three.

## Regression / security / provenance findings

### F-1 (producer's finding) — CONFIRMED REAL, and more severe than reported

Verified at base commit `4da0d52`:

```
BASE roster='rev-a'         :: ('PASS', None)
BASE roster='orchestrator'  :: ('PASS', None)
BASE roster='x'             :: ('PASS', None)
BASE roster=dict(keys)      :: ('PASS', None)
HEAD (all four)             :: ('REFUSE', 'reviewer_agents is malformed …')
```

The original `reviewers = task.get("reviewer_agents") or []` at base iterated a bare string character-by-character. The producer reported the `"rev-a"` case. **It is worse than that:** a packet with `"reviewer_agents": "orchestrator"` — a roster naming *only the reserved identity* — also **PASSED** at base, because the characters `o,r,c,h,…` are each truthy and none equals `"orchestrator"`. So the base guard could be defeated by the very identity R350 exists to exclude, and a single-character roster `"x"` passed too. A `dict` also passed (iterating keys). This is a genuine fail-open in a fail-closed guard. **The fix closes all of them**, and mutant C proves the closure is test-enforced. Disclosing this rather than folding it in silently was the right call.

### Security posture

No new attack surface. No env var, no flag, no CLI option, no task-id special case. The exception cannot be reached without the general roster check passing first. The controls that actually protect integrity are byte-identical: `gate()` still refuses `orchestrator` as an independent reviewer (`tools/project_control.py:887-888`), still refuses unrostered reviewers, and still refuses a producer gating its own task; `accept()` still requires a submit record whose `content_manifest_sha256` matches the live identity, so the pre-existing `blocked → awaiting_gate` shortcut cannot be used to skip evidence.

## Defects

**None in the product code.** The following are ledger/report hygiene items.

**C1 — AS-12 literal containment miss (owner: orchestrator, not the producer).**
`git diff --name-only 4da0d52..HEAD` lists two files outside the packet's `allowed_paths`:

- `project-control/reports/M0-T033-evidence-map.json` (commit `8fd0019`). This file is **mandated by the CLI**: `tools/project_control.py:437-441` — *"in-regime submit requires --evidence-map (JSON in project-control/reports/ mapping each applicable requirement id to evidence)"*. The packet requires the lifecycle that requires this file, but omits the path.
- `project-control/state.json` (commit `1e86cd7`), written automatically by `sync_state()` during the orchestrator's own `submit`. The packet lists `state.json` under `forbidden_paths` while simultaneously mandating the lifecycle (R372) that writes it — internally inconsistent.

**The producer's own commit `6592b89` touched exactly three files, all inside `allowed_paths`.** Producer containment is clean. This is a packet-drafting defect authored by the orchestrator.

*Identity-safety note for whoever fixes this:* adding `project-control/reports/M0-T033-evidence-map.json` to `allowed_paths` does **not** disturb the frozen content identity, because `_MANIFEST_EXCLUDE_PREFIXES = ("project-control/",)` excludes it from the manifest. I verified the digest is driven only by `tools/project_control.py`, `tools/test_project_control.py`, `docs/GATES_AND_CHECKPOINTS.md`. Amending is therefore safe; alternatively record an explicit deviation note and amend at the next natural point. Either satisfies C1 — but it must not pass silently.

**C2 — producer report §6.5 containment table is stale.** Lines 654-668 predate the evidence-map commit and assert *"No file outside `allowed_paths` was modified"* and *"`state.json` … untouched"*. Both are true of the producer's code commit but no longer of the branch. Annotate.

**C3 — OQ-2 framing understated.** Report §3 (lines 299-309) describes the whitespace tightening as affecting `" orchestrator "` only. It also newly refuses producer-name whitespace evasion (`[" backend-x "]` vs producer `backend-x`) and whitespace-only reviewer names. Correct the description.

## Observations (non-blocking, no action required)

- **OBS-1 — S10 block 6 precision gap.** Block 6 asserts `returncode != 0`, no `Traceback`, and `"amend" in stderr`. `"amend"` appears in *every* roster refusal, so the block proves fail-**closed** but not fail-closed-**for-the-stated-reason**. Proven empirically: I built a mutant that silently reads malformed input as an empty list (no explanatory error) and **S10 still passed**. The undetected variant is itself fail-closed, and R367's actual text ("fails closed WITHOUT a traceback") *is* verified, so this is a precision note, not a defect. Asserting `"malformed" in r.stderr` for the malformed cases would close it.
- **OBS-2 — gate-id normalization asymmetry.** `_roster_strings` strips `required_gates`, so `[" G3 "]` satisfies the independent-gate condition, while `accept()` compares raw values. Unreachable through the CLI (the `--gates` enum rejects `" G3"`), and the divergence fails closed at accept. Cosmetic.
- **OBS-3 — evidence map carries `reviewed_sha: null` and `content_manifest_sha256: null`.** Inert: the binding identity lives in the submit record `project-control/reports/M0-T033.json` (`cd8f93b7…` / `8fd0019…`), which I recomputed and confirmed. All `project-control/` artifacts are manifest-excluded by design.
- **OBS-4 — minor line-citation drift** in report §2 (cites `test_project_control.py:1764-1775` for the normal-producer loop; the actual loop is ~1795-1810). Substance verified directly; citations are a few lines off.
- **OBS-5 — pre-existing, out of scope.** `accept()` does `set(t.get("required_gates") or [])`, which raises `TypeError` on a non-iterable. Fail-closed but untidy. Identical at base; `accept` is byte-unchanged. Noted only so it is not mistaken for new.

## Required rework

None to the code. **C1, C2 and C3 are corrections, blocking for acceptance** per the gate-verdict semantics in `.claude/rules/project-control.md` (PASS-with-corrections is recorded as PASS; corrections must be applied and validated before the next gate and before acceptance, via `progress --message`, never by hand-editing control files).

## Reviewer conclusion

**PASS.**

I set out to break this change and could not. The four conditions are genuinely conjunctive — proven not by reading the happy path but by exhausting 143,640 input shapes against the base implementation, which showed **756** newly-passing shapes, **all** of them the single intended case, and **zero** raises. The correction is general, not a disguised special case: it is driven purely by packet shape, and its effect on the real ledger is exactly three tasks, two of them terminal and inert. The original M0-T014 G3 OBS-3 protection is intact. There is no hard-coded task id, no flag, no environment escape, and `INDEPENDENT_GATES` is reused rather than re-listed. `gate()`, `submit()`, `accept()`, `claim()`, `progress()` and the directive-verification path are byte-identical — 33 of 34 shared functions unchanged.

The tests are honest and they bind: six independent mutants each broke S10 in the block that covers the disabled condition, and the unmutated control passed. The execution recorder covers all 10 blocks and the exact label/count sequence is genuinely asserted, not merely accumulated. The evidence map matches the canonical resolver-derived set exactly, 52 for 52, which I re-derived rather than accepted.

The producer's F-1 disclosure is not only true but understated — at base, a roster consisting solely of the string `"orchestrator"` passed the guard it was supposed to be excluded by. Finding that, and reporting it as a finding rather than quietly folding it into the diff, is the behaviour the evidence regime is meant to produce. The same is true of the three open questions and the two preserved STOPs: the producer declined to self-certify anything it was not entitled to settle, which is why this gate had something real to rule on.

Rulings: **OQ-1 — R368 dominates, leave as built. OQ-2 — acceptable and in scope, but restate its true breadth. OQ-3 — accept the producer's reading; R345 is satisfied absolutely. Negative controls — no re-run required; premise verified by blob hash and superseded by my own six.**

The only shortfalls are documentary, and the containment one belongs to the packet's author rather than to the producer. They must be recorded and corrected before acceptance, but none of them touches behaviour, and none of them justifies withholding this gate.
