# M0-T033 — G5 INDEPENDENT SECURITY REVIEW

> **Orchestrator preservation note.** The body below is the `security-reviewer` return preserved
> **VERBATIM** per `.claude/rules/project-control.md` (report-preservation rule), with transport
> entity-decoding only (`&lt;`/`&gt;`/`&amp;` restored to `<`/`>`/`&`). Nothing was added, removed,
> condensed, or reworded. The reviewer was dispatched read-only on explicit Opus 5 under the
> D-004-R307 availability exception.
>
> **Dispatch history (D-004-R411).** A first G5 spawn died mid-run on an API connection error just
> as it began a mutation test. The orchestrator verified NO working-tree contamination (both
> `tools/` blobs byte-identical to HEAD) and re-dispatched with an explicit instruction to mutate
> only a copy outside the repo. This report is from the re-dispatch; the crashed spawn's partial
> output was discarded and never used as evidence.
>
> The reviewer states it could not use `Write` (read-only enforced) and returned the report through
> the agent channel; the orchestrator saved it here verbatim, as the report-preservation rule
> requires.

---

# Gate Report

- **Gate ID:** G5 (independent security review)
- **Task ID:** M0-T033 — Governance-orchestrator unblock-roster semantics
- **Reviewer:** `security-reviewer` (independent; NOT the producer)
- **Producer:** `backend-engineer`
- **Result: PASS** — with 0 critical, 0 high, 0 medium open defects. Three low/informational observations, none blocking.
- **Clean environment/worktree used:** Primary checkout at the frozen reviewed identity; no repo file modified by this review (proof in §8).
- **Model actually running this review:** Opus 5, exact model id `claude-opus-5[1m]`, under the D-004-R307 availability exception.

## 0. Identity verification (first action)

```
$ git rev-parse HEAD
6dec7a5b6793d188d2627c9f9661c4a19ce8f2fd          <-- MATCHES the frozen reviewed identity

$ git rev-parse --abbrev-ref HEAD
task/M0-T033-unblock-roster-semantics
```

Content-identity delta confirmed independently:

```
$ git diff --name-only 1e86cd7..HEAD
project-control/reports/M0-T033.json
```

The only change from the earlier reviewed commit `1e86cd7` to HEAD is the CLI submit record under `project-control/`, which the content manifest excludes. Code blobs are byte-identical across the whole base progression:

```
170478e  tools/project_control.py = 70a5a865b2f13f841b33adeb73ce6fa2156caf41
abb89b8  tools/project_control.py = 70a5a865b2f13f841b33adeb73ce6fa2156caf41
1e86cd7  tools/project_control.py = 6b7d3ac7b52ea3444682a08d818f81541102c2a6
HEAD     tools/project_control.py = 6b7d3ac7b52ea3444682a08d818f81541102c2a6

tools/test_project_control.py: 14a145e1… at abb89b8/170478e/4da0d52 -> 1b5fe813… at 6592b89/1e86cd7/HEAD
```

I proceeded. The producer report was treated as unverified claims throughout; every number below is one I reproduced.

## 1. Acceptance criteria reviewed

AS-1 through AS-12 from `project-control/tasks/M0-T033.json`, plus the seven judgment areas named in the dispatch. All twelve are satisfied; evidence is mapped per-item in §3 and §5.

## 2. Required test run (verbatim, untruncated)

```
$ python tools/test_project_control.py
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

exit code 0
```

**Confirmed: 15/15 groups and `10/10 blocks executed`, 118 assertion cases, exit 0.** Registry validator (AS-10 second half):

```
$ python tools/validate_directive_compliance.py --check ; echo "REAL EXIT: $?"
REAL EXIT: 0
```

## 3. Adversarial analysis — the seven judgment areas

### 3.1 PRIVILEGE ESCALATION — no escalation; the guard was never the binding constraint

This is the central finding and it is **not visible in the diff**. `invalid_unblock_roster` is reachable from exactly one place, `tools/project_control.py:778`:

```python
if cur == "blocked" and target != "canceled":
    roster_err = invalid_unblock_roster(t)
```

It fires only on a **status change out of `blocked` to a non-`canceled` target**. Meanwhile `claim()` at `tools/project_control.py:640` sets the producer with **no reserved-identity check whatsoever**:

