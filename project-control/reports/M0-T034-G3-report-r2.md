<!--
PRESERVATION RECORD (orchestrator, 2026-07-31)
This file preserves the complete M0-T034 G3 ROUND-2 gate return exactly as the independent
reviewer agent `m0t034-g3-r2` delivered it to the orchestrator via SendMessage, in two
labelled parts ("PART 1 of 2", "PART 2 of 2"), preserved the moment they arrived. Both parts
are concatenated here in order, separated by a single blank line. NO alteration was made.
The R024 scan found nothing to redact: the reviewer self-redacted the D3 username token as
`<username token>` at authoring time, exactly so this report could be preserved without
reintroducing the leak it reports.
-->

G3 GATE REPORT — M0-T034 — ROUND 2 — **PART 1 of 2** (expect 2 parts; part 2 contains F4–F8, the regression check, AS-5/C2, observations, verification scope, required rework, and the reviewer conclusion)

REDACTION NOTE, stated up front: finding D3 concerns a machine username committed to a public repo. I have REDACTED that token throughout this report at authoring time, so that preserving this report does not reintroduce the leak it reports. The redacted token is marked `<username token>`. Its exact unredacted value is on line 716 of the file named in D3.

```markdown
# Gate Report — M0-T034 G3, ROUND 2 (independent)

- **Gate ID:** G3
- **Task ID:** M0-T034
- **Reviewer:** `m0t034-g3-r2` — role `code-reviewer`, independent; **not** the producer (`backend-engineer`) and not the round-1 G3 reviewer (`m0t034-g3`).
- **Model actually running:** **Opus 5**, exact model id `claude-opus-5[1m]`, dispatched at explicit Opus 5 under D-004-R307. **I am not Fable 5 and make no such claim.** (My session preamble contained boilerplate naming a different model; my environment block identifies this process as `claude-opus-5[1m]`, and that is what I disclose.)
- **R024 statement:** every path below is `<REPO>`-relative. This report contains no absolute machine path, no machine username, no hostname and no session identifier.

## HEAD verification (first act)

$ git rev-parse HEAD
24d2d8034a753bbe89642ddf35dee13c7bb1aeb9      <- MATCHES the frozen SHA exactly
$ git rev-parse --abbrev-ref HEAD
task/M0-T034-governance-acceptance-semantics
$ git status --porcelain
(empty - clean tree)

Branch commits: `24d2d80` (round-2 rework, under review), `659cdde`/`af5c083`/`3c5ecc5` (orchestrator lifecycle), `1298f4b` (round-1 self-check), `a965c21` (round-1 implementation), base `05ee1917`. I reviewed the **whole task fresh at this SHA**, not the delta — a FAIL-then-fix inherits no pass.

## VERDICT: **FAIL**

The central round-1 defect is genuinely and thoroughly cured, and I want that stated plainly before the failure: **D1 is fixed correctly, F2 and F3 are fixed correctly, F6 is fixed, nothing regressed, and the design is sound.** This is a narrow return, not a rejection of the architecture.

It fails on three things. **(D3)** the D2 cure reintroduced the very defect class it was curing — the machine username is back in the same file, in a public repository, inside the sentence claiming it was removed. **(F5)** is unresolved, and the producer's stated reason for leaving it unresolved is demonstrably wrong: the fix is fully inside `allowed_paths` and needs no schema change. **(F4)** is unresolved; I have a reproducible bypass that erases a deferred obligation from both of the two sources that were supposed to make it unerasable. F4, F5 and F7 were declared **binding at this gate**.

---

## Item 1 — D1: condition (5) is now a pending-only allowlist. **CURED. No residual.**

`<REPO>/tools/directive_registry.py:172-174` replaces the denylist with:

    DEFERRABLE_VERIFICATION_STATES = frozenset({"pending"})

and `:303-309` inverts the test, with the type guard placed **first** so an unhashable state refuses instead of raising:

    state = verification_row.get("state")
    if not isinstance(state, str) or state not in DEFERRABLE_VERIFICATION_STATES:
        refusals.append(...)

`NEGATIVE_VERIFICATION_STATES` is gone from the module entirely (probed: `hasattr(dr, "NEGATIVE_VERIFICATION_STATES") == False`).

**Probed end-to-end through `task_verification_result` -> `_v2_task_unresolved` — the path `accept()` actually calls — not through the classifier helper in isolation.** Fixture: one `sequencing` row bound solely to `accept`, carrying a fully well-formed independent attestation, so conditions (1)-(4) all hold and only `state` varies. 30 states:

| state | DEFERRED | blocks accept |
|---|---|---|
| `"pending"` (intended) | **True** | False |
| `PASS` | False | False (satisfied) |
| `FAIL`, `BLOCKED` | False | True |
| **`UNVERIFIABLE`** | **False** | **True** |
| `NOT_APPLICABLE` | False | True |
| **key absent**, `None` | **False** | **True** |
| **`[]`, `{}`, `()`, `frozenset()`, `["pending"]`, `{"state":"pending"}`** | **False** | **True** (no exception) |
| `""`, `"garbage"`, `"TODO"`, `"PASSED"` | False | True |
| `"fail"`, `"blocked"` (lowercase) | False | True |
| `"Pending"`, `"PENDING"` (case) | False | True |
| `"pending "`, `" pending"`, `"  pending  "`, `+newline`, `+tab` | False | True |
| `0`, `False`, `True`, `1.0` | False | True |

**Anomalies: none. Only the literal token `pending` is deferrable; every other state both refuses deferral and blocks acceptance.** Refusal is the default, and `state=[]` no longer raises — it produces two refusal reasons.

**The uncaught `TypeError` is gone and the docstring is now true.** I fuzzed `acceptance_ordering_deferral` over **124,416** input shapes (two-field combinations of 24 heterogeneous values across `act_class`/`classified_by`/`justification`/`classified_at`, crossed with six row classifications, six `lifecycle_events` shapes and random states and producers): **0 exceptions raised.** The docstring claim at `:220-229` ("Fails closed on every malformed shape and never raises") is now accurate.

**AS-12 holds — the stated rule was amended and it matches behavior.** `<REPO>/tools/directive_registry.py:108-125` now states condition (5) as an allowlist and enumerates exactly what refuses: "FAIL, BLOCKED, UNVERIFIABLE, an absent or null state, an unknown string, a **case- or whitespace-variant** of an allowed token, and any non-string type". Every one of those claims reproduces in the table above, including the whitespace variants — note the producer chose **strict equality** rather than the `state.strip()` the round-1 report suggested, which is the stricter reading, and documented that choice. Condition (2) was correspondingly re-titled "INDEPENDENT, **DATED** ATTESTATION" at `:74-86` to cover the new `classified_at` requirement. A reviewer can still audit a stated rule rather than infer behavior.

**AS-2 grew 10 -> 35 and the new cases are real probes, not padding.** `<REPO>/tools/test_project_control.py:2198-2328`. Every case runs the **full CLI** through `attempt()`, which asserts three things per case: `returncode != 0`, `status == "awaiting_gate"` (a refused accept must not move the task), and `"post_accept_verification" not in t` (a refused accept must register no deferral). Case (vii) at `:2275-2277` iterates **20 states deliberately outside the old `{FAIL, BLOCKED}` denylist** — `UNVERIFIABLE`, `fail`, `blocked`, `FAIL `, `Pending`, `pending `, `PASSED`, `""`, `wat`, `None`, `0`, `1`, `False`, `True`, `[]`, `["pending"]`, `{}`, `{"state":"pending"}` — and asserts `"Traceback" not in err` on each, pinning the no-raise property. Case (vii-b) at `:2286-2292` covers the absent key. Five more cases probe the new dated-attestation condition, one probes case/whitespace-respelled self-classification, one probes a missing row. The positive control at `:2318-2323` proves the fixture accepts when well-formed, so the 34 refusals are caused by the broken condition and not by an unrelated fixture precondition. `assert cases == 35` pins the count.

**Severity: resolved. This was the blocking defect and it is closed properly.**

## Item 2 — D2: the absolute path at producer-report line 198. **The named line is CURED; see D3.**

`<REPO>/project-control/reports/M0-T034-producer-report.md` line 198 no longer contains a `cd` transcript at all (the file grew; the amended transcript now reads `$ cd <REPO>/.claude/worktrees/agent-a8497f73f558bac2a` at `:889` and `:1110`). The producer amended its own evidence, so the report-preservation rule is respected. **D2 as scoped is cured.**

## Item 2b — **D3 (NEW, BLOCKING): the D2 remediation reintroduced the machine username into the same public file.**

`<REPO>/project-control/reports/M0-T034-producer-report.md:716` — the sentence describing the D2 fix names the machine username token as a literal grep pattern, alongside `Downloads/nyc-zoning`, in one line:

> and re-swept the whole file and `tools/` for `<username token>`, `/c/Users`, `C:\Users` and `Downloads/nyc-zoning` — **no matches remain**.

The sentence is self-falsifying: **it is itself the match.** Between the username token and the `Downloads/nyc-zoning` fragment on the same line, it discloses substantially what the original line-198 leak disclosed — the OS username plus the home-directory layout.

Reproduction, and proof it is **new in this commit** rather than pre-existing:

    $ gh repo view --json visibility,nameWithOwner
    {"nameWithOwner":"martin10101/nyc-buildability","visibility":"PUBLIC"}

    $ git grep -n -o "<username token>" -- project-control/reports/M0-T034-producer-report.md
    project-control/reports/M0-T034-producer-report.md:716

    $ git diff 1298f4b 24d2d80 | grep "^+" | grep "<username token>"
    +and re-swept the whole file and `tools/` for `<username token>`, `/c/Users`, `C:\Users` and

Exactly one occurrence, and it is on the `+` side of the round-2 diff — introduced by the rework, in the file the rework was cleaning.

**Severity: BLOCKING**, for consistency with the precedent this task already set: round-1 G3 graded this identical class in this identical file BLOCKING (as D2), and the orchestrator adopted that grading when it dispatched the rework. I record round-1 G5's contrary view honestly — it graded the class LOW on the ground that 30+ already-accepted reports carry the same pattern, and I independently confirm that pervasiveness (`git grep -c` over `project-control/` returns hits in `M0-T002-G1-verification.md`, `M0-T004-producer-report.md`, `M0-T012-G3-security-review.md` and many more). But the distinguishing fact in both rounds is that **this task introduces a new occurrence**, and here it does so inside the fix for that exact defect. This is R024's fourth recurrence and is the strongest available argument for the queued OBS-6 systemic fix (redaction at preservation time), which no per-report discipline has yet achieved.

**Fix: one word.** Replace the username token with `<user>` (or drop the pattern list). The repo-wide sweep of the 30+ accepted reports should remain its own follow-up, as round-1 G5 recommended — those reports are immutable and blocking M0-T034 for them would be inconsistent.

## Item 3 — F2: post-accept discharge held to the gate's own standard. **CURED IN CODE.**

The old discharge read a bare state and accepted `PASS`. It is now routed through a new method, `<REPO>/tools/directive_registry.py:820-889` `deferred_requirement_discharge()`, which enforces every standard the accept-time gate applies:

- **independence** (`:849-861`) — a non-empty `producer` **and** a non-empty `verifier` that is not the producer, compared through `_identity_key()` (case- and whitespace-insensitive);
- **content identity** (`:862-867`) — the record's `reviewed_manifest_sha256` must equal `expected_identity`;
- **reviewed commit** (`:868-874`) — the record's `reviewed_sha` must equal `expected_sha`;
- **row state** (`:875-885`) — `PASS`, or `NOT_APPLICABLE` with justification and an approver, via `_row_is_satisfied()` at `:798-807`;
- **record readability** (`:846-848`) — a missing, duplicate or unreadable container fails closed, including the case where the row was **deleted** ("a deferred obligation cannot be discharged by its own deletion", `:881-883`).

`accept()` supplies the binding values: `<REPO>/tools/project_control.py:569-571` stamps `deferred_at_identity` and `deferred_at_sha` onto every deferral it records, and `:640-651` refuses to proceed if a deferral record lacks either ("its discharge cannot be bound to what was accepted (fail closed)").

**The union is real.** `<REPO>/tools/project_control.py:606-664` builds the outstanding set from two sources: the packet's `post_accept_verification` records, and a re-derivation via `outstanding_lifecycle_claims()` (`<REPO>/tools/directive_registry.py:891-908`) over every **accepted, in-regime** task's verification rows that still claim a lifecycle classification and are unsatisfied. An unreadable record yields a synthetic row so the caller fails closed rather than reading "nothing outstanding".

I reproduced the union myself against a synthetic temp ledger with the resolver stubbed (the real ledger untouched, read-only throughout):

    A. untouched accepted packet                   blockers=1   (deferral not discharged)
    B. delete post_accept_verification ONLY        blockers=1   (re-derived from the registry)

**The specific claim the rework makes — "deleting the packet key removes the record, not the obligation" — is TRUE.** The regression test that proves it is genuine and end-to-end: `<REPO>/tools/test_project_control.py:2497-2631`, 9 CLI-level `checkpoint` cases including bare-PASS-with-no-verifier (a), producer self-discharge under a respelled identity (b), wrong content identity (c), wrong reviewed commit (d), deleted row (e), **packet-key deletion with re-derivation (g)**, an `UNVERIFIABLE` post-accept verdict (i), and a positive control (f) proving a proper discharge does proceed.

**Severity: resolved.** "Deferral is not waiver" is now true in code, not prose. See F4 in part 2 for what the union still does not cover.

## Item 4 — F3: fail-closed on an unknown producer identity. **CURED in every live layer.**

The old `elif producer and by == producer:` silently disabled itself. All four layers where independence is actually evaluated now refuse explicitly:

| Layer | Line | Behavior |
|---|---|---|
| classifier condition (2) | `directive_registry.py:255-258` | `elif not _identity_key(producer): refusals.append("...unevaluable independence test is refused (fail closed)")` |
| `_v2_task_unresolved` | `directive_registry.py:936-940` | explicit `if not producer:` reason |
| `_v1_task_unresolved` | `directive_registry.py:1005-1009` | explicit `if not producer:` reason |
| `deferred_requirement_discharge` | `directive_registry.py:855-857` | explicit `if not producer:` reason |

Reproduced through the real call path — both cases that released in round 1 now gate:

    producer EMPTY,  self-attested (classified_by == producer)   DEFERRED=False  blocks=True
    producer None,   self-attested                               DEFERRED=False  blocks=True

This also closes round-1 G3's **O2** and round-1 G5's probes **C** and **D**.

**Severity: resolved.**
```

