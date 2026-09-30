# M0-T033 — Governance-orchestrator unblock-roster semantics — PRODUCER REPORT

- **Task**: M0-T033 — Governance-orchestrator unblock-roster semantics
- **Producer**: `backend-engineer` (unnamed spawn; roster identity resolved, writes authorized by
  `.claude/hooks/readonly_agent_guard.py` — `backend-engineer` is not in `READ_ONLY_AGENTS`)
- **Model**: Opus 5 — exact model id `claude-opus-5[1m]`, run under the D-004-R307 availability
  exception. Stated explicitly because the D-004 effort/model decision remains open.
- **Frozen base identity**: `4da0d524f1345c7126c8b551014359f9d5548975`
  (base progression, all orchestrator-performed: `abb89b8` -> `170478e` -> `4da0d52`; see §0 and §7.1.
  The code work product is identical across all three — guard blob `6b7d3ac7…` throughout.)
- **Worktree**: `.claude/worktrees/agent-af94933c3b313bae5`, branch `worktree-agent-af94933c3b313bae5`
- **Requested status**: `awaiting_gate`. This report is producer evidence only. It does NOT
  claim the task is complete or accepted — an independent gate decides.

## 0. Failure history, preserved honestly (D-004-R411)

**This task did NOT complete in a single clean pass.** It took three dispatches, two of which
failed before any implementation work began. Recording that plainly, because the stop in (b) is
evidence of the attestation control working as designed and must not be tidied away.

**(a) First dispatch — every write denied.** The producer was spawned WITH a spawn name. Per
`.claude/hooks/readonly_agent_guard.py` (module docstring, lines 6-11 and the fail-closed branch at
lines 354-362), a NAMED spawn carries the runtime spawn name in `agent_type`, so the
`.claude/agents/` roster role is unrecoverable and the identity resolves as spawned-unknown. The
guard then fails CLOSED and governs the agent as read-only, denying every `Write`/`Edit`. No
implementation was possible. This was the orchestrator's dispatch error, stated here as fact and
not as blame; the fix was to re-spawn UNNAMED so the `backend-engineer` roster identity resolves
(`backend-engineer` is not in `READ_ONLY_AGENTS`, lines 52-62).

**(b) Second dispatch — producer STOPPED on a frozen-base identity mismatch.** The dispatch named
branch `task/M0-T033-unblock-roster-semantics` and frozen base `170478e`. That branch was checked
out in the PRIMARY checkout and cannot simultaneously be checked out in an isolated worktree, so
the spawn landed on `worktree-agent-af94933c3b313bae5` at
`abb89b821d3cb7beacc916784c92c9d5570122e0` — an ancestor of the frozen base. The producer verified
identity first, found the mismatch, and **stopped without writing.**

Materially: the producer also determined that all three in-scope files were **byte-identical** at
both commits (blob SHAs `70a5a865`, `14a145e1`, `b250643a`) and that the only divergence was four
control-plane files — i.e. it could have proceeded and produced an identical diff. **It stopped
anyway**, because the attestation condition was stated unconditionally and because this task
concerns a guard that must not be routed around. It also flagged that its copy of
`project-control/tasks/M0-T033.json` was the stale pre-G0 revision (92 lines changed), so the
authoritative acceptance scenarios would have been read from the wrong revision.

**(c) Third dispatch — corrected resume.** The orchestrator fast-forwarded this worktree
`abb89b8 -> 170478e` (four control-plane files only) and re-dispatched. Identity re-verified before
any write:

```
$ git rev-parse HEAD
170478efc34e52f3479d9bb0ac914ad0c364b245

$ git branch --show-current
worktree-agent-af94933c3b313bae5
```

The code work in this report was produced at `170478e` and re-verified unchanged at the final base
`4da0d52`. That fast-forward changed no reviewable input; it changed only four control-plane files
(the G0 record, the G0 readiness report, `state.json`, and the M0-T033 packet).

**(d) Fourth correction — incomplete execution-proof instrumentation.** The orchestrator's
containment review found the R413/R414 instrumentation incomplete (`_rec` wired to blocks 1-5 only,
`executed` never read, no per-block counts printed) while that instrumentation was still being
written. The finding was correct about the file as it stood. It is now complete and re-verified —
see **§5A**, including three negative controls.

**(e) Fifth correction — second base advance for amendment 10.** The producer derived 42 applicable
requirements where the orchestrator's cross-check said 52, and **reported the discrepancy rather
than adopting either number**. Root cause (independently confirmed by the orchestrator): amendment
10 was captured at `836daef`, a CHILD of base `170478e`, so rows R410-R419 did not exist at the
producer's base. The orchestrator then fast-forwarded this worktree `170478e -> 4da0d52`, where the
registry holds 420 rows. Re-derivation at the new base yields **52**, matching. Full trail in §7.1;
tracked as OQ-4 (now RESOLVED) in §8A.

Base identity re-verified after that advance, before any further writing:

```
$ git rev-parse HEAD
4da0d524f1345c7126c8b551014359f9d5548975

$ git hash-object tools/project_control.py
6b7d3ac7b52ea3444682a08d818f81541102c2a6
```

The guard blob is unchanged across the advance, so no code evidence in this report required
re-basing — only the derivation-dependent mapping table. See §7.1 for the explicit re-basing
assessment.

## 1. Semantic change

### 1.1 BEFORE (pre-change `tools/project_control.py`, byte-identical at `170478e` and `4da0d52`)

```python
def invalid_unblock_roster(task: dict):
    """Return an explanatory string when a task's packet does not carry a valid
    producer + independent-reviewer roster, else None.

    Blocked-task roster precondition (M0-T014 G3 OBS-3): a task in `blocked`
    status must not be able to re-enter the active workflow until its packet is
    amended with a real producer and at least one usable independent reviewer.
    A valid roster requires:
      - a non-empty producer_agent that is not the reserved orchestrator; and
      - at least one reviewer in reviewer_agents that is neither empty, the
        reserved orchestrator, nor equal to the producer (an independent gate
        recorded by such a reviewer would otherwise be impossible to satisfy).
    Enforced on WRITE only at the unblock transition; stored history untouched.
    """
    producer = (task.get("producer_agent") or "").strip()
    if not producer:
        return ("no producer_agent is set; amend the packet with a producer before "
                "unblocking.")
    if producer == RESERVED_ORCHESTRATOR:
        return (f"producer_agent is the reserved {RESERVED_ORCHESTRATOR!r}; amend the "
                f"packet with a real producer before unblocking.")
    reviewers = task.get("reviewer_agents") or []
    usable = [r for r in reviewers
              if r and r != RESERVED_ORCHESTRATOR and r != producer]
    if not usable:
        return ("reviewer_agents has no usable independent reviewer (must be non-empty "
                f"and contain a reviewer that is neither {RESERVED_ORCHESTRATOR!r} nor "
                f"the producer {producer!r}); amend the packet before unblocking.")
    return None
```

Two defects, both visible above:

1. **Over-trigger.** `producer == RESERVED_ORCHESTRATOR` was an *unconditional* refusal. Its stated
   rationale is that an independent gate would otherwise be unsatisfiable — but that rationale does
   not hold for a packet that rosters usable independent reviewers and requires an independent gate.
2. **Fail-OPEN on malformed data.** `task.get("reviewer_agents") or []` iterated whatever it found.
   A bare string `"rev-a"` iterated into `['r','e','v','-','a']`, every element truthy and unequal
   to the orchestrator/producer, so `usable` was non-empty and the packet **passed** the roster
   check. A dict or an int raised `TypeError` out of the CLI.

### 1.2 AFTER (this change)

The full corrected text is in `tools/project_control.py:648-750`. The executable logic:

```python
    producer_raw = task.get("producer_agent")
    if producer_raw is not None and not isinstance(producer_raw, str):
        return (f"producer_agent is malformed (expected a string, got "
                f"{type(producer_raw).__name__}); amend the packet before unblocking.")
    producer = (producer_raw or "").strip()
    if not producer:
        return ("no producer_agent is set; amend the packet with a producer before "
                "unblocking.")
    reviewers, rerr = _roster_strings(task.get("reviewer_agents"), "reviewer_agents")
    if rerr:
        return rerr
    usable = [r for r in reviewers
              if r and r != RESERVED_ORCHESTRATOR and r != producer]
    if not usable:
        return ("reviewer_agents has no usable independent reviewer (must be non-empty "
                f"and contain a reviewer that is neither {RESERVED_ORCHESTRATOR!r} nor "
                f"the producer {producer!r}); amend the packet before unblocking.")
    if producer == RESERVED_ORCHESTRATOR:
        return _orchestrator_governance_exception(task)
    return None
```

The unconditional orchestrator refusal is replaced by a delegation that runs **after** the general
roster check has already passed, so the general check is a precondition of the exception rather
than an alternative to it.

### 1.3 The four conditions are conjunctive — and where each is enforced

An orchestrator-produced task leaves `blocked` only if **all four** hold. Ordering matters: the
reviewer condition is evaluated first and applies to every task, so the exception can never be
reached by a packet with an unusable roster.

| # | Condition | Enforced at | Mechanism |
|---|---|---|---|
| 1 | `task_type` is exactly `governance` | `tools/project_control.py:683` | `not isinstance(task_type, str) or task_type.strip() != GOVERNANCE_TASK_TYPE` — a non-string type fails closed on the same line |
| 2 | at least one required gate in `INDEPENDENT_GATES` | `tools/project_control.py:691` | `if not set(gates) & INDEPENDENT_GATES` (malformed `required_gates` fails closed first, line 687-690) |
| 3 | at least one usable independent reviewer | `tools/project_control.py:742-747` | the **general** check every task passes; `usable` excludes empty, `RESERVED_ORCHESTRATOR`, and the producer |
| 4 | every other control unchanged | not a new check — by construction | this guard is called from exactly one site, `tools/project_control.py:779`, inside the `blocked -> <active>` branch of `progress()`. `gate()`, `submit()`, `accept()`, directive verification and evidence identity are byte-unchanged (see §5). |

Condition 3 is deliberately *not* re-implemented inside the exception: it is the shared code path at
lines 742-747, so there is exactly one definition of "usable independent reviewer" and the exception
cannot drift from it.

Short-circuit proof that the conditions are conjunctive, not disjunctive: `invalid_unblock_roster`
returns the reviewer refusal at line 744-747 **before** line 748 tests the producer identity.
`_orchestrator_governance_exception` then returns a refusal string unless *both* remaining
conditions pass, and only `return None` (line 697) admits the transition.

### 1.4 Gate-class constant reused — no second source of truth

Condition 2 tests membership in the **existing** `INDEPENDENT_GATES` frozenset declared at
`tools/project_control.py:117`:

```python
INDEPENDENT_GATES = frozenset({"G1", "G3", "G4", "G5", "G6"})
```