```python
t.update({"producer_agent": a.agent, "worktree": a.worktree,
          "status": "claimed", "progress_percent": 10})
```

I also read `_directive_claim_check` (`tools/project_control.py:392`) — its `agent` parameter is **never referenced in the body**; it validates directive refs and governance-path coverage only, never identity.

Consequence: `claim --agent orchestrator` has always been accepted for any claimable task of any type, and such a task then runs `ready -> claimed -> in_progress -> self_check -> awaiting_gate -> accepted` **without ever encountering this guard**. The prohibition being relaxed was therefore never a general ban on orchestrator-as-producer; it was a narrow rail on one transition, added for legacy blocked packets (M0-T014 G3 OBS-3). Relaxing it grants an adversary **no capability they did not already hold by a shorter route**.

**Worst reachable outcome, modelled.** For a hand-edited packet shaped as `task_type=governance, producer_agent=orchestrator, required_gates=[G5], reviewer_agents=[X]` to reach `accepted`, `accept()` (byte-identical to base, §3.7) requires a PASS `G5` record whose `role == "independent_review"` and whose `reviewer != producer`. `gate()` (byte-identical) refuses `reviewer == "orchestrator"` for every independent gate unconditionally, refuses `reviewer == producer`, and refuses any reviewer absent from `reviewer_agents`. So the orchestrator label **cannot** record the gate that unblocking now requires. The loop is closed at gate-record-creation time.

Sharper still: the new path is the **only** path in the module that *forces* `required_gates` to contain an independent gate. A task claimed the ordinary way may carry `required_gates: []` and face no independent gate at all. Naming the orchestrator honestly is therefore **strictly more constrained** than the rejected option (a) of naming a fictional producer.

Residual, and pre-existing: forging the outcome requires hand-writing `project-control/gates/<task>-G5.json`, which defeats every guard in the module equally. The module discloses this at lines 4–12: *"there is no authentication or signature. The enforcement model is procedural."* Unchanged here.

**Verdict: no privilege escalation. "governance + one independent gate + one usable reviewer" is a sufficient barrier for the capability actually granted, which is narrow: un-sticking an already-`blocked` packet.**

### 3.2 SEPARATION OF DUTIES — intact, mechanically proven

AST-level comparison of every function in the module, base vs HEAD:

```
TOTAL functions base=34 head=36
ADDED  : ['_orchestrator_governance_exception', '_roster_strings']
REMOVED: []
CHANGED: ['invalid_unblock_roster']

gate                     IDENTICAL
submit                   IDENTICAL
accept                   IDENTICAL
claim                    IDENTICAL
new_task                 IDENTICAL
progress                 IDENTICAL
main                     IDENTICAL
_task_git_identity       IDENTICAL
_directive_claim_check   IDENTICAL
_task_in_regime          IDENTICAL
_regime                  IDENTICAL
```

`gate()` still refuses a producer-authored independent record (`tools/project_control.py:892`, `"Producer cannot independently gate own task."`) and the reserved identity (`:887-891`). `accept()` still rejects `rec.get("reviewer") == producer` for independent gates (`:998-1000`). The usable-reviewer computation still excludes the producer (`tools/project_control.py:742-743`). Test block 9 exercises all of this against the real CLI on a task that used the new path, and it is one of the 10 blocks proven to execute.

**Cannot reach `accepted` with no genuinely independent gate via the new path.**

### 3.3 FAIL-CLOSED — `_roster_strings` attacked, nothing raises or coerces