END OF PART 1. Part 2 follows immediately: F4–F8 with the reproducible bypass, the regression check, suite/validator results, AS-5/owner ruling C2, non-blocking observations, verification scope and sandbox refusals, required rework, and the reviewer conclusion with the verdict.

G3 GATE REPORT — M0-T034 — ROUND 2 — **PART 2 of 2** (continues directly from part 1)

```markdown
## Item 5 — F4: one mutable unguarded packet key. **IMPROVED but NOT RESOLVED. Reproducible bypass. Severity: MEDIUM, binding.**

F4's stated property is "a second durable record **the packet cannot unilaterally retract**". The packet can still retract it — it now takes two keys instead of one, both in the same file and both outside the material identity.

Reproduction (synthetic temp ledger, resolver stubbed, real ledger untouched):

    A. untouched accepted packet                                       blockers=1   material_digest_moved=False
    B. delete post_accept_verification ONLY                            blockers=1   material_digest_moved=False
    C. delete post_accept_verification AND directive_refs              blockers=0   material_digest_moved=False
    D. delete post_accept_verification + flip status off "accepted"    blockers=0   material_digest_moved=False
    E. empty directive_refs, keep the deferral record                  blockers=1   material_digest_moved=False

Cases **C** and **D** erase the obligation from **both** arms of the union and produce **zero** blockers. The cause is at `<REPO>/tools/project_control.py:619-623`: the re-derivation arm is gated on `t.get("status") == "accepted"` **and** a non-empty `directive_refs`. Neither field is in `MATERIAL_FIELDS` (`<REPO>/tools/directive_registry.py:1502-1504`, unchanged: ten keys, none of them these), so neither edit moves the material digest and neither is flagged by the new dirt guard — confirmed by the `material_digest_moved=False` column, which I computed with the shipped `material_digest()`.

**I verified the producer's reason for not taking the `MATERIAL_FIELDS` route, and it is sound.** `material_digest()` at `<REPO>/tools/directive_registry.py:1507-1512` builds `{k: task.get(k) for k in MATERIAL_FIELDS}`, so adding any key inserts a `null` entry into every packet's canonical JSON. Measured against the live ledger:

    tasks scanned                                                            : 77
    tasks carrying post_accept_verification today                            : 0
    tasks whose material digest WOULD move if the key joined MATERIAL_FIELDS : 77 / 77

That would retro-invalidate grandfathering for every legacy task — a retro-rejection of stored history, which AS-8 forbids. The producer was right to refuse it and right to route it to the already-decided C1 follow-up.

**So this is not a producer blunder; it is an unclosed gap with a real constraint behind it.** But F4 was declared binding at this gate and the property it names does not hold. Two ways forward, both cheap: gate the re-derivation arm on `_task_in_regime(t)` alone (dropping the `status == "accepted"` and non-empty-`directive_refs` preconditions, so a retracted field cannot silence it), or accept the gap explicitly on the record and hold F4 open until C1 lands — C1's decided inversion would pull `directive_refs` into the identity and close case C, though case D (a lifecycle-owned `status` field) would survive it.

## Item 6 — F5: attestation not bound to the identity it was made at. **NOT RESOLVED, and the stated reason does not hold. Severity: MEDIUM, binding.**

What was done: `classified_at` must now be a well-shaped **and calendar-valid** ISO-8601 date-and-time (`<REPO>/tools/directive_registry.py:176-190`, `_is_dated_attestation` + `ATTESTATION_TIMESTAMP_RE`), so `"t"`, `""`, `None`, a bare date, and `2026-13-99T99:99:99+00:00` all refuse. Reproduced — all five refuse through the real path. That is a genuine improvement and it is documented in condition (2).

What was not done: the attestation still carries no identity of its own. Verified by signature:

    acceptance_ordering_deferral (requirement_row, verification_row, producer: 'str' = '') -> 'tuple'
    'classified_at_identity' in module source : False

So the F5 scenario is fully live on the **grant** path: a verifier who re-verifies at a new identity and refreshes the record's `reviewed_manifest_sha256`/`reviewed_sha` carries every existing attestation forward untouched, and it still releases the row at the new identity. (The **discharge** path is bound — `deferred_requirement_discharge` compares both — but that is the other half of the lifecycle.)

**The producer's justification is refuted.** Producer report §10.2 and §9.5 state that closing F5 "needs a schema field I am forbidden to define". It does not. The classifier already reads **four** fields — `act_class`, `classified_by`, `justification`, `classified_at` — none of which are defined in `directive_verification.schema.json` either; all four are admitted solely by `additionalProperties: true`. Reading a fifth is no more a schema definition than reading the first four was. And the identity is already in hand at the call site: `acceptance_ordering_deferral` is invoked at `<REPO>/tools/directive_registry.py:988` from inside `_v2_task_unresolved`, whose signature (`:915`) takes `reviewed_manifest_sha256` as a parameter. Passing it through and requiring `claim.get("classified_at_identity") == reviewed_manifest_sha256` is a change confined entirely to `tools/directive_registry.py` — an **allowed path**. F5 was closable in scope and was not closed.

## Item 7 — F6: case-sensitive independence comparison. **CURED where reachable.**

`_identity_key()` (`<REPO>/tools/directive_registry.py:196-201`, `strip().casefold()`, non-string -> `""`) is applied at the classifier (`:255,259`) and at all three verification-layer comparisons (`:870, 943, 1012`). Reproduced: a producer re-spelling itself as `" PROD-p "` against producer `"prod-P"` now **gates** where round-1 probe V released it.

**One unconverted site, and it is dead code.** `<REPO>/tools/directive_registry.py:682` inside `unresolved_requirements()` retains the old `elif producer and verifier == producer:` shape — both case-sensitive and fail-open on an empty producer. A repo-wide search finds **zero callers**:

    $ grep -rn "unresolved_requirements" --include=*.py --include=*.md --include=*.json .   (excluding task_unresolved_requirements and gate reports)
    ./tools/directive_registry.py:664:    def unresolved_requirements(...)      <- the definition only

Unreachable today, so not a live defect. Flagged as a latent hazard: it is the last copy of the exact pattern F3 and F6 were raised to eliminate, and it would fail open if ever re-wired. **Severity: LOW / observation.**

Separately and for the record: `<REPO>/tools/project_control.py:1085` and `:1196` also compare reviewer against `producer` case-sensitively with a `producer and` short-circuit. These are the **pre-existing M0-T014-era gate-roster checks**, a different mechanism from directive verification, untouched by this task and outside what F3/F6 named. Not charged against this gate; noted so the next reviewer does not rediscover them as new.

## Item 8 — F7: absolute-path leak recurrence. **RECURRED.** See D3 in part 1. **Severity: BLOCKING.**

## Item 9 — F8: `lifecycle_classification` outside the schema, so CI never validates it. **NOT RESOLVED — and structurally unfixable by this producer. Severity: MEDIUM, orchestrator decision required.**

Verified unchanged at HEAD:

    $ git diff --name-only 05ee1917 HEAD -- project-control/directives tools/validate_directive_compliance.py
    (0 files)
    $ grep -c "lifecycle_classification" project-control/directives/schema/v1/directive_verification.schema.json  ->  0
    $ grep -c "lifecycle_classification" tools/validate_directive_compliance.py                                   ->  0

**I confirm the producer's containment argument.** The schema lives under `project-control/directives/**`, which the packet lists as a forbidden path and reserves to the orchestrator's D-001 capture authority; `tools/validate_directive_compliance.py` is forbidden **by design** so the validator stays an independent check on the code being changed. The producer could not have fixed F8 without breaching containment, and correctly did not. **This must not be charged to the producer** — it needs an orchestrator scope decision: widen M0-T034's `allowed_paths`, or fold the schema/validator work into the C1 follow-up (which already touches this area), and record the choice.

The residual risk is real but bounded: the classifier validates every field of the attestation and fails closed on each malformed shape, so an invalid attestation yields a refusal and never a deferral. It is one layer, not two, and CI does not check the shape.

## Regression check — round-1 credited findings all hold

**Rider 1 — unattested rows default INTO the gate set. Verified from code and by probe; strengthened since round 1.** 22 attestation-axis shapes through the real `task_verification_result` path:

    NO lifecycle_classification key at all                 DEFERRED=False  blocks=True
    lifecycle_classification = None / {} / True / string   DEFERRED=False  blocks=True
    whitespace-only classified_by + justification          DEFERRED=False  blocks=True
    self-attested (by == producer)                         DEFERRED=False  blocks=True
    self-attested, RESPELLED " PROD-p "                    DEFERRED=False  blocks=True   <- F6 fix
    producer EMPTY / None, self-attested                   DEFERRED=False  blocks=True   <- F3 fix
    undated / impossible-date / date-only attestation      DEFERRED=False  blocks=True   <- new
    act_class case-variant "Accept" / outside enum "merge" DEFERRED=False  blocks=True
    row events [accept,gate] / empty list                  DEFERRED=False  blocks=True
    row classification prohibition / hold / "Sequencing"   DEFERRED=False  blocks=True
    FULL well-formed attestation (sequencing / obligation) DEFERRED=True   blocks=False
    UNEXPECTED RELEASES: NONE

I also ran a 1,105,920-shape sweep asserting that **every** release satisfies all five stated conditions. 72 releases, and every apparent exception resolved to the documented whitespace-strip on `act_class` (`" accept "` -> `accept`), which round-1 G5 recorded as intentional. **No release violates the stated rule.**

**Vacuous-guard fix intact**, reproduced against the real repository at HEAD for M0-T027's actual scope:

    OLD raw-blob identity  : e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  entries=0
    sha256(empty byte str) : e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855   <- IDENTICAL
    NEW control-plane entries: 5   err=None

**AS-8 — ordinary scopes byte-identical to before.** I loaded the base and HEAD versions of the module side by side and recomputed:

    ['tools/project_control.py'] old=82ba83bd5e0c6e86 new=82ba83bd5e0c6e86 identical=True
    ['tools/']                   old=4e24ec70d3c3b9db new=4e24ec70d3c3b9db identical=True
    ['docs/']                    old=90a8c7a3552dedd3 new=90a8c7a3552dedd3 identical=True
    ['apps/']                    old=e0138e61373dc420 new=e0138e61373dc420 identical=True
    ['services/']                old=8e31d8f9da4e098d new=8e31d8f9da4e098d identical=True
    ['.github/']                 old=0272ee498b6742ea new=0272ee498b6742ea identical=True
    ['tools/','docs/']           old=f741ae0d16966a77 new=f741ae0d16966a77 identical=True

**AS-3 — no special-casing.** AST-parsed the executable bodies of all ten new/changed functions in both modules and scanned for `getenv|environ|force|bypass|override|allowlist_task` and any ledger task id or requirement id. Every hit resolved to docstring/comment provenance prose (`D-004-R629`, `D-004-R630`, "there is no bypass flag"). `project_control.py` reads the environment **nowhere**; `directive_registry.py`'s only `os.environ` use is `GIT_LITERAL_PATHSPECS=1`, a hardening. Classification derives from row semantics only.

**AS-9 — containment clean.** The round-2 commit touches exactly five files, all in `allowed_paths`:

    project-control/reports/M0-T034-producer-report.md
    tools/directive_registry.py
    tools/project_control.py
    tools/test_directive_compliance.py
    tools/test_project_control.py

    $ git diff --name-only 05ee1917 HEAD -- project-control/directives tools/validate_directive_compliance.py
    0 files

No requirement row's applicability was edited; `project-control/directives/**` is untouched across the whole branch (D-004-R627 holds).

**All three suites green at the frozen SHA, run by me:**

    $ python tools/test_project_control.py
      OK: all 22 project-control test groups passed        (was 20)
      S10 [D-004-R413/R414]: 10/10 blocks, 118 assertion cases   (UNCHANGED - no-regression evidence)
      S11 AS-2: 35 cases incl. positive control            (was 10)
      S11 deferral is not waiver: 9 cases incl. positive control   (new)
      S11 an unknown producer identity fails closed        (new)
      PC_EXIT=0

    $ python tools/test_directive_compliance.py
      Ran 98 tests / OK                                     (was 83, from a 55 baseline)
      DC_EXIT=0

    $ python tools/validate_directive_compliance.py --check
      VAL_EXIT=0

**New coupling, verified benign today.** `checkpoint` now loads the directive registry whenever any accepted in-regime task exists. Measured against the live ledger: registry loads in **53 ms** with **0** errors, **11** accepted in-regime tasks spanning **12** (task, directive) pairs, **0** pairs re-derive a non-empty outstanding set, and `_post_accept_verification_blockers()` returns **0** blockers. The producer's numbers reproduce. The availability trade the producer disclosed is real but adds nothing today.

## AS-5 and owner ruling C2 — cited, not re-litigated

Owner ruling **C2** (2026-07-31, recorded in the AS-5 scenario record at `<REPO>/project-control/tasks/M0-T034.json:49`) is binding and I apply it as written: AS-5's **literal clause is NOT MET and PROVEN UNMEETABLE**, and the substituted material/lifecycle mechanism is **ACCEPTED in substance, as a mechanism**. I do not reopen either half. I confirm the two things C2 leaves to this gate: the mechanism is present and non-vacuous (the identity numbers above), and **the 43-field exclusion list is unchanged and un-endorsed** — `MATERIAL_FIELDS` at `<REPO>/tools/directive_registry.py:1502-1504` is byte-identical to round 1. That boundary is owner decision **C1**'s queued follow-up and is **out of scope here**; I flag only that F4 case C above is one of its concrete consequences, which strengthens the case for that follow-up.

## Other observations (non-blocking, for the record)

- **`_row_is_satisfied` documents an independence it does not check.** `<REPO>/tools/directive_registry.py:798-807` accepts `NOT_APPLICABLE` on a non-empty `not_applicable_justification` **and** a non-empty `not_applicable_approved_by`, but never checks that the approver differs from the producer — while the enclosing docstring at `:842` says "NOT_APPLICABLE with justification + **independent** approver". Pre-existing convention (the same presence-only reading appears at `:701-702` and `:983-985`), not introduced here, and the record-level `verifier != producer` check still applies to the record as a whole. Wording nit worth correcting so the stated standard matches the enforced one.
- **Condition (1) strips `act_class` but does not casefold it** (`" accept "` releases, `"ACCEPT"` refuses), while condition (5) does neither for `state` and condition (2) does both for identities. All three behaviors are defensible and two of the three are documented; condition (1)'s strip is not. Documentation nit only.
- **No test covers a corrupt task packet followed by `checkpoint`** — the producer disclosed this at §10.6 and correctly notes the re-derivation widens the gap slightly, since `checkpoint` now reads more state than before.
- **AS-13** (`<REPO>/project-control/reports/M0-T034-lifecycle-classification.md`) does not exist at this SHA. Expected — the packet assigns it to the orchestrator, written from the independent verifier's AS-10 return — but it remains outstanding for acceptance.

## What I verified independently vs. could not verify

**Independently verified by execution at the frozen SHA:** the frozen HEAD and clean tree; all three suite/validator runs with real exit codes; the 30-state D1 probe end-to-end through `task_verification_result`; the 124,416-shape never-raises fuzz; the 1,105,920-shape release-validity sweep; the 22-shape rider-1 attestation probe; the F4 union bypass on a synthetic ledger (cases A-E) with material-digest measurement; the `MATERIAL_FIELDS` widening impact across all 77 real packets; the F5 signature and call-site scope by `inspect.signature` and source; the dead-code status of `unresolved_requirements` repo-wide; the AS-8 byte-identity of seven ordinary scopes by loading both module versions side by side; the AS-3 AST scan; the AS-9 containment diffs; the vacuous-guard old/new identities against the real repository; the live-ledger effect of the new checkpoint coupling; repository visibility via `gh repo view`; and the D3 leak location and its presence on the `+` side of the round-2 diff.

**Could not verify:** the exhaustive per-requirement pass over D-004's `ALL` set — that is the `directive-compliance-verifier`'s lane, recorded in `verification.json`; the AS-10 per-row classification of the eight candidate rows, which is that verifier's judgment under D-004-R632 and which I deliberately did not make; AS-13, not yet in the tree; and the identity values at the **merged** head, whose `reviewed_sha` will differ once this branch lands.

**Sandbox refusals and substitute routes (none omitted, no check dropped):** the read-only guard refused one Bash heredoc file-write to the scratchpad, and the `Write` tool is not available in this context. Substitute in every case: piped `python -c` payloads with no `>` character anywhere, reading results from stdout. All probes above were executed by that route. I ran **no** write-producing command — no `tools/project_control.py` against the ledger, no git write, no `gh` write. The suites do drive the CLI, but only inside `tempfile.mkdtemp` scratch projects, and my F4 probe built its own temp ledger and restored the patched module globals in a `finally` block.

## Required rework

**Blocking, returns to the producer (both fixes are inside `allowed_paths`):**

1. **D3** — redact the machine username token at `<REPO>/project-control/reports/M0-T034-producer-report.md:716`. One word. Producer-amended, per the report-preservation rule.
2. **F5** — bind the attestation to the identity it was made at: pass `reviewed_manifest_sha256` into `acceptance_ordering_deferral` at the `<REPO>/tools/directive_registry.py:988` call site and require the claim to name it. No schema change is needed — the classifier already reads four fields admitted only by `additionalProperties: true`. Amend condition (2)'s stated rule to match, and add a test proving an attestation carried forward to a new identity no longer releases.

**Blocking, orchestrator decision required (the producer cannot fix these in scope):**

3. **F4** — either tighten the re-derivation gate at `<REPO>/tools/project_control.py:619-623` so retracting `directive_refs` or `status` cannot silence it, or record an explicit decision to hold F4 open until the C1 follow-up lands. Cases C and D above are the reproduction.
4. **F8** — decide whether to widen `allowed_paths` for the schema/validator work or fold it into the C1 follow-up. The producer was structurally forbidden from touching either target and correctly did not.

**Carried, non-blocking:** the dead-code fail-open at `directive_registry.py:682`; the `_row_is_satisfied` docstring/behavior wording; condition (1)'s undocumented strip; the missing corrupt-packet checkpoint test; AS-13 still outstanding for acceptance.

## Reviewer conclusion

The rework did the hard part right. Condition (5) is now an allowlist in a module that is allowlist-shaped everywhere else, and I could not find a single state — valid, invalid, malformed, wrong-typed, wrong-cased, or padded — that reaches deferral other than the literal token `pending`. The `TypeError` is gone and 124,416 fuzz inputs raise nothing, so the docstring's promise is finally true. The stated rule was amended in the same change, so AS-12 still buys a reviewer a rule to audit rather than behavior to infer. "Deferral is not waiver" moved from prose into code, with a discharge path that enforces independence, content identity and reviewed commit, backed by a nine-case CLI test that includes the packet-deletion scenario and a positive control. Independence no longer disables itself on an empty producer or a re-spelled name. Nothing regressed: ordinary scopes are byte-identical, the vacuous-guard fix is intact, S10's 118 assertion cases are unchanged, and all three suites pass at their stated counts. The producer disclosed its own unclosed items instead of burying them, and its refusal to widen `MATERIAL_FIELDS` was right for a reason I verified against all 77 packets.

It fails on three narrow things. The D2 cure put the machine username back into the same public file, inside the sentence claiming it had been removed — the fourth recurrence of R024, and the most direct evidence yet that per-report discipline is not working and the queued preservation-time redaction is the actual fix. F5 was left open on a reason that does not survive inspection: the classifier already reads four schema-undefined fields, and the identity is a parameter of the calling function, so the fix was in-scope all along. And F4's property — an obligation the packet cannot unilaterally retract — still does not hold; two hand-edits to an accepted packet erase it from both arms of the union without moving the material digest.

None of this touches the architecture, which I judge sound, and none of it reopens the permissive-classifier risk the owner cared most about — that risk is closed. Two of the four items are one-word and one-parameter changes; the other two are scope decisions only the orchestrator can make.

**VERDICT: FAIL.** Returns to the producer for D3 and F5; F4 and F8 require an orchestrator scope decision before re-gate.
```

END OF PART 2 — end of report.

**Orchestrator-facing summary (not part of the report):**
- HEAD verified `24d2d8034a753bbe89642ddf35dee13c7bb1aeb9` on `task/M0-T034-governance-acceptance-semantics`, clean tree. Running as **Opus 5** (`claude-opus-5[1m]`), not Fable 5.
- **Verdict: FAIL.** Round-1 blocking defects D1, D2(line 198), F2, F3 are all genuinely cured; F6 cured; zero regressions; 22 groups / 98 tests / validator all exit 0.
- **New blocking defect D3:** the D2 remediation reintroduced the machine username at producer-report line 716, in a PUBLIC repo, inside the sentence claiming it was removed. One-word fix. I redacted it in this report.
- **F5 unresolved** and the producer's stated reason ("needs a schema field I am forbidden to define") is refuted — the classifier already reads four schema-undefined fields and the identity is a parameter at the call site, so the fix is entirely inside an allowed path.
- **F4 unresolved** with a reproducible bypass: deleting `post_accept_verification` **and** `directive_refs` (or flipping `status` off `accepted`) yields zero blockers and does not move the material digest. The producer's refusal to widen `MATERIAL_FIELDS` is CORRECT — I verified it would move the digest of all 77 packets and retro-invalidate grandfathering, which AS-8 forbids. This needs your decision, not producer rework.
- **F8 unresolved and structurally unfixable by the producer** — both targets are forbidden paths by design. Needs a scope decision from you: widen `allowed_paths` or fold into the C1 follow-up.
- Two items you may want independently: the live ledger currently shows 0 post-accept blockers and 11 accepted in-regime tasks all re-deriving empty, so the new `checkpoint` -> registry coupling blocks nothing today; and `unresolved_requirements()` at `directive_registry.py:664` is dead code repo-wide still carrying the fail-open pattern F3/F6 eliminated everywhere else.