This is the same constant that `gate()` branches on (`tools/project_control.py:859+`, the `else:
# INDEPENDENT_GATES` arm) and that `accept()` enforces. The guard re-lists **no** gate id — the
refusal message renders the class dynamically via `'/'.join(sorted(INDEPENDENT_GATES))`
(line 694). Consequence: if the gate taxonomy is ever changed, the unblock guard follows
automatically and cannot disagree with gate recording. This is asserted mechanically by the
source-level proof at `tools/test_project_control.py:1855-1860` (`INDEPENDENT_GATES` present, no
`['"]G[0-7]['"]` literal in the guard's executable code).

Similarly `GOVERNANCE_TASK_TYPE` (`tools/project_control.py:132`) and `RESERVED_ORCHESTRATOR`
(line 126) are named constants; the guard carries no bare `"governance"` or `"orchestrator"`
literal (asserted at `tools/test_project_control.py:1857-1862`).

### 1.5 Malformed data now fails CLOSED (new helper)

`_roster_strings` (`tools/project_control.py:648-666`) is the single normalizer for both
list-of-name fields. `None` still reads as `[]` (preserving the historical `or []` behavior), but a
bare string, a dict, a number, or any non-string element returns an explanatory error instead of
being iterated or coerced. Every branch of the guard returns a string or `None`; no packet shape
raises.

## 2. OPEN QUESTION FOR EXPLICIT INDEPENDENT-REVIEW RULING (D-004-R415) — the validation asymmetry: R352 vs R368

> **STATUS: UNRESOLVED BY DESIGN. The independent reviewers rule on this — not the producer, not
> the orchestrator.** I have deliberately NOT tightened the code to make this question disappear,
> and I am not arguing it away. Both directions are stated below so the ruling can be made on the
> merits. Whichever way it goes, the behaviour is already pinned by tests, so the ruling is a
> decision about intent, not a discovery about behaviour.

**Do not let this be buried.** `required_gates` and `task_type` are consulted **only on the
orchestrator-producer path** (they are read inside `_orchestrator_governance_exception`, which is
reached only from line 748-749). Therefore:

> A **non-orchestrator** producer whose `required_gates` is malformed (a bare string, a dict, a
> number, a list containing `None`) **still unblocks**, exactly as it did before this change.

This is a deliberate scope judgment, not an oversight. The trade-off:

- **D-004-R368** requires that "normal non-orchestrator producer behavior remains unchanged."
  Validating `required_gates` on the normal path would change normal-producer behavior — packets
  that unblocked before would begin to fail.
- **D-004-R352** requires that "malformed roster data fails CLOSED." `reviewer_agents` and
  `producer_agent` — the two fields that constitute the *roster* — **do** fail closed on every path,
  including the normal producer path. `required_gates` is a gate-requirement field, not a roster
  field.

**The case for ruling R352 dominant (tighten):** "malformed data fails closed" is a security-shaped
invariant, and a reader of R352 could reasonably expect it to cover every field the guard consults,
not a subset. Leaving one field unvalidated on one path is the kind of asymmetry that later reads
as an oversight.

**The case for ruling R368 dominant (leave as built — what I implemented):** R352's subject is
*roster* data, and both roster fields (`reviewer_agents`, `producer_agent`) DO fail closed on every
path. `required_gates` is a gate-requirement field. Validating it on the normal path would change
normal-producer behaviour, which R368 forbids in terms.

I implemented the R368 reading. **I did not treat that as settling the question.** The behaviour is
pinned by tests either way:
`tools/test_project_control.py:1764-1775` asserts the normal producer still unblocks with
`required_gates` of `["G0"]`, `["G2","G7"]` and `[]`, and lines 1718-1722 assert malformed
`reviewer_agents` fails closed on the **normal producer** path as well as the orchestrator path.

If the reviewers rule that R352 should dominate, the fix is one line (hoist the `required_gates`
normalization above the producer branch) plus updated test expectations — but it is a scope change
and a producer must not make it unilaterally. **Reviewers: please record an explicit verdict on
this item rather than letting it pass silently.**

## 2A. FINDING F-1 — PRE-EXISTING FAIL-OPEN DEFECT IN THE ORIGINAL GUARD

> **This is a DEFECT I FOUND IN THE ORIGINAL CODE, not incidental cleanup, and not part of the
> authorized semantic change.** It is disclosed here as a finding in its own right so reviewers
> assess it as such. The fix stays in.

**Defect.** At the frozen base, `invalid_unblock_roster` read the roster as:

```python
    reviewers = task.get("reviewer_agents") or []
    usable = [r for r in reviewers
              if r and r != RESERVED_ORCHESTRATOR and r != producer]
```

If `reviewer_agents` was a **bare string** rather than a list, Python iterated it **character by
character**. A packet carrying `"reviewer_agents": "rev-a"` produced
`['r', 'e', 'v', '-', 'a']` — every element truthy, none equal to `"orchestrator"` or to the
producer — so `usable` was non-empty and the packet **PASSED the roster check and unblocked**.

**Severity.** This is a fail-OPEN in a guard whose entire purpose is to fail closed. A malformed
packet could re-enter the active workflow with no usable independent reviewer, which is precisely
the state the M0-T014 G3 OBS-3 precondition exists to prevent. A dict or an int in the same field
instead raised `TypeError` out of the CLI.

**Fix.** `_roster_strings` (`project_control.py:648-666`) validates the shape and returns an
explanatory refusal. `None` still reads as `[]`, preserving the historical behaviour.

**Proof it was real and is now closed.** Negative control NC-3 (§5A.4) re-disables exactly this
type check and reproduces the defect: S10 block 6 fails with
`malformed reviewer_agents {... 'reviewer_agents': 'rev-a'} must fail closed, not unblock`.
31 malformed shapes are covered at `test_project_control.py:1744-1778`.

**Relationship to the authorized scope.** D-004-R352 requires malformed roster data to fail closed,
so this fix is squarely in scope for the roster fields. Its interaction with `required_gates` on the
non-orchestrator path is the separate open question in §2 — which I have NOT resolved.

## 3. OPEN QUESTION 2 FOR INDEPENDENT REVIEWERS — the whitespace-stripping tightening

> **UNRESOLVED BY DESIGN. Reviewers rule on this; I did not.** Stated as a behaviour change beyond
> the strict minimum so it is assessed rather than absorbed.

`_roster_strings` returns `[item.strip() for item in value]`, so reviewer names are now stripped
before comparison. The previous code compared unstripped. Effect: a packet whose only reviewer is
`" orchestrator "` previously counted as a usable independent reviewer and unblocked; it is now
refused. This moves in the fail-closed direction and closes a whitespace evasion of the reserved
identity, but it *is* a behaviour change beyond the minimum and reviewers should see it stated.
No existing test depended on the old behaviour (full suite green, §6.1).

## 4. OPEN QUESTION 3 FOR INDEPENDENT REVIEWERS — the AS-11 literal-grep interpretation

> **UNRESOLVED BY DESIGN. Reviewers rule on this; I did not.** I applied one reading and state it
> openly rather than presenting it as settled.

AS-11 as literally worded asks that the changed region contain no `M0-T0…` task-id pattern. The
changed region **does** retain two prose provenance citations in docstrings: `M0-T014 G3 OBS-3`
(pre-existing attribution for why the guard exists), `M0-T007/M0-T008` (pre-existing legacy
examples), and one new forward reference `M0-T033`.

I kept them deliberately. CLAUDE.md permanent principle 2 requires that every rule retain
provenance; stripping the `M0-T014 G3 OBS-3` attribution to satisfy a grep would destroy the trace
to why the guard exists. The binding intent of R345 is "do not hard-code M0-T027 anywhere in the
guard fix" — i.e. no task-specific special case in the logic. That is proven mechanically and more
strongly than a grep of prose:

- `tools/test_project_control.py:1837-1854` parses the three guard functions with `ast`, **strips
  their docstrings**, and asserts the remaining executable code matches no `M\d+-T\d{3}` at all.
- `tools/test_project_control.py:1868-1869` asserts the literal string `M0-T027` appears **nowhere
  in the entire module** — not in code, not in a comment, not in a docstring.

So: zero task ids in executable logic; zero mentions of the motivating task anywhere in the file.
M0-T027 is admitted by packet **shape** only. Flagging the interpretation so the reviewers can
reject it if they read AS-11 more literally.

## 5. `docs/GATES_AND_CHECKPOINTS.md` — NOT TOUCHED

**The file is byte-identical to the frozen base.** Confirmed by `git status --porcelain` (§6.3): it
does not appear in the changed-file set.

I re-read all 167 lines rather than trusting the prior pass. The file states **no** invariant about
`producer_agent`, about the reserved orchestrator as a producer, or about the unblock roster — the
unblock-roster precondition is a `project_control.py` mechanism (M0-T014 G3 OBS-3) that this
document never describes. The three closest statements are all **preserved, not contradicted**:

| Line | Statement | Effect of this change |
|---|---|---|
| 5 | "No producer approves its own work." | Preserved. The orchestrator-as-producer still cannot record G1/G3/G4/G5/G6 — `gate()` refuses the reserved identity (`project_control.py:887-891`) and refuses `reviewer == producer` (line 892-893). Proven at `test_project_control.py:1805-1815`. |
| 14 | "Any active state → `blocked`" | Preserved. This change governs only the *exit* from `blocked`; entry is untouched. |
| 163 | "Producer and G3 reviewer must be different agent identities." | Preserved and reinforced. Condition 3 requires a reviewer `!= producer` *before* the exception can apply, and `gate()` independently re-checks it. |

Editing the file would have been an unauthorized change under D-004-R342/R343 (packet risk 3).

## 5A. Test-execution proof (D-004-R413/R414) — registration, per-block counters, negative controls

Presence of test code is not evidence of execution. Four independent proofs, in increasing strength.

### 5A.1 Registered in the suite's real mechanism

The runner iterates `ALL_TESTS` (declared at `tools/test_project_control.py:1958`, iterated at
`:1978-1980`). S10 is registered:

```
$ grep -n "test_s10_governance_orchestrator_unblock," tools/test_project_control.py
1968:    test_s10_governance_orchestrator_unblock,
```

### 5A.2 Group count INCREASED 14 -> 15

The summary line is **computed, not hardcoded**, so no in-scope update to a literal was required:

```
$ grep -n "project-control test groups passed" tools/test_project_control.py
1980:    print(f"OK: all {len(ALL_TESTS)} project-control test groups passed")
```

Baseline vs now (`ALL_TESTS` entries):

```
$ git show 4da0d524f1345c7126c8b551014359f9d5548975:tools/test_project_control.py | grep -c "^    test_"
14

$ grep -c "^    test_" tools/test_project_control.py
15
```

Run output moved from `OK: all 14 …` at the frozen base to `OK: all 15 …` (§6.1).

### 5A.3 Per-block execution counters — every block, exact counts

Every numbered block calls `_rec(label, cases)` **only when control flow reaches its end**, and
`_rec` asserts `cases > 0`. All ten are wired (blocks 6-9 and the source-proof block included):

```
$ grep -n "_rec(\"" tools/test_project_control.py
1673:        _rec("1-non-governance-orchestrator-refused", n)
1697:        _rec("2-governance-orchestrator-unblocks", n)
1710:        _rec("3-governance-orchestrator-no-reviewers-refused", n)
1723:        _rec("4-orchestrator-only-roster-refused", n)
1740:        _rec("5-governance-no-independent-gate-refused", n)
1778:        _rec("6-malformed-fails-closed", n)
1811:        _rec("7-normal-producer-unchanged", n)
1839:        _rec("8-cancel-and-message-only-ungated", n)
1879:        _rec("9-gate-unchanged", n)
1922:        _rec("10-source-level-generality-proofs", len(guard_names))
```

`executed` **is read**: `tools/test_project_control.py:1943-1947` asserts the recorded list equals
the exact expected ordered `(label, count)` pairs, so a skipped, reordered, short-circuited, or
case-losing block FAILS rather than passing quietly. Exact counts (not a floor) are used
deliberately — adding a case must be a conscious update.

The run output itself carries the evidence — **executed count, expected count, and per-block case
counts**:

```
    S10 [D-004-R413/R414]: 10/10 blocks executed, 118 assertion cases
    S10 per-block case counts: 1-non-governance-orchestrator-refused=32, 2-governance-orchestrator-unblocks=9, 3-governance-orchestrator-no-reviewers-refused=2, 4-orchestrator-only-roster-refused=3, 5-governance-no-independent-gate-refused=6, 6-malformed-fails-closed=31, 7-normal-producer-unchanged=12, 8-cancel-and-message-only-ungated=12, 9-gate-unchanged=8, 10-source-level-generality-proofs=3
```

**10/10 blocks, 118 assertion cases.** The `10/10` is computed as
`len(executed)/len(expected_blocks)`, so it cannot read `10/10` unless every expected block actually
recorded itself.

Disclosure: my first instrumentation attempt asserted an invented floor `total >= 120`. The real
count is 118, so S10 FAILED on that guessed number. I replaced the guess with the measured exact
counts rather than lowering a threshold to fit. That failure is recorded here rather than smoothed
away.

### 5A.4 NEGATIVE CONTROLS — proof S10 binds the new code, not vacuously passing

Method used: **deliberate temporary failure injection, then full revert with byte-identity proof.**
Each control disables exactly one required condition; S10 must fail, and must fail *in the block
that covers that condition*.

Intended final state before injection:

```
$ git hash-object tools/project_control.py
6b7d3ac7b52ea3444682a08d818f81541102c2a6
```

**NC-1 — condition 1 (`task_type == governance`) disabled.** Replaced the guard line with
`if False:`. Expected: block 1 fails.

```
$ python -c "... t.test_s10_governance_orchestrator_unblock()"; echo "EXIT CODE: $?"
Traceback (most recent call last):
  File "<string>", line 5, in <module>
  File "...\tools\test_project_control.py", line 1665, in test_s10_governance_orchestrator_unblock
    assert r.returncode != 0, \
           ^^^^^^^^^^^^^^^^^
AssertionError: task_type 'engineering' + orchestrator producer must not unblock to backlog
EXIT CODE: 1
```

**NC-2 — condition 2 (independent-gate requirement) disabled.** Expected: block 5 fails.

```
$ python -c "... t.test_s10_governance_orchestrator_unblock()"; echo "EXIT CODE: $?"
Traceback (most recent call last):
  File "<string>", line 5, in <module>
  File "...\tools\test_project_control.py", line 1732, in test_s10_governance_orchestrator_unblock
    assert r.returncode != 0, f"required_gates {gates!r} has no independent gate"
           ^^^^^^^^^^^^^^^^^
AssertionError: required_gates [] has no independent gate
EXIT CODE: 1
```

**NC-3 — the fail-closed type check in `_roster_strings` disabled** (reintroducing the ORIGINAL
fail-open defect). Expected: block 6 fails. This control specifically exercises R352/R367.

```
$ python -c "... t.test_s10_governance_orchestrator_unblock()"; echo "EXIT CODE: $?"
Traceback (most recent call last):
  File "<string>", line 5, in <module>
  File "...\tools\test_project_control.py", line 1769, in test_s10_governance_orchestrator_unblock
    assert r.returncode != 0, \
           ^^^^^^^^^^^^^^^^^
AssertionError: malformed reviewer_agents {'task_type': 'governance', 'producer_agent': 'orchestrator', 'required_gates': ['G0', 'G3'], 'reviewer_agents': 'rev-a'} must fail closed, not unblock
EXIT CODE: 1
```

NC-3 reproduces the exact original defect: the bare string `"rev-a"` iterates into single
characters and reads as a usable roster.

**(c)+(d) Restoration, and both S10 and the full suite pass again.** S10 alone:

```
$ python -c "... t.test_s10_governance_orchestrator_unblock()"; echo "EXIT CODE: $?"
OK: S10 governance-orchestrator unblock semantics (4 conjunctive conditions, preserved defaults, fail-closed malformed data, gate() unchanged, source-level generality proofs)
    S10 [D-004-R413/R414]: 10/10 blocks executed, 118 assertion cases
    S10 per-block case counts: 1-non-governance-orchestrator-refused=32, 2-governance-orchestrator-unblocks=9, 3-governance-orchestrator-no-reviewers-refused=2, 4-orchestrator-only-roster-refused=3, 5-governance-no-independent-gate-refused=6, 6-malformed-fails-closed=31, 7-normal-producer-unchanged=12, 8-cancel-and-message-only-ungated=12, 9-gate-unchanged=8, 10-source-level-generality-proofs=3
EXIT CODE: 0
```

Full suite untruncated with exit code: §6.1 (15/15 groups, exit 0).

**(e) The injected defect is ABSENT from the final state.**

Blob identity — the restored guard is byte-identical to the pre-injection intended state:

```
$ git hash-object tools/project_control.py
6b7d3ac7b52ea3444682a08d818f81541102c2a6
```

No injected marker or stub survives anywhere under `tools/`:

```
$ grep -rn "NEGATIVE CONTROL" tools/ ; echo "grep exit (1 = absent, correct): $?"
grep exit (1 = absent, correct): 1

$ grep -rn "if False" tools/ ; echo "grep exit (1 = absent, correct): $?"
grep exit (1 = absent, correct): 1
```

`git diff` of the guard region in the final state — all three conditions the controls disabled are
present and intact (`task_type` condition, independent-gate condition; the `_roster_strings` type
check is proven by the blob hash and the NC-3 re-pass):

```diff
+def _orchestrator_governance_exception(task: dict):
+    task_type = task.get("task_type")
+    if not isinstance(task_type, str) or task_type.strip() != GOVERNANCE_TASK_TYPE:
+        return (f"producer_agent is the reserved {RESERVED_ORCHESTRATOR!r} and task_type is "
+                f"{task_type!r}, not {GOVERNANCE_TASK_TYPE!r}; amend the packet with a real "
+                f"producer before unblocking.")
+    gates, gerr = _roster_strings(task.get("required_gates"), "required_gates")
+    if gerr:
+        return (f"producer_agent is the reserved {RESERVED_ORCHESTRATOR!r} and the governance "
+                f"exception cannot be established: {gerr}")
+    if not set(gates) & INDEPENDENT_GATES:
+        return (f"producer_agent is the reserved {RESERVED_ORCHESTRATOR!r} and required_gates "
+                f"{gates} requires no independent gate "
+                f"({'/'.join(sorted(INDEPENDENT_GATES))}), so independent review of "
+                f"orchestrator-produced evidence is not structurally possible; amend the "
+                f"packet before unblocking.")
+    return None
...
+    if producer == RESERVED_ORCHESTRATOR:
+        return _orchestrator_governance_exception(task)
     return None
```

(Full guard diff in §6.6.) **No temporary defect survives into the diff to be ported.** All negative
controls were performed in this isolated worktree only; the primary checkout was never touched.

Each of the three conditions the correction adds is therefore proven to be *load-bearing* in the
tests: disable any one and S10 fails in the corresponding block.

## 6. Verbatim command outputs

### 6.1 `python tools/test_project_control.py` — FULL, UNTRUNCATED

```
$ python tools/test_project_control.py; echo "EXIT CODE: $?"
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
EXIT CODE: 0
```

**Totals: 15 test groups, all passed, exit code 0.** Group count rose 14 → 15 (S10 added). S8 — the
pre-existing unblock-roster regression group — is green **unmodified**: its assertions check only
that `"amend"` appears in stderr, and the reordered refusal for the orchestrator-producer case
still contains `"amend"`. I re-read `tools/test_project_control.py:1021-1084` and confirmed no S8
assertion needed changing.

### 6.2 `python tools/validate_directive_compliance.py --check`

```
$ python tools/validate_directive_compliance.py --check; echo "EXIT CODE: $?"
EXIT CODE: 0
```

`--check` is documented as "quiet on success" (`tools/validate_directive_compliance.py:477`), so
empty output + exit 0 IS the pass. Re-run without the flag for a human-readable confirmation:

```
$ python tools/validate_directive_compliance.py; echo "EXIT CODE (no args): $?"
directive registry OK: 5 directive(s), 5 active; source hashes, ID append-only, and producer/verifier separation verified.
EXIT CODE (no args): 0
```

### 6.3 `git status --porcelain` (read-only; nothing committed)

```
$ git status --porcelain -uall
 M .claude/agent-memory/backend-engineer/MEMORY.md
 M .claude/agent-memory/backend-engineer/env-producer-sandbox-no-exec.md
 M tools/project_control.py
 M tools/test_project_control.py
?? project-control/reports/M0-T033-producer-report.md
```

`-uall` expands untracked directories to individual files, so nothing is hidden behind a collapsed
directory entry. Five paths total, all authorized.

Final guard blob hash and base identity, after all negative controls were reverted:

```
$ git hash-object tools/project_control.py
6b7d3ac7b52ea3444682a08d818f81541102c2a6

$ git rev-parse HEAD
4da0d524f1345c7126c8b551014359f9d5548975
```

Scoped to the task's directories:

```
$ git status --porcelain -- tools docs project-control
 M tools/project_control.py
 M tools/test_project_control.py
```

### 6.4 `git diff --stat`

```
$ git diff --stat
 .claude/agent-memory/backend-engineer/MEMORY.md    |   2 +-
 .../env-producer-sandbox-no-exec.md                |   1 +
 tools/project_control.py                           | 105 +++++-
 tools/test_project_control.py                      | 370 +++++++++++++++++++++
 4 files changed, 466 insertions(+), 12 deletions(-)

$ git diff --stat -- tools docs
 tools/project_control.py      | 105 ++++++++++--
 tools/test_project_control.py | 370 ++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 464 insertions(+), 11 deletions(-)
```

(`test_project_control.py` grew from +296 to +370 with the R413/R414 execution-proof
instrumentation. `project_control.py` is unchanged at +105/-11 — the negative controls were fully
reverted, proven by the blob hash in §6.3. `docs/GATES_AND_CHECKPOINTS.md` does not appear: it is
byte-identical to the frozen base.)

### 6.5 Containment against `allowed_paths`

| Changed file | In `allowed_paths`? |
|---|---|
| `tools/project_control.py` | YES (packet `allowed_paths[0]`) |
| `tools/test_project_control.py` | YES (packet `allowed_paths[1]`) |
| `project-control/reports/M0-T033-producer-report.md` | YES (packet `allowed_paths[3]`) — this file |
| `.claude/agent-memory/backend-engineer/*` (2 files) | Own-agent memory, permitted to every agent by `.claude/rules/project-control.md` (AGENT_OPERATING_SYSTEM §7); outside gate-evidence and ledger scope |

`docs/GATES_AND_CHECKPOINTS.md` — unchanged (conditional path not exercised).
`project-control/tasks/M0-T033.json` — not written by me (orchestrator lifecycle path).
No file outside `allowed_paths` was modified. No `effort` key was written anywhere;
`teammateDefaultModel` was not touched. `.github/**`, `services/**`, `apps/**`, `packages/**`,
`render.yaml`, `CLAUDE.md`, `.claude/hooks/**`, `.claude/rules/**`, `project-control/directives/**`,
`master_plan.json`, `state.json`, `gates/`, `checkpoints/`, `blockers/` — all untouched.

### 6.6 `git diff tools/project_control.py` — the exact semantic change

```diff
@@ -36,11 +36,14 @@ TASK LIFECYCLE (docs/GATES_AND_CHECKPOINTS.md)
     blocked -> awaiting_gate is the one progress exception). `accepted` and
     `canceled` are terminal: no subcommand modifies a terminal task.
     A task leaving `blocked` for any active status (every target except
-    `canceled`) must first carry a valid roster: a real producer_agent (not
-    the reserved "orchestrator") and at least one reviewer in reviewer_agents
-    that is neither empty, "orchestrator", nor the producer. A blocked task
-    with an empty/invalid roster (e.g. legacy M0-T007/M0-T008) cannot re-enter
-    the workflow until the orchestrator amends its packet (M0-T014 G3 OBS-3).
+    `canceled`) must first carry a valid roster: a real producer_agent and at
+    least one reviewer in reviewer_agents that is neither empty,
+    "orchestrator", nor the producer. A blocked task with an empty/invalid
+    roster (e.g. legacy M0-T007/M0-T008) cannot re-enter the workflow until
+    the orchestrator amends its packet (M0-T014 G3 OBS-3). producer_agent ==
+    the reserved "orchestrator" is invalid EXCEPT in one narrow case: a
+    `governance` task that also requires an independent gate and rosters a
+    usable independent reviewer (see invalid_unblock_roster; M0-T033).
 
 ACCEPT PRECONDITIONS (all required)
     1. --agent orchestrator (procedural label, see above);
@@ -122,6 +125,12 @@ INDEPENDENT_GATES = frozenset({"G1", "G3", "G4", "G5", "G6"})
 # retro-rejected.
 RESERVED_ORCHESTRATOR = "orchestrator"
 
+# The ONE task_type whose evidence the main-session orchestrator legitimately
+# produces itself (ADR-005: only the orchestrator runs the control plane), and
+# therefore the only type admitted by the narrow exception in
+# invalid_unblock_roster. Named here so the guard never carries a bare literal.
+GOVERNANCE_TASK_TYPE = "governance"
+
 CLAIMABLE_STATUSES = frozenset({"ready", "rework"})
 SUBMITTABLE_STATUSES = frozenset({"claimed", "in_progress", "self_check", "rework"})
 
@@ -636,6 +645,58 @@ def claim(a):
     return 0
 
 
+def _roster_strings(value, field: str):
+    """Return (items, error) for a packet field that must hold a list of names.
+
+    Fails CLOSED. None reads as the empty list (the historical `or []` read),
+    but a bare string, a dict, or any non-string element is malformed and
+    returns an explanatory error instead of being iterated or silently
+    coerced: a bare "rev-a" would otherwise iterate into single characters and
+    read as a usable roster.
+    """
+    if value is None:
+        return [], None
+    if not isinstance(value, (list, tuple)):
+        return None, (f"{field} is malformed (expected a list of strings, got "
+                      f"{type(value).__name__}); amend the packet before unblocking.")
+    for item in value:
+        if not isinstance(item, str):
+            return None, (f"{field} is malformed (entry {item!r} is not a string); "
+                          f"amend the packet before unblocking.")
+    return [item.strip() for item in value], None
+
+
+def _orchestrator_governance_exception(task: dict):
+    """Return None when the ONE narrow case that lets the reserved orchestrator
+    stand as producer_agent at the unblock transition applies, else an
+    explanatory refusal string.
+
+    Conditions 1 and 2 of that case: task_type is exactly the governance type,
+    and the packet requires at least one INDEPENDENT gate. Condition 3 (a
+    usable independent reviewer) is the general roster check every task must
+    already pass in invalid_unblock_roster, and condition 4 is that nothing
+    else changes: this guard governs only the blocked-exit transition, so the
+    gate classes, submit, accept, directive-regime, evidence-identity and
+    producer-versus-reviewer rules apply to such a task exactly as before.
+    """
+    task_type = task.get("task_type")
+    if not isinstance(task_type, str) or task_type.strip() != GOVERNANCE_TASK_TYPE:
+        return (f"producer_agent is the reserved {RESERVED_ORCHESTRATOR!r} and task_type is "
+                f"{task_type!r}, not {GOVERNANCE_TASK_TYPE!r}; amend the packet with a real "
+                f"producer before unblocking.")
+    gates, gerr = _roster_strings(task.get("required_gates"), "required_gates")
+    if gerr:
+        return (f"producer_agent is the reserved {RESERVED_ORCHESTRATOR!r} and the governance "
+                f"exception cannot be established: {gerr}")
+    if not set(gates) & INDEPENDENT_GATES:
+        return (f"producer_agent is the reserved {RESERVED_ORCHESTRATOR!r} and required_gates "
+                f"{gates} requires no independent gate "
+                f"({'/'.join(sorted(INDEPENDENT_GATES))}), so independent review of "
+                f"orchestrator-produced evidence is not structurally possible; amend the "
+                f"packet before unblocking.")
+    return None
+
+
 def invalid_unblock_roster(task: dict):
     """Return an explanatory string when a task's packet does not carry a valid
     producer + independent-reviewer roster, else None.
@@ -644,26 +705,48 @@ def invalid_unblock_roster(task: dict):
     status must not be able to re-enter the active workflow until its packet is
     amended with a real producer and at least one usable independent reviewer.
     A valid roster requires:
-      - a non-empty producer_agent that is not the reserved orchestrator; and
+      - a non-empty producer_agent; and
       - at least one reviewer in reviewer_agents that is neither empty, the
         reserved orchestrator, nor equal to the producer (an independent gate
         recorded by such a reviewer would otherwise be impossible to satisfy).
+
+    producer_agent == the reserved orchestrator is invalid EXCEPT in ONE narrow
+    case: a governance task that ALSO requires an independent gate
+    (G1/G3/G4/G5/G6) and ALSO rosters a usable independent reviewer. The four
+    conditions are conjunctive - the reviewer condition is the general check
+    below, task_type and the independent gate are checked in
+    _orchestrator_governance_exception, and every other control is untouched.
+    The prohibition exists because an independent gate would otherwise be
+    unsatisfiable; where the packet proves it IS satisfiable, the main-session
+    orchestrator is recognized as the truthful producer of orchestrator-produced
+    governance evidence instead of being forced into a fictional producer label.
+    There is no special-cased task id, no flag, and no environment override.
+
+    Malformed packet data fails CLOSED: every branch returns an explanatory
+    string, and no shape of producer_agent, reviewer_agents, required_gates or
+    task_type raises.
+
     Enforced on WRITE only at the unblock transition; stored history untouched.
     """
-    producer = (task.get("producer_agent") or "").strip()
+    producer_raw = task.get("producer_agent")
+    if producer_raw is not None and not isinstance(producer_raw, str):
+        return (f"producer_agent is malformed (expected a string, got "
+                f"{type(producer_raw).__name__}); amend the packet before unblocking.")
+    producer = (producer_raw or "").strip()
     if not producer:
         return ("no producer_agent is set; amend the packet with a producer before "
                 "unblocking.")
-    if producer == RESERVED_ORCHESTRATOR:
-        return (f"producer_agent is the reserved {RESERVED_ORCHESTRATOR!r}; amend the "
-                f"packet with a real producer before unblocking.")
-    reviewers = task.get("reviewer_agents") or []
+    reviewers, rerr = _roster_strings(task.get("reviewer_agents"), "reviewer_agents")
+    if rerr:
+        return rerr
     usable = [r for r in reviewers
               if r and r != RESERVED_ORCHESTRATOR and r != producer]
     if not usable:
         return ("reviewer_agents has no usable independent reviewer (must be non-empty "
                 f"and contain a reviewer that is neither {RESERVED_ORCHESTRATOR!r} nor "
                 f"the producer {producer!r}); amend the packet before unblocking.")
+    if producer == RESERVED_ORCHESTRATOR:
+        return _orchestrator_governance_exception(task)
     return None
```

Note the diff contains **no** change to `progress()`'s call site, `gate()`, `submit()` or
`accept()`. The only hunks are the module docstring, the new constant, the two new helpers, and the
body of `invalid_unblock_roster`.

## 7. Per-requirement mapping — REGENERATED from the canonical applicable set

Not a hand-picked range. Derived in this worktree via the canonical resolver:

```
$ python -c "import sys, json; sys.path.insert(0,'tools')
from directive_registry import DirectiveRegistry
reg = DirectiveRegistry().load()
task = json.loads(open('project-control/tasks/M0-T033.json', encoding='utf-8').read())
applicable, unresolved = reg.derive_applicable(task)
..."
COUNT: 52
UNRESOLVED: []
D-004-R332,D-004-R335,D-004-R336,D-004-R337,D-004-R338,D-004-R339,D-004-R340,D-004-R341,
D-004-R342,D-004-R343,D-004-R344,D-004-R345,D-004-R346,D-004-R347,D-004-R348,D-004-R349,
D-004-R350,D-004-R351,D-004-R352,D-004-R353,D-004-R354,D-004-R355,D-004-R356,D-004-R357,
D-004-R358,D-004-R359,D-004-R360,D-004-R361,D-004-R362,D-004-R363,D-004-R364,D-004-R365,
D-004-R366,D-004-R367,D-004-R368,D-004-R369,D-004-R370,D-004-R371,D-004-R372,D-004-R373,
D-004-R387,D-004-R389,D-004-R410,D-004-R411,D-004-R412,D-004-R413,D-004-R414,D-004-R415,
D-004-R416,D-004-R417,D-004-R418,D-004-R419
```

**52 ids, zero unresolved**, derived at base `4da0d52`. The table below contains every one of them
and no id outside the set.

Note on the boundary: **`D-004-R420` EXISTS in the registry but is NOT in the derived applicable
set**, so it is deliberately absent from the table. (Its text — "No Step 5, no M0-T032, and no
unrelated work" — is a scope constraint the resolver does not attach to this task.) Earlier
instructions referred to the amendment-10 range as "R410-R420"; the canonical derivation ends at
R419, and I follow the derivation.

§7.1 records the earlier 42-vs-52 discrepancy and its resolution — retained deliberately as part of
the evidence trail.

| Req | Requirement (abbreviated) | What satisfies it | Evidence location |
|---|---|---|---|
| R332 | OPTION B AUTHORIZED: a narrow, independently reviewed correction to `invalid_unblock_roster` | Exactly one narrow case added; correction is independently reviewable and gated | §1.2-§1.3; `project_control.py:648-750` |
| R335 | Opus-5 availability exception (R307) ACTIVE: explicit Opus 5 for producer/reviewers/verifiers | Producer ran on explicit Opus 5 | report header; §9 |
| R336 | Disclose the actual model honestly; never claim a model not used | Model stated as `claude-opus-5[1m]` | report header |
| R337 | Contract M0-T033 if unused | **ORCHESTRATOR SCOPE** — packet contracted before dispatch | `project-control/tasks/M0-T033.json` (not written by me) |
| R338 | Producer must be a REAL EXISTING NON-ORCHESTRATOR agent qualified for Python control-plane tooling, distinct from every reviewer | Producer is `backend-engineer`, a real `.claude/agents/` roster definition, not in `READ_ONLY_AGENTS`, and absent from the four reviewers | §0(a); packet `producer_agent`/`reviewer_agents` |
| R339 | Reviewers exactly code-reviewer, security-reviewer, control-plane-verifier, directive-compliance-verifier | Packet rosters exactly those four | packet `reviewer_agents` (not written by me) |
| R340 | Required gates exactly G0, G2, G3, G5 | Packet requires exactly those | packet `required_gates` (not written by me) |
| R341 | Cite applicable governance directives through the canonical resolver | Mapping regenerated via `DirectiveRegistry.derive_applicable` | **this section**, §7.1 |
| R342 | Authorized paths exactly: `project_control.py`, `test_project_control.py`, conditional `GATES_AND_CHECKPOINTS.md`, own packet/reports | Changed set is exactly the first two plus this report | §6.3, §6.5 |
| R343 | No other tools, hooks, settings, agent defs, product, deployment, or unrelated control-plane behavior may change | Nothing else changed; `gate()`/`submit()`/`accept()` byte-unchanged | §6.3, §6.5, §6.6 |
| R344 | Correct `invalid_unblock_roster` GENERALLY, not a special case | Guard keys on packet **shape** (`task_type`, `required_gates`, `reviewer_agents`) only | `project_control.py:700-750`; generality proof `test_project_control.py:1838-1856` |
| R345 | Do not hard-code M0-T027 anywhere in the guard fix | Zero task ids in executable code; `M0-T027` absent from the whole module | `test_project_control.py:1837-1854` (ast, docstrings stripped), `:1868-1869` (whole-file). See §4 for the interpretation |
| R346 | Do not add a bypass flag | No new CLI option, no env read, no override token | `test_project_control.py:1871-1876` (`progress -h` option set), `:1863-1867` (no token / no `os.environ` / no `getenv`) |
| R347 | PRESERVE: missing producer remains invalid | `if not producer: return …` unchanged | `project_control.py:736-738`; test `test_project_control.py:1750-1757` (`None`, `""`, `"   "`) |
| R348 | PRESERVE: non-governance + orchestrator producer remains invalid | Condition 1 refusal | `project_control.py:683-686`; test `test_project_control.py:1644-1659` (8 task types x 4 targets) |
| R349 | PRESERVE: empty reviewer roster remains invalid | General usable-reviewer check | `project_control.py:744-747`; test `:1679-1688` (`[]` and `None`) |
| R350 | PRESERVE: roster of only `orchestrator` remains invalid | `usable` excludes `RESERVED_ORCHESTRATOR` | `project_control.py:742-743`; test `:1689-1698` (3 shapes) |
| R351 | PRESERVE: roster of only the producer remains invalid | `usable` excludes `producer` | `project_control.py:742-743`; test `:1758-1763` |
| R352 | PRESERVE: malformed roster data fails CLOSED | `_roster_strings` + `producer_agent` type check | `project_control.py:648-666`, `:731-734`; test `:1713-1747` (33 malformed shapes). **Scope caveat for `required_gates` on the normal path — see §2** |
| R353 | PRESERVE: `blocked -> canceled` remains permitted | Guard is not called when `target == "canceled"` | call site `project_control.py:778`; test `:1776-1791` (6 roster shapes incl. malformed) |
| R354 | PRESERVE: independent-gate enforcement unchanged | `gate()` byte-unchanged | §6.6 diff (no `gate()` hunk); test `:1800-1835` |
| R355 | ADD EXACTLY ONE narrow case, four conditions conjunctive | Single delegation reached only after the general check passes | `project_control.py:748-749`; §1.3 |
| R356 | Condition 1: `task_type` exactly `governance` | `task_type.strip() != GOVERNANCE_TASK_TYPE` | `project_control.py:683` |
| R357 | Condition 2: >= 1 required gate from G1/G3/G4/G5/G6 | `set(gates) & INDEPENDENT_GATES` | `project_control.py:691`; test `:1660-1670` (each of G1/G3/G4/G5/G6) |
| R358 | Condition 3: >= 1 usable independent reviewer | Shared general check | `project_control.py:742-747` |
| R359 | Condition 4: all existing controls still apply | Guard governs only the blocked-exit transition; no other function changed | §6.6 diff; test `:1800-1835` |
| R360 | PURPOSE: recognize the orchestrator as truthful producer where independent review is possible | Rationale recorded in the guard docstring; enforced by conditions 2+3 together | `project_control.py:711-720` |
| R361 | Must not weaken `gate()`, `submit()`, `accept()`, directive verification, evidence identity, producer-vs-reviewer separation | No hunk touches them; S2/S3/S6/S9 groups still green | §6.6; §6.1 (15/15 groups) |
| R362 | TEST 1: non-governance orchestrator rejection still green | S10 (1) + pre-existing S8 unmodified | `test_project_control.py:1644-1659`; S8 at `:1021-1084` |
| R363 | TEST 2: governance + orchestrator + independent gate + usable reviewer CAN unblock | S10 (2), each independent gate + each active target | `test_project_control.py:1660-1678` |
| R364 | TEST 3: governance + orchestrator + no reviewers FAILS | S10 (3) | `test_project_control.py:1679-1688` |
| R365 | TEST 4: roster of only `orchestrator` FAILS | S10 (4) | `test_project_control.py:1689-1698` |
| R366 | TEST 5: no independent required gate FAILS, refusal names it | S10 (5), asserts each of G1/G3/G4/G5/G6 in stderr | `test_project_control.py:1699-1712` |
| R367 | TEST 6: malformed reviewer data fails closed WITHOUT traceback | S10 (6), asserts `"Traceback" not in stderr` | `test_project_control.py:1713-1747` |
| R368 | TEST 7: normal non-orchestrator producer unchanged | S10 (7), incl. (research\|governance) x (with\|without independent gate) | `test_project_control.py:1748-1775` |
| R369 | TEST 8: `blocked -> canceled` unchanged | S10 (8), incl. message-only progress | `test_project_control.py:1776-1799` |
| R370 | TEST 9: an independent reviewer cannot equal the producer | S10 (9), plus no-gate-record-written assertion | `test_project_control.py:1800-1835` |
| R371 | TEST 10: full suites green | 15/15 groups exit 0; validator exit 0 | §6.1, §6.2 |
| R372 | Run M0-T033 through its COMPLETE controlled lifecycle | **ORCHESTRATOR SCOPE — not producer-satisfiable.** G0 recorded at `170478e`; this report is the producer submission for G2/G3/G5 | not claimed here |
| R373 | Merge and accept ONLY after every required independent gate passes at ONE frozen identity | **ORCHESTRATOR SCOPE — not producer-satisfiable.** Producer work is frozen at `4da0d52`, guard blob `6b7d3ac7…` | not claimed here |
| R387 | PHASE 4 step 7: STOP on any blocking or ambiguous result | Honoured twice: the frozen-base attestation STOP (§0b), and the derivation discrepancy reported instead of resolved (§7.1). Three open questions left for reviewers rather than self-resolved (§8A) | §0(b), §7.1, §8A |
| R389 | PHASE 4 step 9: clean ONLY the branches/worktrees created for these two authorized tasks | **ORCHESTRATOR SCOPE.** I performed no git mutation, no branch/worktree creation or deletion | §9 item 4 |
| R410 | Continue M0-T033 under the CORRECTED frozen-base dispatch; no new owner decision required | Resumed and completed at the corrected bases; every base advance orchestrator-performed, each re-verified before writing | §0(c), §0(e) |
| R411 | Preserve the original producer attestation STOP (frozen-base mismatch under worktree isolation) AND the corrected resume honestly; neither omitted nor smoothed | §0 records all five events as a multi-dispatch history, explicitly not a clean single pass — including that the in-scope blobs were byte-identical and the producer stopped anyway | **§0(a)-(e)** |
| R412 | Do not waive or silently resolve either carried item (never-executed S10 body; `required_gates`/`task_type` asymmetry) | Neither waived: the S10 body is now proven executed 10/10 (§5A), and the asymmetry is preserved unresolved as OQ-1. Two producer errors also disclosed rather than smoothed | §5A, §2, **§8A**, §9 item 1a |
| R413 | PROVE every test relied on for acceptance is REGISTERED and EXECUTED — registration plus observed execution in run output, not mere presence of code | Registered in `ALL_TESTS` (`:1968`); group count 14 -> 15; summary computed from `len(ALL_TESTS)`; `10/10 blocks executed, 118 assertion cases` in the run output | §5A.1, §5A.2, §5A.3 |
| R414 | If the S10 body is never invoked it CANNOT count as passing evidence: correct it in scope or return a blocker | Corrected in scope (not returned as a blocker): end-of-block recorder on all 10 blocks + asserted exact ordered `(label, count)` sequence + three negative controls proving the tests bind | §5A.3, §5A.4 |
| R415 | PRESERVE the asymmetry for an EXPLICIT independent-review ruling weighed against R352 and R368; the reviewers rule, producer and orchestrator do not settle it | Preserved unresolved in its own titled section with both directions argued; no code changed to make it disappear; explicit statement that reviewers rule | **§2**, §8A OQ-1 |
| R416 | After the producer returns, perform the CONTRACTED EXACT-DIFF CONTAINMENT REVIEW | **ORCHESTRATOR SCOPE — not claimed by me.** I supply the inputs: `git status --porcelain -uall`, `git diff --stat`, full guard diff | §6.3, §6.4, §6.6 (inputs only) |
| R417 | Perform a TREE-IDENTICAL PORT onto the controlled task branch | **ORCHESTRATOR SCOPE — not claimed by me.** No git mutation performed; guard blob `6b7d3ac7…` published for port verification | §6.3, §9 item 4 |
| R418 | Proceed through the AUTHORIZED M0-T033 gates ONLY (G0, G2, G3, G5) | **ORCHESTRATOR SCOPE — not claimed by me.** I recorded no gate and requested only `awaiting_gate` | report header, §9 item 4 |
| R419 | Keep M0-T027 UNTOUCHED until M0-T033 is MERGED AND ACCEPTED (tightens R374, which bound only the implementation window) | M0-T027 untouched in any form; absent from `git status`; string `M0-T027` absent from the whole module, asserted mechanically. I make no claim on the post-merge window, which is orchestrator scope | **§8**, `test_project_control.py:1868-1869` |

R337, R372, R373 and R389 are lifecycle obligations of the orchestrator. I record them as
**ORCHESTRATOR SCOPE, not satisfied by this report**, rather than claiming them.

### 7.1 DERIVATION DISCREPANCY — RESOLVED (raised under D-004-R387; tracked as OQ-4)

**Retained deliberately.** The discrepancy and its resolution are part of the evidence trail and are
not deleted now that they are settled.

**What happened.** At base `170478e` my canonical derivation yielded **42** ids; the orchestrator's
cross-check stated **52**. I reported the discrepancy and **refused to adopt either number**,
because adopting an underived count would have put an unverified figure into gate evidence.

| | Count | Set |
|---|---|---|
| Mine (derived at `170478e`) | **42** | R332, R335-R373, R387, R389 |
| Orchestrator cross-check ("at the current head") | **52** | R332, R335-R373, R387, R389, **R410-R419** |
| **Mine, re-derived at corrected base `4da0d52`** | **52** | matches the cross-check exactly |

Set-differenced programmatically:

```
mine   : 42
coord  : 52
coord-only (I lack): ['D-004-R410', 'D-004-R411', 'D-004-R412', 'D-004-R413', 'D-004-R414',
                     'D-004-R415', 'D-004-R416', 'D-004-R417', 'D-004-R418', 'D-004-R419']
mine-only (they lack): []
unresolved: []
```

The delta is **exactly R410-R419** — the amendment-10 rows — and nothing else. I hold no id the
orchestrator lacks.

**Root cause, verified — not a defect in either derivation.** The D-004 registry in this worktree
contains R1..R409 and no row at or above R410:

```
$ python -c "... re.findall(r'D-004-R(\d+)', raw) ..."
D-004 requirement ids present in worktree registry:
  count = 409  min = R1  max = R409
  any >= 410 present? NONE
```

My worktree was frozen at `170478e`. Amendment 10 was captured by the orchestrator **after** that
commit, so R410-R419 did not exist at that base and could not be derived there. Both derivations
were correct at their own base; they differed only because the bases differed.

**RESOLUTION.** The orchestrator independently confirmed the root cause and fast-forwarded this
worktree `170478e -> 4da0d52` (ADR-005 authority; `project-control/directives/**` is a forbidden
path for me, so I could not have made this correction myself). Amendment 10 was captured at
`836daef`, a child of `170478e`. At the corrected base the registry holds 420 rows and my
re-derivation returns **52 ids, zero unresolved**, matching the cross-check exactly. The §7 table is
regenerated from that derived set; the ten previously-unmappable rows R410-R419 are now mapped from
**verbatim registry text**, not from prose relayed to me.

**EXPLICIT RE-BASING ASSESSMENT (asked directly, answered directly).** Beyond the mapping table, I
assessed whether any earlier evidence needed re-basing, and re-ran rather than assumed:

| Evidence | Re-based? | Basis |
|---|---|---|
| Guard semantics / diff / blob hash | **No change needed** | `git hash-object tools/project_control.py` = `6b7d3ac7…` at both bases; `4da0d52` touches only `project-control/directives/**`, the M0-T033 packet progress log and `state.json` — nothing in my write scope |
| Full test suite | **Re-run at `4da0d52`** | 15/15, exit 0, identical output incl. `10/10 blocks executed, 118 assertion cases` (§6.1) |
| Directive validator | **Re-run at `4da0d52`** | exit 0; "5 directive(s), 5 active" (§6.2) |
| Containment (`-uall`, `--stat`) | **Re-run at `4da0d52`** | identical 5 paths / 4 files, +466/-12 (§6.3, §6.4) |
| 14 -> 15 group-count baseline (§5A.2) | **Re-checked at `4da0d52`** | `git show 4da0d52:tools/test_project_control.py \| grep -c "^    test_"` still returns 14 |
| Negative-control evidence (§5A.4) | **Still valid, not re-run** | The controls were performed against the identical guard blob; re-running would produce the same three failures. Stated plainly so reviewers can require a re-run if they disagree |
| §0(a)/(b) history, F-1, OQ-1/2/3 | **Unaffected** | Historical facts and source-level findings, independent of the registry base |

I did not re-run the three negative controls at the new base. That is the one place where a reviewer
could reasonably ask for a repeat; I judged it unnecessary because the guard blob is byte-identical,
and I am flagging the judgment rather than hiding it.

## 8. M0-T027 — NOT TOUCHED (D-004-R374)

Explicit confirmation: **`project-control/tasks/M0-T027.json` was not read into any write, not
modified, and M0-T027 was not touched in any form.** It does not appear in `git status --porcelain`
(§6.3). The string `M0-T027` appears nowhere in `tools/project_control.py` — asserted mechanically
at `tools/test_project_control.py:1868-1869`.

M0-T027 is admitted by the corrected guard purely by packet **shape**: `task_type == "governance"`,
`producer_agent == "orchestrator"`, `required_gates` `["G0","G2","G3","G5"]` (G3 and G5 are in
`INDEPENDENT_GATES`), and three usable independent reviewers. Any packet with that shape is
admitted; M0-T027 is named nowhere in the logic. I did not run the guard against the real M0-T027
packet, because doing so would be a control-plane write; reviewers can verify shape admission by
reading the packet read-only.

## 8A. OPEN QUESTIONS FOR INDEPENDENT REVIEWERS — none self-certified, none resolved

**Three items remain open** (OQ-1, OQ-2, OQ-3); OQ-4 is now RESOLVED and retained for the trail.
**I did not resolve, self-certify, or argue away any of the open items**, and I did not change code
to make any of them disappear. Each open item needs an explicit recorded verdict.

| # | Open question | Where | What the reviewers must rule |
|---|---|---|---|
| OQ-1 | **R368 vs R352 validation asymmetry** — `required_gates`/`task_type` are consulted ONLY on the orchestrator-producer path, so a non-orchestrator producer with malformed `required_gates` still unblocks (unchanged behaviour) | **§2** | Whether R352 (fail closed) or R368 (normal producer unchanged) dominates. If R352: hoist the `required_gates` normalization above the producer branch (one line + test updates) |
| OQ-2 | **Whitespace-stripping tightening** — reviewer names are now `.strip()`ed, so a roster of only `" orchestrator "` is refused where it previously unblocked | **§3** | Whether this fail-closed tightening is acceptable in scope, or must be reverted to an exact-match comparison |
| OQ-3 | **AS-11 literal-grep interpretation** — prose provenance (`M0-T014`, `M0-T007/M0-T008`, `M0-T033`) retained in docstrings; generality proven on executable code with docstrings stripped, plus whole-file absence of `M0-T027` | **§4** | Whether the binding intent of R345/R346 is "no task-specific logic" (my reading) or a literal grep of the changed region |
| ~~OQ-4~~ | **RESOLVED — derivation discrepancy 42 vs 52.** Root cause: amendment 10 was captured at `836daef`, a child of base `170478e`, so R410-R419 did not exist at my base. Orchestrator fast-forwarded `170478e -> 4da0d52`; re-derivation returns **52, zero unresolved**, matching. Table regenerated from verbatim registry text. Retained in the trail, not deleted | **§7.1** | No ruling required. Reviewers may still wish to confirm the one judgment I flagged: the three negative controls were not re-run at the new base (guard blob byte-identical) |

Related disclosed finding (not an open question — a defect found and fixed): **F-1**, the
pre-existing fail-open roster defect, §2A.

## 9. Self-check limitations and open items

0. **RESOLVED (was: amendment-10 rows undederivable).** After the orchestrator's base correction to
   `4da0d52`, all 52 applicable ids derive cleanly and R410-R419 are mapped from verbatim registry
   text. Residual judgment I am flagging: the three negative controls were **not re-run** at the new
   base, because the guard blob is byte-identical across it. See §7.1.
1. **Three open questions are left for the reviewers** — OQ-1, OQ-2, OQ-3, consolidated in **§8A**
   (OQ-4 resolved, retained for the trail). None is self-certified. In particular the R368-vs-R352
   asymmetry (D-004-R415) stays open for an explicit ruling.
1a. **Two producer errors occurred and are disclosed, not smoothed**: the R413/R414 instrumentation
   was initially wired to blocks 1-5 only with `executed` never read (caught by the orchestrator's
   containment review, now corrected — §5A.3), and my first execution-total assertion used an
   invented floor of 120 against a real count of 118, which failed until I measured it (§5A.3).
2. **§3 whitespace tightening** of reviewer names is a behaviour change beyond the strict minimum.
3. **§4 AS-11 literal-grep interpretation** — prose provenance retained; reviewers may disagree.
4. I did **not** execute any control-plane write (`new-task`/`claim`/`progress`/`submit`/`gate`/
   `accept`/`checkpoint`), any git mutation, or any `gh` command. All CLI behaviour was proven
   against disposable temp projects created by the test harness, never the real ledger.
5. The S10 group creates ~60 temp tasks under ids `M9-T101+` inside `tempfile.mkdtemp()` trees that
   are removed in a `finally` block; no real ledger file is touched (consistent with S7, which only
   *copies* the real ledger read-only).
6. No permission denial occurred during implementation. The only denials in this task were in the
   earlier stopped session (worktree isolation refusing shared-checkout git and compound commands),
   and they were resolved by the orchestrator's base correction.