```
bare string reviewers F1   REFUSE  reviewer_agents is malformed (expected a list of strings, got st
dict reviewers             REFUSE  reviewer_agents is malformed (expected a list of strings, got di
int reviewers              REFUSE  reviewer_agents is malformed (expected a list of strings, got in
None reviewers             REFUSE  reviewer_agents has no usable independent reviewer (must be non-
nested list                REFUSE  reviewer_agents is malformed (entry ['r'] is not a string); amen
list with None             REFUSE  reviewer_agents is malformed (entry None is not a string); amend
list with dict             REFUSE  reviewer_agents is malformed (entry {'x': 1} is not a string); a
list with int              REFUSE  reviewer_agents is malformed (entry 1 is not a string); amend th
bool reviewers             REFUSE  reviewer_agents is malformed (expected a list of strings, got bo
tuple reviewers            PERMIT (allow)
producer list              REFUSE  producer_agent is malformed (expected a string, got list); amend
producer dict              REFUSE  producer_agent is malformed (expected a string, got dict); amend
producer int               REFUSE  producer_agent is malformed (expected a string, got int); amend
producer bool              REFUSE  producer_agent is malformed (expected a string, got bool); amend
producer None              REFUSE  no producer_agent is set; amend the packet with a producer befor
producer absent            REFUSE  no producer_agent is set; amend the packet with a producer befor
empty packet               REFUSE  no producer_agent is set; amend the packet with a producer befor
```

Zero exceptions escaped across all 17 shapes. The single `PERMIT` is a **tuple of well-formed strings**, which is a valid roster by construction and is unreachable from JSON (`json.load` never produces tuples). Not a defect.

Orchestrator-exception path, 28 shapes:

```
INTENDED gov+O+G5+rev        PERMIT (unblocks)
gov+O+G1 only                PERMIT (unblocks)
engineering+O                REFUSE   task_type is not governance
task_type absent/None/int/list/dict+O   REFUSE  (all four)
task_type GOVERNANCE upper   REFUSE   (case-sensitive)
task_type governance-x       REFUSE
gov+O no indep gate (G0/G2/G7)          REFUSE
gov+O gates absent/None/bare-str/dict/int/nested/None-elem   REFUSE (all seven)
gov+O gates g5 lower         REFUSE   (gate ids case-sensitive)
gov+O EMPTY reviewers        REFUSE
gov+O reviewers=[orchestrator]          REFUSE
gov+O reviewers '  orchestrator  '      REFUSE   <-- whitespace evasion closed
gov+O reviewers '   ' / ''   REFUSE
```

The four conditions are genuinely conjunctive, and the orchestrator branch at `tools/project_control.py:748-749` is reachable **only after** the general usable-reviewer check has already passed — so condition 3 cannot be skipped.

The only additional `PERMIT`s were whitespace-normalized restatements of the intended packet (`' governance '`, `[' G5 ']`, `'  orchestrator '` as producer). These are semantically the same packet, not a bypass. **Ruling on the disclosed whitespace-stripping tightening: ACCEPT.** It is monotonically tightening on the reviewer side — it is precisely what makes D-004-R350 ("a roster containing only orchestrator remains invalid") actually hold, which it did not at base.

### 3.4 OQ-1 — the required explicit ruling (D-004-R415)

**Reproduced the asymmetry first.** Differential table, base vs HEAD, produced by loading both revisions in one process:

```
case                       BASE           HEAD           DELTA
F1 bare str rev            PERMIT         REFUSE         <<< CHANGED
F1 bare str = orchestr     PERMIT         REFUSE         <<< CHANGED
whitespace only rev        PERMIT         REFUSE         <<< CHANGED
padded orchestrator rev    PERMIT         REFUSE         <<< CHANGED
padded producer rev        PERMIT         REFUSE         <<< CHANGED
rev list with int          PERMIT         REFUSE         <<< CHANGED
rev list with None         REFUSE         REFUSE
rev dict                   PERMIT         REFUSE         <<< CHANGED
producer as list           RAISE:AttributeError REFUSE   <<< CHANGED
producer as int            RAISE:AttributeError REFUSE   <<< CHANGED
normal ok                  PERMIT         PERMIT
normal self review only    REFUSE         REFUSE
gov + O + G5 + rev         REFUSE         PERMIT         <<< CHANGED   <-- the ONE intended loosening
eng + O                    REFUSE         REFUSE
CASE Orchestrator          PERMIT         PERMIT
non-O malformed gates      PERMIT         PERMIT         <-- OQ-1 asymmetry
non-O gates dict           PERMIT         PERMIT         <-- OQ-1 asymmetry
non-O task_type int        PERMIT         PERMIT         <-- OQ-1 asymmetry
```

**Every delta is a tightening except exactly one, which is the intended case.** The asymmetry is real and confirmed.

**RULING: D-004-R368 DOMINATES. R352 is not violated. No change is required.**

Three independent grounds, in order of weight:

**(a) The proposed extension would close zero exploitable paths, because the permissive outcome is reachable through well-formed values.** `required_gates` has exactly one downstream security consumer, `accept()` at `tools/project_control.py:988`: `for g in sorted(set(t.get("required_gates") or []))`. I evaluated that expression on every malformed shape:

```
'G5'                 ['5', 'G']          -> lookup miss, accept appends a refusal reason
{'a': 'G5'}          ['a']               -> lookup miss, accept refuses
[['G5']]             RAISES TypeError    -> abort, never accepts
[]  ''  None  0      []                  -> loop body never runs (zero gates checked)
['G5','G3']          ['G3', 'G5']        -> enforced normally
```

Single-character elements can never match a gate id, so every *non-empty* malformed shape makes `accept()` fail **loudly**. The only permissive shape is a **falsy** one — and `_roster_strings([])` and `_roster_strings(None)` both return `([], None)`, i.e. **valid**. So extending the validation to the non-orchestrator path would not catch `[]` or `None` at all. An attacker who can write the packet simply writes `required_gates: []` and the extended check waves it through identically. A control an adversary bypasses with a well-formed value is not a security control.

**(b) The unblock transition is structurally the wrong enforcement point.** The guard is reachable only from `blocked` (`:778`). Any `required_gates` invariant enforced there is bypassed by the trivial expedient of never being blocked — which is the normal path for every task. Adding the check would create coverage that looks broad and is in fact conditional on an incidental status, which is worse than not having it: it invites reliance. The correct locations for that invariant already exist and are untouched — `new_task()` validates `--gates` against the `GATE_IDS` enum at creation (`:536-540`), and `accept()` consumes it.

**(c) The directive text supports R368 on its own terms.** Verbatim from `project-control/directives/D-004-agent-teams-runtime-adoption/requirements.json`:

- **D-004-R352:** "PRESERVE DEFAULT: malformed **roster** data fails CLOSED."
- **D-004-R367:** "TEST 6: malformed **reviewer** data fails closed WITHOUT a traceback."
- **D-004-R368:** "TEST 7: normal non-orchestrator producer behavior remains **unchanged**."

R352's subject is *roster* data, and R367 — the requirement that operationalizes R352 as an executable test — narrows it further to *reviewer* data. `required_gates` is gate-requirement data and `task_type` is classification data; neither is roster data on any reading. And for the fields R352 does govern (`producer_agent`, `reviewer_agents`), the differential table above proves fail-closed behavior on **every** path including the non-orchestrator one. **There is no actual conflict to resolve.** Conversely, extending validation to normal producers would newly refuse packets that unblock today — a direct violation of R368's "unchanged".

I note that R352 is phrased as "PRESERVE DEFAULT", yet the base did **not** fail closed (see F-1). The producer had to *establish* the default rather than preserve it, and did so for roster data universally. That over-delivers on R352 rather than shortchanging it.

**Independence statement:** I produced the differential table and the `accept()` analysis before reading any other reviewer's position; the orchestrator's progress-log entry recording the control-plane-verifier and code-reviewer rulings appeared in my working tree only at the end of the review (§8) and I read it after forming this conclusion. My grounds (a) and (b) are not in their reasoning as summarized; ground (c) partially overlaps. I reach the same verdict by a different and, I believe, stronger route: the decisive point is not merely that `accept()` fails loudly, but that the proposed control is **defeated by a well-formed value** and sits on a transition most tasks never traverse.

### 3.5 FINDING F-1 — pre-existing fail-open: genuinely exploitable at base, now closed

**Confirmed exploitable.** Base code was `reviewers = task.get("reviewer_agents") or []`, then `usable = [r for r in reviewers if r and r != RESERVED_ORCHESTRATOR and r != producer]`. A bare string iterates character-wise: `"rev-a"` -> `['r','e','v','-','a']`, all truthy, none equal to `"orchestrator"` or the producer -> non-empty `usable` -> **PERMIT**. Reproduced above: `F1 bare str rev  BASE PERMIT / HEAD REFUSE`.

**More severe than the producer disclosed, and I reproduced the sharper case independently:** `reviewer_agents = "orchestrator"` (a bare string naming *only* the reserved identity) also **PERMITTED at base** — the character set `{'o','r','c','h','e','s','t','a'}` contains no element equal to `"orchestrator"`. The base guard could be defeated by the exact identity D-004-R350 exists to exclude. Two further base fail-opens I found that the producer did not name: a whitespace-only reviewer `['   ']` and a padded `['  orchestrator  ']` both **PERMITTED at base**, both **REFUSED at HEAD** via the new `.strip()`. And `producer_agent` as a list or int **raised an uncaught `AttributeError`** at base (traceback to the operator) rather than returning an explanatory refusal.

**Severity: MEDIUM at base — now CLOSED.** Medium rather than high because exploitation presupposes write access to the task packet, and an actor with that access has a shorter legitimate-looking route (write any plausible producer/reviewer name). Its real weight is as an *integrity* defect: a plausible hand-edit or legacy typo (string instead of list) silently defeated the M0-T014 G3 OBS-3 protection with no diagnostic. The fix closes all five variants I tested. **This change is a net security improvement independent of the feature it enables.**

### 3.6 NO ESCAPE HATCH — confirmed

```
$ grep -n "os.environ\|getenv\|environ\|import os\|sys.argv\|--force\|--override\|--bypass\|--allow" tools/project_control.py
723:    There is no special-cased task id, no flag, and no environment override.
```

The sole hit is prose inside the `invalid_unblock_roster` docstring. `os` is imported (line 85) but used **only** for atomic file replacement — `os.replace`, `os.fdopen`, `os.unlink` at lines 157/175/180. No `os.environ`, no `os.getenv`, anywhere in the module.

CLI surface: the diff contains **zero** `argparse` / `add_parser` / `add_argument` changes (grep over the diff returned no matches), and `main()` is AST-identical to base. The `progress` subparser (`tools/project_control.py:1129-1139`) exposes exactly `--task-id`, `--agent`, `--percent`, `--status`, `--message`. No task-id special case: `grep -c "M0-T027" tools/project_control.py` returns `0`. The two task-id strings remaining in the module (`M0-T014 G3 OBS-3` at :704, `M0-T033` at :46) are provenance citations inside docstrings and are used in no conditional — the suite proves this structurally at `tools/test_project_control.py:1898` by AST-unparsing the three guard functions with docstrings stripped and asserting no `M\d+-T\d{3}` survives.

### 3.7 SCOPE — nothing outside authorization changed

```
$ git diff --name-only abb89b8..HEAD | grep -E "^(\.claude/|\.github/|services/|apps/|packages/|render\.yaml|CLAUDE\.md)"
(exit 1 — no matches)

$ git diff --exit-code abb89b8..HEAD -- docs/GATES_AND_CHECKPOINTS.md
(exit 0 — BYTE-IDENTICAL)

$ git diff --name-only abb89b8..HEAD -- project-control/tasks/M0-T027.json
(no output — untouched, D-004-R374/R419 satisfied)
```

Producer's own commit containment:

```
$ git show --name-only 6592b89
project-control/reports/M0-T033-producer-report.md
tools/project_control.py
tools/test_project_control.py
```

Exactly three files, all inside `allowed_paths`. All other changed files in the range are orchestrator lifecycle/directive-registry writes.

**I independently verified the conditional-doc decision rather than accepting it.** `docs/GATES_AND_CHECKPOINTS.md` contains **no** mention of `producer_agent`, `reviewer_agents`, or `invalid_unblock_roster` (grep exit 1). Its only adjacent invariant is line 5, *"No producer approves its own work. A task becomes accepted only after its required gates pass and the orchestrator records the acceptance."* — which the change **preserves** (§3.2). No stated invariant is contradicted, so leaving the file byte-identical is correct.

`tools/test_project_control.py` is **purely additive**: `git diff … | grep "^-" | grep -v "^---"` returns nothing (exit 1). Zero deleted lines — the pre-existing S8 roster tests are unmodified in *bytes*, not merely "in substance", which is stronger than AS-1 requires.

## 4. Standard security-check sweep

Scan of the code diff for secret/network/injection surface:

```
$ git diff abb89b8..HEAD -- tools/ | grep -inE "password|secret|token|api[_-]?key|service[_-]?role|supabase|http://|https://|requests\.|urllib|socket|subprocess|eval\(|exec\(|pickle|os\.system|shell=True|__import__"
175:+      no environment/bypass/override token; `progress` gains no new option.
187: import subprocess          <-- CONTEXT line (pre-existing), test harness invoking the CLI under test
495:+                f"guard executable code must carry no {tok!r} token:\n{code}"
```

All three are benign prose/assertion text; `import subprocess` is an unchanged context line.

| Check | Ruling |
|---|---|
| Cross-tenant isolation | **N/A** — no tenant model, no DB, no request context in this diff. Local single-user control plane. |
| Service-role secrecy | **PASS (N/A)** — no credentials, no Supabase client, no key material introduced or referenced. |
| Private storage | **N/A** — no object storage or bucket policy touched. |
| SSRF | **PASS (N/A)** — no outbound network call, no URL parsing, no fetch of any kind in the module. |
| Injection | **PASS** — no SQL, no shell, no `eval`/`exec`/`pickle` on untrusted data, no `shell=True`. The one dynamic construct is `ast.parse` over the tool's *own* source in the test file. |
| Upload controls | **N/A** — no file upload path. |
| Prompt-injection defenses | **PASS** — no LLM call, no prompt construction, no untrusted text routed to a model. Note the packet text *is* attacker-influenceable and is surfaced in error strings, but only to stderr, never to a model. |
| Least privilege | **PASS, and improved.** The relaxation is the narrowest that satisfies the owner's option (b); it is the only code path that *forces* an independent gate to be required. See §3.1. |
| Log redaction | **PASS.** Error messages interpolate attacker-controlled packet values, but every string-valued interpolation uses `!r` (`repr`), which escapes newlines and control characters — so stderr/log-injection via a crafted `task_type`, reviewer name, or nested value is blocked. `f"…required_gates {gates}…"` (`:692-693`) formats a *list*, whose `str()` calls `repr()` on each element, so it is escaped too. No secrets exist in the data to redact. |

## 5. Security-bearing requirement verification

Reproduced at reviewed identity `6dec7a5b6793d188d2627c9f9661c4a19ce8f2fd` / content identity `cd8f93b76116c1e43b84bb0aa54f5ad621ddc16ae5e0a932cdfe86f65a8e1665`. This covers the rows in G5's security remit; the exhaustive 52-row pass over all applicable D-004 rows is the `directive-compliance-verifier`'s gate (producer ≠ verifier) and I do not duplicate or pre-empt it.

| Requirement ID | Verdict | Reproduced evidence |
|---|---|---|
| D-004-R344 (correct GENERALLY) | PASS | AST proof, `test_project_control.py:1898`; no task-id in guard executable code |
| D-004-R345 (no M0-T027 hard-code) | PASS | `grep -c "M0-T027" tools/project_control.py` = 0 |
| D-004-R346 (no bypass flag) | PASS | §3.6 — zero argparse deltas; `progress` options unchanged; no env read |
| D-004-R347 (missing producer invalid) | PASS | §3.3 rows `producer None` / `producer absent` / `empty packet` |
| D-004-R348 (non-governance + orchestrator invalid) | PASS | §3.3 `engineering+O` REFUSE; suite block 1 = 32 cases incl. `"Governance"`, `"gov"`, `""` |
| D-004-R349 (empty roster invalid) | PASS | §3.3 `gov+O EMPTY reviewers` REFUSE; suite block 3 |
| D-004-R350 (orchestrator-only roster invalid) | PASS | §3.3 `reviewers=[O]` and `'  orchestrator  '` both REFUSE; **base PERMITTED the padded form** |
| D-004-R351 (producer-only roster invalid) | PASS | §3.4 `normal self review only` REFUSE at both revisions |
| D-004-R352 (malformed roster fails closed) | PASS | §3.3 (17 shapes) + §3.4 differential; ruled on in §3.4 |
| D-004-R353 (blocked->canceled permitted) | PASS | Suite block 8 = 12 cases, incl. malformed producer/reviewer shapes |
| D-004-R361 (no weakening of gate/submit/accept/verification/identity/separation) | PASS | §3.2 AST hash table — all IDENTICAL; only 1 function changed, 2 added, 0 removed |
| D-004-R362 (AS-1) | PASS | Suite block 1, 32 cases executed |
| D-004-R363 (AS-2) | PASS | Suite block 2, 9 cases; all five independent gate ids exercised |
| D-004-R364 (AS-3) | PASS | Suite block 3, 2 cases |
| D-004-R365 (AS-4) | PASS | Suite block 4, 3 cases |
| D-004-R366 (AS-5) | PASS | Suite block 5, 6 cases |
| D-004-R367 (malformed fails closed, no traceback) | PASS | Suite block 6, 31 cases; my §3.3 sweep produced zero exceptions |
| D-004-R368 (normal producer unchanged) | PASS | §3.4 differential — `normal ok` and `normal self review only` unchanged; ruled dominant |
| D-004-R369 (AS-8) | PASS | Suite block 8, 12 cases |
| D-004-R370 (independent reviewer ≠ producer) | PASS | Suite block 9, 8 cases against the real CLI; `gate()` AST-identical |
| D-004-R371 (full suites green) | PASS | §2 — 15/15 exit 0; validator exit 0 |
| D-004-R413/R414 (execution proof, not presence of code) | PASS | `10/10 blocks executed`; exact ordered `(label,count)` sequence asserted at `test_project_control.py:1943`; total pinned at `:1947` |
| D-004-R415 (explicit independent ruling on the asymmetry) | PASS | §3.4 — explicit ruling delivered with independent grounds |

## 6. Negative-control ruling (explicitly requested)

**RULING: re-running the three negative controls is NOT REQUIRED.** I verified the premise rather than accepting it.

The controls were run against a guard whose blob was `6b7d3ac7b52ea3444682a08d818f81541102c2a6` — **identical to the HEAD blob**. Independently, I matched every traceback line number quoted in the producer report against the HEAD test file:

```
$ sed -n '1664,1666p' tools/test_project_control.py        # NC-1 cites line 1665
                r = unblock(tid, target)
                assert r.returncode != 0, \
                    f"task_type {ttype!r} + orchestrator producer must not unblock to {target}"

$ sed -n '1732p' tools/test_project_control.py             # NC-2 cites line 1732
            assert r.returncode != 0, f"required_gates {gates!r} has no independent gate"

$ sed -n '1769,1770p' tools/test_project_control.py        # NC-3 cites line 1769
            assert r.returncode != 0, \
                f"malformed {label} {fields!r} must fail closed, not unblock"
```

All three match exactly — line number, assertion text, and the reported failing value. NC-2's `required_gates []` is the first element of block 5's loop `([], ["G0"], …)`; NC-3's reported dict is byte-for-byte the first element appended to `malformed` at `:1747-1749`. The controls demonstrably executed against **byte-identical** test content, and the base advance (`170478e -> 4da0d52`) touched only `project-control/` files, which S10 never reads (it builds its own ledger in a temp dir). A re-run would be a no-op by construction.

No injected artifact survives, verified by me at HEAD:

```
$ grep -rn "if False\|NEGATIVE CONTROL\|NC-1\|NC-2\|NC-3" tools/ ; echo "exit: $?"
exit: 1     (absent — correct)
```

## 7. Findings

**No critical. No high. No open medium.**

| ID | Severity | Status | Detail |
|---|---|---|---|
| F-1 | MEDIUM | **CLOSED by this change** | Pre-existing fail-open in `invalid_unblock_roster` at base (`tools/project_control.py:667` at `abb89b8`). Bare-string `reviewer_agents` iterated character-wise and passed; `"orchestrator"` as a bare string passed; whitespace-only and padded-reserved reviewers passed; non-string `producer_agent` raised an uncaught `AttributeError`. Repro in §3.5. **Remediation already applied** by `_roster_strings` (`tools/project_control.py:648-666`) + the `producer_agent` type check (`:729-732`). Verified closed. |
| OBS-1 | LOW (informational) | Pre-existing, **out of scope**, unchanged | `tools/project_control.py:988` — `accept()` enforces **zero** required gates when `required_gates` is falsy (`[]`, `""`, `None`, `0`). `accept` is AST-identical to base, so this diff neither introduces nor worsens it, and the new orchestrator path is the one place that *prevents* it. Reachable only by hand-editing a packet, which is outside the module's disclosed threat model (`:4-12`). **Recommendation:** consider a follow-up task adding a non-empty `required_gates` assertion in `accept()` and/or `new_task()`. **Not a blocker for G5.** |
| OBS-2 | LOW (informational) | Pre-existing, unchanged | Reserved-identity comparison is exact-match, so a case variant (`"Orchestrator"`) is not recognized as reserved — `PERMIT` at both base and HEAD (§3.4). No security impact: the label is procedural, any non-reserved label unblocks anyway, and `gate()`/`accept()` compare against the same exact string consistently, so no split-brain arises. Noted for completeness only. |
| OBS-3 | LOW (informational) | Orchestrator-authored; already self-acknowledged as C1 | `project-control/tasks/M0-T033.json` `allowed_paths` omits `project-control/reports/M0-T033-evidence-map.json`, which `_directive_submit_check` mandates for an in-regime submit; and `forbidden_paths` lists `state.json`, which `sync_state()` necessarily writes. This is packet-drafting inconsistency, not a capability grant — it confers no privilege on the producer, whose commit `6592b89` touched only allowed paths. **Not a G5 blocker.** |

Also noted, no severity: `_directive_claim_check(t, agent)` at `tools/project_control.py:392` accepts an `agent` parameter that is never referenced in its body. Pre-existing, AST-identical to base, harmless — but it is worth knowing that no identity restriction exists at claim, since that fact is load-bearing for §3.1.

## 8. Reviewer read-only attestation

I ran no `tools/project_control.py` subcommand, no git write, no `gh`, and no write-producing shell command. The read-only guard blocked three of my attempts (a shell redirect, and two `python tools/project_control.py progress -h` invocations); I worked around them with read-only inspection rather than escalating, and the `Write` tool is not enabled in this context.

I mutated **nothing**. Proof that the code is byte-identical to HEAD after all my testing:

```
$ git hash-object tools/project_control.py       -> 6b7d3ac7b52e   (HEAD: 6b7d3ac7b52e)  IDENTICAL
$ git hash-object tools/test_project_control.py  -> 1b5fe813a00c   (HEAD: 1b5fe813a00c)  IDENTICAL
$ git diff --stat -- tools/                      -> (empty, exit 0)
```

All adversarial testing was done by importing the module and calling the **pure** helpers (`invalid_unblock_roster`, `_roster_strings` — no I/O, no side effects), and by loading the base revision via `git show` + `exec` into a throwaway namespace in memory. `python -B` was used so no `__pycache__` was written into the repo.

**Working-tree note for the orchestrator (not my doing):** during my review, `project-control/state.json` and `project-control/tasks/M0-T033.json` became modified. I diffed both: the only changes are an `updated_at` timestamp and one new `progress_log` entry authored by `agent: "orchestrator"` at `2026-07-30T17:39:42Z` recording the two returned reviews. That is your own concurrent lifecycle write, it is uncommitted, and it does not affect the reviewed content identity (`project-control/` is manifest-excluded). Flagging it so it is not mistaken for reviewer contamination.

## 9. Reviewer conclusion

**PASS.**

The change is the narrowest correction that satisfies the owner's option (b), and I was unable to construct a privilege escalation from it. The decisive point is structural and lies outside the diff: `claim()` never restricted the reserved identity and the guard fires only on the `blocked` exit, so orchestrator-as-producer was always reachable by a shorter route — this relaxation removes an over-broad rail on one transition rather than granting new authority. Everything that actually enforces separation of duties (`gate()`, `accept()`) is proven AST-identical to base, and the new path is uniquely *stricter* than every other path in requiring an independent gate to exist at all. Independent review of orchestrator-produced governance evidence therefore remains structurally guaranteed, and this very report — produced by a reviewer that is neither the producer nor the orchestrator — is an instance of it.

Net security posture **improves**: the change closes a real pre-existing fail-open (F-1) that let a malformed packet — including one naming only the reserved identity — defeat the roster check entirely, and it converts two uncaught tracebacks into explanatory refusals.

OQ-1 ruled **FOR D-004-R368**; no change required. Negative controls **need not be re-run**. No rework is required for G5.
