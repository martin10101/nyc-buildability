<!--
PRESERVATION RECORD (orchestrator, 2026-07-31)
This file preserves the complete M0-T034 G3 ROUND-3 gate return exactly as the independent
reviewer agent `m0t034-g3-r3` delivered it to the orchestrator via SendMessage, in three
labelled parts ("PART 1 of 3" .. "PART 3 of 3"), preserved the moment they arrived. All
parts are concatenated here in order, separated by a single blank line. NO alteration was
made. The R024 scan found nothing to redact: the reviewer derived identity tokens from the
environment at runtime and printed counts only; no token appears in any form.
-->

PART 1 of 3 — G3 ROUND-3 GATE REPORT, M0-T034

# Gate Report — M0-T034 G3, ROUND 3 (independent)

**Gate:** G3 (code review)
**Task:** M0-T034 — Governance acceptance semantics: lifecycle-aware `accept()` + real guards for governance-shaped tasks
**Reviewer:** `m0t034-g3-r3` (role `code-reviewer`; independent — not the producer, not the round-1 or round-2 reviewer, not the G5 reviewer)
**Date:** 2026-07-31
**Round:** 3 (round 1 G3+G5 FAIL at `1298f4b`; round 2 G3 FAIL / G5 PASS-with-corrections at `24d2d80`)

**Model disclosure (D-004-R307).** I am running as **Opus 5**, exact model id `claude-opus-5[1m]`, dispatched at explicit Opus 5. I am **not** Fable 5 and make no such claim.

**R024 self-redaction.** Every path here is `<REPO>`-relative. I have excluded absolute paths, the machine username, hostname, and session/agent identifiers. Where I swept for identity tokens I derived them from the environment at runtime and printed **counts only** — no token is quoted in this report in any form, masked or otherwise. One probe raised a Python traceback containing an absolute path; I describe that fixture error in words and omit the trace.

## VERDICT: **PASS**

All three items returned to the producer in round 2 (D3, F5, the in-scope half of C3) are cured, verified by my own execution at the frozen SHA. No round-1 or round-2 credited finding regressed. Containment is exact. F4 and F8 are explicitly ruled on (owner rider 4, PART 2) as a named follow-up bundle, not as blockers.

## HEAD verification (first act)

```
$ git rev-parse HEAD
dbf0a887aabebb55958d9e96e8584c41e443258a     <- equals the frozen reviewed SHA
$ git status --porcelain | wc -l
0                                            <- clean tree
```

Round-3 commit `dbf0a88`, base `5474b3e`, branch `task/M0-T034-governance-acceptance-semantics`.

---

# PART A — OWNER RIDER DISPOSITIONS

The six owner riders of 2026-07-31 bind this report. Each gets an explicit disposition; supporting detail is in PART B (message 3 of 3).

## Rider 1 — D1: does the AS-2 suite probe OUTSIDE the old denylist, and does `state: []` still raise? **DISPOSITION: SATISFIED.**

The prior suite certified the hole because a denylist certifies only the values its author enumerated. This one does not.

**The suite reaches outside.** AS-2 case (vii) at `<REPO>/tools/test_project_control.py:2278-2293` iterates **20** state values and the comment states the intent explicitly ("The probe deliberately reaches OUTSIDE the old {FAIL, BLOCKED} denylist … the independent verifier stating it COULD NOT verify the obligation must never read as permission to defer it"). The set is `UNVERIFIABLE, FAIL, BLOCKED, fail, blocked, "FAIL ", Pending, "pending ", PASSED, "", wat, None, 0, 1, False, True, [], ["pending"], {}, {"state": "pending"}` — covering UNVERIFIABLE, case variants, whitespace variants, null, the empty list, and non-string types. Each iteration asserts the refusal names the stated rule (`"not an explicitly pending row"`) **and** that no `Traceback` appears. An **absent** state key is covered separately at `:2294-2301`. These run at the **CLI** level through `accept()`, and each also asserts the task does not move off `awaiting_gate` and that no deferral is registered.

**Independently re-derived, not read.** I probed **26** values beyond the old two-token list — `UNVERIFIABLE`, `unverifiable`, `Unverifiable`, `None`, `""`, `"   "`, `[]`, `{}`, `["pending"]`, `{"k":"pending"}`, `0`, `1`, `False`, `True`, `PASSED`, `wat`, `Pending`, `"pending "`, `" pending"`, `PENDING`, `fail`, `blocked`, `"FAIL "`, `set()`, `()`, `3.14`:

```
values probed beyond the old two-token list: 26
   raised     : none
   deferred   : none
   unnamed    : none
   allowlist  : ['pending']
```

Zero raised, zero released, every refusal named the stated rule.

**`state: []` specifically — the round-1 crasher.** Included in the 26 above: **no exception** and **no deferral**. The `isinstance(state, str)` guard at `<REPO>/tools/directive_registry.py:122-125` is documented as load-bearing precisely for this ("an unhashable state (e.g. `[]`) must REFUSE, never raise, or a malformed row would abort the acceptance evaluation instead of failing closed within it"). The docstring's "never raises" promise is now true rather than asserted — see the 24,000-shape fuzz in PART B.

**Structural confirmation:** `DEFERRABLE_VERIFICATION_STATES` is `frozenset({"pending"})` — a one-token **allowlist**. The test at `<REPO>/tools/test_directive_compliance.py:1125-1126` asserts the denylist-shaped constant `NEGATIVE_VERIFICATION_STATES` does not reappear anywhere in the module source, so the inversion cannot be quietly undone.

**Sandbox note:** my isolated absent-state-key probe was refused by my read-only guard (the dict filter on the `"state"` key pattern-matched a control-plane mutation rule). Substitute route, no check dropped: `row.get("state")` returns `None` for an absent key, and `None` is in my 26-value probe and refused; the CLI-level absent-key case at `:2294-2301` passed under my own execution of the full suite.

## Rider 2 — condition (6): exact binding at BOTH call sites, and do the carried-forward tests isolate the stale stamp as sole cause? **DISPOSITION: SATISFIED.**

**Both call sites bound, and I exercised both.**

| Call site | Location | Verified by |
|---|---|---|
| v2 (the path `accept()` calls) | `<REPO>/tools/directive_registry.py:1042-1043` | Probe A + CLI probe B |
| v1 (dormant legacy shape) | `<REPO>/tools/directive_registry.py:1095-1096` | Probe D |

Both pass `reviewed_manifest_sha256` — a real parameter of each enclosing function (`_v2_task_unresolved` at `:965-966`, `_v1_task_unresolved` at `:1053-1054`), so neither argument is a stray. Grep confirms these are the **only** two production call sites; the sole test call without the argument (`<REPO>/tools/test_directive_compliance.py:1007-1012`) is deliberately the default-refuses test.

**The comparison is exact string equality** at `<REPO>/tools/directive_registry.py:346-361`: `isinstance` guards first, an unusable `expected_identity` refuses with its own named reason, then `not isinstance(stamped, str) or stamped != expected`. No normalisation, so a re-cased or re-spaced stamp refuses rather than being silently accepted.

**Non-circularity — the property that makes the whole condition mean anything.** I verified this rather than assuming it. `accept()` computes the identity **from git** at `<REPO>/tools/project_control.py:541` (`identity, resolved_sha, ierr = _task_git_identity(reg_mod, t)`) over the task's `allowed_paths` at the resolved commit, and passes it at `:568`. It is **not** read from the verification record — the record's own `reviewed_manifest_sha256` is separately compared against the same computed value at `<REPO>/tools/directive_registry.py:997-1000`. The attestation must therefore name a git-derived value the verifier could not choose after the fact.

**The carried-forward tests do isolate the stale stamp as sole cause.** `CarriedForwardAttestationTests` at `<REPO>/tools/test_directive_compliance.py:1163-1225` drives `task_verification_result()`, not the classifier in isolation. `test_the_same_attestation_carried_forward_to_a_new_identity_no_longer_releases` (`:1201-1217`) refreshes the record's `reviewed_manifest_sha256` to a new identity while carrying the per-row attestation forward untouched, asserts the row no longer releases and falls back to ordinary "not PASS" gating — then **re-stamps the attestation at the new identity and asserts the deferral returns**. Changing that one field and nothing else is what makes the stale stamp the sole cause; a bare negative test could not establish it. A sibling test covers the unavailable expectation; `:1193-1199` is the positive control.

I reproduced this myself end-to-end:

```
PASS P1  positive control defers at the attested identity
PASS P2  stale carried-forward attestation does NOT release (names the key, falls back to "not PASS")
PASS P6  re-stamping at the new identity restores the deferral -- stale stamp isolated as sole cause
```

…and at the CLI boundary with a positive control on the same fixture (PART B, probe B).

## Rider 3 — did the round-2 fixes (F2 discharge parity, F3 empty-producer) survive round 3 unchanged? **DISPOSITION: SATISFIED — proven byte-exact, not spot-checked.**

I parsed both revisions and compared every relevant function AST-normalised across `5474b3e..dbf0a88`:

```
deferred_requirement_discharge     IDENTICAL     <- F2 discharge parity
outstanding_lifecycle_claims       IDENTICAL
task_verification_result           IDENTICAL
_row_is_satisfied                  IDENTICAL
_identity_key                      IDENTICAL     <- F6 case/whitespace independence
_text                              IDENTICAL
_is_dated_attestation              IDENTICAL     <- round-2 condition (2) dating fix
_v2_task_unresolved                CHANGED
_v1_task_unresolved                CHANGED
acceptance_ordering_deferral       CHANGED
```

For the three CHANGED functions I extracted the exhaustive line-level delta, short enough to state in full:

- `_v2_task_unresolved` — **1 line**: the call site gains `reviewed_manifest_sha256`.
- `_v1_task_unresolved` — **1 line**: the same.
- `acceptance_ordering_deferral` — the signature gains `expected_identity=None`; the docstring changes five→six and documents the new argument; the condition-(6) block is added (5 statements); the returned deferral dict gains `classified_at_identity`.

**Nothing else changed.** The F3 empty-producer refusals in `_v2_task_unresolved` (`:988-991`), in `_v1_task_unresolved` (`:1061-1063`), and condition (2) inside the classifier are all outside that delta — untouched. F2's discharge function is byte-identical. This is an exhaustive proof, not a sample.

Behaviourally re-confirmed at this SHA:

```
PASS R4 F3: an unknown producer identity fails closed (6 shapes: "", None, "   ", 7, [], {})
PASS R5 F6: independence is case- and whitespace-insensitive in both directions (4 pairs)
PASS P8 condition (2) intact: producer == classified_by still refuses even with a correct stamp
OK: S11 deferral is not waiver -- post-accept discharge held to the gate's own standard (9 cases)
OK: S11 an unknown producer identity fails closed (independence is never inert)
```

--- END PART 1 of 3 — riders 4-6 follow in PART 2 ---

PART 2 of 3 — G3 ROUND-3 GATE REPORT, M0-T034 (owner riders 4-6)

## Rider 4 — F4 and F8: block, or a named follow-up bundle? **DISPOSITION: THEY DO NOT BLOCK. G3 accepts them as the named follow-up bundle below.**

Silence is not a disposition, so I rule explicitly.

**Neither F4 nor F8 lowers the acceptance bar, which is the standard rider 1 of the task packet sets.** F4's residual requires an actor who already has write access to the task packet to retract two fields simultaneously; it does not admit any *attestation* that should have been refused. F8's residual is a missing second layer (CI schema validation), not a hole in the first — the classifier validates every field of the attestation and fails closed on each malformed shape, so an invalid attestation yields a refusal and never a deferral. Both were correctly *not* fixed in scope: F8's two targets are `forbidden_paths` by containment design, and a producer who had "fixed" them would have failed AS-9; F4's `MATERIAL_FIELDS` route would have retro-invalidated grandfathering for every legacy packet, which AS-8 forbids.

**The recorded decisions are present and accurate.** Both are in the task packet's progress log, `<REPO>/project-control/tasks/M0-T034.json`, entry `at: 2026-07-31T16:55:24.148133+00:00`, agent `orchestrator`, explicitly "subject to owner veto". I checked the record against both round-2 reports rather than accepting it:

- **F4** — recorded as "two-key packet tamper, cases C/D … HELD OPEN and folded into the owner-queued C1 MATERIAL_FIELDS follow-up task, per both reviewers' convergent recommendation". Round-2 G3 (item 5) named cases C and D and offered "hold F4 open until C1 lands" as one of two routes; round-2 G5 (axis 4) graded it "SUBSTANTIALLY CLOSED, residual F4-R (MEDIUM, non-blocking) … Fold into the C1 follow-up". The recommendations do converge. **Accurate.**
- The record's technical rationale for rejecting the in-task alternative — "dropping the `status==accepted` precondition would misclassify pre-accept lifecycle rows as post-accept blockers" — I verified independently: `outstanding_lifecycle_claims` (`<REPO>/tools/directive_registry.py:946-963`) has no acceptance-state precondition of its own, so removing the gate at `<REPO>/tools/project_control.py:632` would surface pending lifecycle claims on tasks not yet accepted, blocking `checkpoint()` before acceptance. **The rationale is correct.**
- The commitment that "the union docstring's 'no single mutable record' claim will be softened by the producer in round 3" matches G5 correction C3 in substance and **is done** (PART B item 3).
- G5's c15-scope observation (M0-T034 absent from D-004's manifest scope) is carried to the same follow-up, as G5 asked. **Accurate.**
- **F8** — recorded as "contracted as its own follow-up task folded into the C1 follow-up scope, per G5 correction C2 — both targets are forbidden paths by containment design and MUST NOT be widened into M0-T034". Matches round-2 G3 item 9 and round-2 G5 axis 4 exactly. **Accurate.**

**G3 accepts them into this named bundle, which is BLOCKING for the follow-up, not for M0-T034:**

> **Follow-up bundle "C1 MATERIAL_FIELDS boundary + attestation validation"** — the owner-decided C1 follow-up already queued after M0-T027 acceptance, carrying:
> 1. **F4 residual** — the two-key packet retraction (cases C and D). C1's decided inversion pulls `directive_refs` into the material identity and closes case C; case D (`status`) needs the same treatment or an obligation record outside the task packet.
> 2. **F8** — define `lifecycle_classification` in `<REPO>/project-control/directives/schema/v1/directive_verification.schema.json` and mirror conditions (1), (2), (4), (5) — **and now (6)** — in `<REPO>/tools/validate_directive_compliance.py`, so CI checks the attestation independently of the code path that releases it.
> 3. **G5's c15 scope gap** — D-004's manifest scope is `['M0-T027','M0-T028','M0-T029','M0-T033']`, so validator check c15 does not cover M0-T034 itself.
> 4. **F5's remaining residual** — the attestation is now bound to *content*, but remains transportable between records at the *same* identity. Materially narrowed this round; named so it is not lost.
> 5. **OBS-6** — redaction at preservation time (the systemic cause of the D3/F7 recurrences; 76 tracked files carry the token).

**Conditions on this acceptance, on the record:** (a) the bundle must exist as a controlled task before M0-T034's own post-accept verification closes, so it cannot evaporate; (b) `allowed_paths` for M0-T034 must **not** be widened to absorb any of it, per the containment design both round-2 gates upheld; (c) items 1 and 2 must not be split apart, since F8's validator work is what would independently catch a malformed attestation that item 1's identity work assumes is well-formed.

If the orchestrator does not contract that bundle, F4 and F8 revert to blocking findings and this disposition does not carry.

## Rider 5 — rule on the producer's disclosed items 1, 2 and 4. **DISPOSITION: ALL THREE ACCEPTABLE. No rework.**

**Item 1 — exact equality in (6) versus case-insensitive in (2). ACCEPTABLE.** The distinction tracks a real difference in the compared values: (2) compares agent names a human types, where re-spelling is expected and must not defeat an independence check; (6) compares a machine digest that is never retyped, where any variation is evidence of tampering or of a copied attestation. The reasoning is stated in the rule at `<REPO>/tools/directive_registry.py:136-141`, so it is auditable rather than inferred. Decisively, the failure mode is asymmetric in the safe direction: across my 24,000-shape fuzz every near-miss produced a refusal and **not one** produced a release. Under rider 1 of the task packet — a classifier one notch too permissive is the worst outcome this task can produce — strictness is the correct error to make. The producer's own framing of the risk (a confusing refusal for a verifier who pastes a stray newline) is accurate and is the lesser harm.

**Item 2 — binding the dormant v1 path as well. ACCEPTABLE, and now proven rather than argued.** G3 r2 named only the v2 site, so this is scope the producer added. I did not take the safety on assertion: I exercised the v1 path directly, since an untested dormant path is exactly where a stray argument yields a `NameError`.

```
PASS V1a v1 path executes without raising and DEFERS at the attested identity
PASS V1b v1 path REFUSES a stale carried-forward stamp (cond. 6 bound here too)
PASS V1c v1 path never raises and never releases across 11 malformed stamps
PASS V1d v1 path with an UNAVAILABLE expected identity gates rather than releases
```

The alternative — leaving one copy fail-open behind a path that could be re-wired — is the worse risk, and this matches the round-2 F3/F6 precedent both gates credited.

**Item 4 — amending more of §9.9 than the single token G3 named. ACCEPTABLE, and better than the minimal fix.** The defect was never the token; it was *quoting a pattern inside the sentence asserting that pattern has no matches*. Three of the four quotations had that shape, so redacting one would have left the sentence self-falsifying in three remaining ways — a cure that re-fails on the next sweep. The edit is confined to the producer's own evidence (permitted under the report-preservation rule), is annotated in place at `<REPO>/project-control/reports/M0-T034-producer-report.md:723-726` so no reader mistakes amended text for what was submitted, and the round-2 G3 report independently preserves what the original said. The audit trail is intact.

## Rider 6 — D3: zero literal matches on ADDED lines and in tracked `tools/`, removed-side occurrences being the redacted lines themselves. **DISPOSITION: SATISFIED, with one minor evidence-accuracy note against the producer's own table.**

**Added side — zero, in every form I could construct:**

```
round-3 diff: 596 added lines, 65 removed lines

pattern                          ADDED   REMOVED
machine username                     0         1
home prefix (forward-slash)          0         0
home prefix (backslash)              0         0
git-bash home prefix                 0         0
home fragment (forward)              0         0
home fragment (backslash)            0         0
hostname                             0         0
```

**Tracked files — zero.** Sweep over the producer report plus all 20 tracked `tools/` files, five patterns, token taken from the environment and never typed:

```
files in sweep scope: 20
machine-username         matches: 0
windows-home-prefix      matches: 0
git-bash-home-prefix     matches: 0
home-path-fragment       matches: 0
hostname                 matches: 0
hit files: []
```

Every tracked M0-T034 artifact is clean, including the immutable round-1 and round-2 gate reports and the packet:

```
project-control/gates/M0-T034-G3.json                : 0
project-control/gates/M0-T034-G5.json                : 0
project-control/reports/M0-T034-G3-report.md         : 0
project-control/reports/M0-T034-G3-report-r2.md      : 0
project-control/reports/M0-T034-G5-report.md         : 0
project-control/reports/M0-T034-G5-report-r2.md      : 0
project-control/reports/M0-T034-producer-report.md   : 0
project-control/tasks/M0-T034.json                   : 0
```

**The single removed-side occurrence is the redacted line itself.** It sits in `<REPO>/project-control/reports/M0-T034-producer-report.md` — the only file where a removal was required — is 80 characters (the report's wrap width), and contains "re-swept" and "`tools/`". That identifies it as the wrapped §9.9 sentence round-2 G3 located. Its appearance on the `-` side is unavoidable when the fix is a deletion, and it introduces nothing new because that line was already committed in round 2.

**The cure is structural, not cosmetic.** At `<REPO>/project-control/reports/M0-T034-producer-report.md:716-721` the four sweep patterns are now **described in prose** ("the machine username … the Git-Bash and the Windows absolute home-directory prefixes, and the home-directory path fragment") rather than enumerated literally, so the sentence can no longer be its own counterexample.

**Minor evidence-accuracy note.** The producer's §11.4 Command E table reports removed-side counts of **1** for each of four patterns (username, git-bash home prefix, windows home prefix, home-directory fragment). I reproduce **1** for the username and **0** for all three home-path patterns, in both slash conventions. The producer's table therefore over-reports three of its four removed-side rows. This is in the *conservative* direction — the report claims to have removed more sensitive content than it actually did — and it does not touch the cure, which rests on the added side and the tracked-file sweep, both zero. Recorded for accuracy, not as a defect requiring rework.

**Systemic context, disclosed not charged.** The token appears in **76 tracked files** repo-wide, including immutable accepted reports. That is pre-existing OBS-6, outside this task's `forbidden_paths` and correctly untouched; both prior G5 rounds graded this class LOW and recommended against loading a repo-wide sweep onto M0-T034. I reach the same conclusion independently, and item 5 of the rider-4 bundle carries it.

--- END PART 2 of 3 — supporting findings, regressions, Pyright adjudication and verdict follow in PART 3 ---

PART 3 of 3 — G3 ROUND-3 GATE REPORT, M0-T034 (supporting findings and verdict)

# PART B — SUPPORTING FINDINGS

## Item 1 — D3: the machine username in the producer report. **CURED.**

Evidence under rider 6 (PART 2). Round 2 failed because the D2 cure sentence *quoted* the token inside the very sentence claiming no matches remained; the round-3 fix does not repeat that pattern in any form, because the patterns are now described rather than enumerated. An inline amendment note at `<REPO>/project-control/reports/M0-T034-producer-report.md:723-726` records that the text was changed and why, so the report-preservation rule is respected and the audit trail intact.

## Item 2 — F5: attestation bound to the identity it was granted at. **CURED. Verified end-to-end, four independent ways.**

**Rule text amended (AS-12).** `<REPO>/tools/directive_registry.py:62` now reads "ALL SIX conditions", with **(6) IDENTITY-BOUND ATTESTATION** stated in full at `:127-146`, enumerating its refusals as explicitly as (1)–(5) do: absent key, null, empty or whitespace-only, non-string, case-variant, whitespace-padded, any other identity (naming the stale carried-forward case as the one that matters most), and an unevaluable expectation. The classifier docstring (`:240-262`) and the `project_control.py` module header (`:70`) match. The new constant `ATTESTATION_IDENTITY_KEY = "classified_at_identity"` is at `:197` with a comment recording that reading it defines no schema.

The producer added a **separate** condition rather than folding the check into (2) as G3 r2 suggested. I judge this **better than what was asked** — (2) is about *who* attested and (6) about *what content*, and folding a new refusal class into an already-audited condition would have hidden it. AS-12's test at `<REPO>/tools/test_directive_compliance.py:1154-1160` pins the rule text to contain "(6)", "IDENTITY-BOUND ATTESTATION", `ATTESTATION_IDENTITY_KEY`, "EXACT STRING", "CASE-VARIANT" and "UNEVALUABLE", so rule and behaviour cannot drift silently.

**Probe A — through `task_verification_result()`, the path `accept()` calls:**

```
PASS P1  positive control defers at the attested identity
PASS P2  stale carried-forward attestation does NOT release
PASS P3  all 20 malformed/near-miss stamps refuse with a named reason, none raise
PASS P4  absent classified_at_identity refuses
PASS P5  an UNAVAILABLE expected identity gates (never releases), 10 shapes
PASS P6  re-stamping at the new identity restores the deferral
PASS P7  condition (5) allowlist intact even with a correct stamp, 10 states
PASS P8  condition (2) intact: producer==classified_by still refuses with a correct stamp
PASS P9  record-level staleness still reported independently
PASS P10 deferral record carries classified_at_identity and does not alias the attestation
```

P3's 20 shapes: stale, uppercase, leading space, trailing space, trailing newline, trailing tab, truncated, extended, empty, whitespace-only, `None`, `int`, `float`, `list`, `dict`, `True`, `bytes`, `set`, `tuple`, nested object. P5's 10: `None`, `""`, `"   "`, `"\n"`, `int`, `list`, `dict`, `True`, `bytes`, `float`.

**Probe B — at the CLI `accept()` boundary, with a positive control on the same fixture:**

```
PASS E7 CLI accept refuses: stale carried-forward stamp
PASS E7 CLI accept refuses: ABSENT stamp (the pre-condition-(6) shape)
PASS E7 CLI accept refuses: case-variant stamp
PASS E7 CLI accept refuses: whitespace-padded stamp
PASS E8 POSITIVE CONTROL on the same fixture: a correctly bound stamp still accepts
```

Each refusal also asserts stderr names `classified_at_identity`, the row falls back to "not PASS", no `Traceback` appears, the task does not move off `awaiting_gate`, and no deferral is registered.

**Probe C — never-raises, independently re-derived.** 24,000 shapes (20 stamps x 20 expected identities x 10 states x 6 producers, including unhashable and non-string values on every axis):

```
fuzz shapes: 24000  exceptions: 0  releases: 4
PASS R2 never raises across 24000 heterogeneous shapes
PASS R3 every one of the 4 releases satisfied cond (2)+(5)+(6) exactly
```

Every release was re-checked to satisfy: usable string expectation, `stamp == expected` exactly, `state == "pending"`, known producer distinct from the classifier, empty refusal list. (The producer reported 1,444 shapes / 0 exceptions / 6 releases over a differently-shaped matrix; consistent.)

**Probe D — the dormant v1 path.** Under rider 5, item 2 (PART 2).

**Test honesty, verified by AST rather than by reading counts:**

```
tools/test_directive_compliance.py   98 -> 102 tests   REMOVED: none
   ADDED: test_condition6_attestation_must_be_bound_to_the_reviewed_identity
          test_an_attestation_defers_at_the_identity_it_was_made_at
          test_the_same_attestation_carried_forward_to_a_new_identity_no_longer_releases
          test_an_unavailable_expected_identity_gates_rather_than_releases
tools/test_project_control.py        22 -> 22 tests    REMOVED: none, ADDED: none
```

Every removed line in the test diff is a call-site signature update, the pinned-count update, or the five→six prose change. **No test was deleted or weakened.** AS-2's pinned count moved `35 -> 48` at `<REPO>/tools/test_project_control.py:2366`; the 13 new cases at `:2334-2354` are 12 stamp shapes plus the unstamped attestation, so 35 + 13 = 48 exactly, and the printed line was updated rather than left stale. The `attempt()` helper at `:2222-2233` asserts on every case that accept is refused, the task stays `awaiting_gate`, and no deferral is registered.

## Item 3 — C3: union docstring honesty. **CURED, with zero behavior change, proven mechanically.**

I diffed the logic, not the prose, by comparing ASTs with docstrings stripped:

```
old len: 71585  new len: 72754
AST-with-docstrings equal:      False
AST-docstrings-STRIPPED equal:  True
```

The round-3 change to `<REPO>/tools/project_control.py` is **docstring-only** — every statement and control-flow edge is equivalent. The producer correctly did **not** drop the `status == "accepted"` precondition, which is the in-task alternative G3 r2 offered.

**The docstring states exactly what the code delivers**, claim by claim against `:596-611`: arm (a) at `:627-631` (no acceptance-state precondition); arm (b) at `:632-636` and `:670-685`; "deleting the packet's deferral record alone does NOT erase the obligation" (arm (b) never reads that record); "(b) is reached through the SAME packet's `status` and `directive_refs`" (`:632-636` gates on exactly those); and "neither field is in MATERIAL_FIELDS", verified mechanically:

```
MATERIAL_FIELDS count: 10
  status                   material: False
  directive_refs           material: False
  post_accept_verification material: False
  allowed_paths            material: True     (control: the constant is non-vacuous)
```

**The residual reproduced end-to-end, in both directions**, driving the real CLI through `accept()` then `checkpoint()` on a temp project (the supported mechanism the suite itself uses, no monkeypatching):

```
PASS E1 accept succeeds with well-formed identity-bound attestations
PASS E2 deferral record carries classified_at_identity == the granted identity
PASS E3 case A (intact): first post-accept opportunity REFUSES
PASS E4 case B (packet deferral record deleted ALONE): STILL refuses via arm (b)
PASS E5 case C (record + status retracted): both arms silenced -- residual REAL
PASS E6 case D (record + directive_refs retracted): both arms silenced -- residual REAL
```

Case B's refusal contains "re-derived from", confirming arm (b) is speaking. **The docstring is honest in both directions**: it neither overstates what the union delivers (B) nor understates the residual (C, D). The module header at `:82-90` carries the same corrected wording.

## Item 4 — no regressions

**Suites and validator, under my own execution at the frozen SHA:**

```
$ python tools/test_project_control.py
OK: S11 lifecycle-aware acceptance + first-post-accept verification (AS-1, AS-4)
OK: S11 unmet NON-lifecycle rows still block acceptance (AS-2, 48 cases incl. positive control)
OK: S11 governance-shaped staleness identity + dirt guard (AS-5, AS-6)
OK: S11 reviewed_sha comparison + no-regression (AS-7, AS-8)
OK: S11 deferral is not waiver -- post-accept discharge held to the gate's own standard (9 cases)
OK: S11 an unknown producer identity fails closed (independence is never inert)
OK: S11 no special-casing; classification rule stated in code (AS-3, AS-12)
OK: all 22 project-control test groups passed
PC_EXIT=0

$ python tools/test_directive_compliance.py
Ran 102 tests in 66.346s -- OK
DC_EXIT=0

$ python tools/validate_directive_compliance.py --check   -> VAL_CHECK_EXIT=0
$ python tools/validate_directive_compliance.py           -> VAL_EXIT=0
  directive registry OK: 5 directive(s), 5 active; source hashes, ID append-only,
  and producer/verifier separation verified.
```

All counts match the producer's §11.4 claims. S10's 118 assertion cases and S7's 366 real ledger files unchanged. Against the live ledger, `_post_accept_verification_blockers()` returns **0** blockers and the registry loads with **0** errors across 5 directives.

**Rider 1 of the task packet — the default is to gate. Holds.**

```
PASS R1a a row making NO lifecycle claim gates silently (no release, no noise)
PASS R1b a bare pending row with no attestation gates
```

Unattested rows default **into** the gate set; attestation only ever releases. Condition (6) strengthens this — it adds a sixth way to stay in the gate set and no way to leave it.

**Conditions (1)-(5) intact under adversarial probes with a correct stamp present**, so the new condition cannot be masking a weakened old one:

```
condition (1)  17 act_class values; release set == the closed enumeration exactly     PASS
               ('ACCEPT','Accept','submit','gate','claim','','accepted',None,7,[],
                'accep','acceptx' all gate; the four owner-enumerated tokens release)
condition (3)   7 lifecycle_events shapes; only a SOLE {'accept'} binding releases    PASS
condition (4)  12 classifications; prohibition/hold/decision/authorization/dependency/
               harness/evidence/external_fact/return all structurally unreachable     PASS
condition (5)  per rider 1 (26 values beyond the old two-token list)                  PASS
condition (2)  per rider 3 (6 unknown-producer shapes, 4 re-spelling pairs)           PASS
```

**AS-8 byte-identical ordinary scopes.** Asserted at `<REPO>/tools/test_project_control.py:2512-2519` — an ordinary (non-control-plane) scope's identity equals the raw `git_tree_manifest` value byte for byte — and passing under my run. Structurally unreachable by this diff: `git_tree_manifest`/`frozen_git_identity` are untouched and `project_control.py` is docstring-only.

**Containment (AS-9). Exact.**

```
$ git diff --name-only 5474b3e..dbf0a88
project-control/reports/M0-T034-producer-report.md
tools/directive_registry.py
tools/project_control.py
tools/test_directive_compliance.py
tools/test_project_control.py

$ git diff --name-only 5474b3e..dbf0a88 -- project-control/directives tools/validate_directive_compliance.py
(0 files)
```

Exactly the five allowed files; no requirement row's applicability edited; the append-only invariant (D-004-R627) not holed. The whole-branch diff additionally shows `gates/`, the four preserved gate reports, `state.json` and `tasks/M0-T034.json` — all **orchestrator** lifecycle writes from `5474b3e` and earlier, absent from the round-3 commit. A naive containment read would flag them; they are correct.

## Item 5 — the flagged static-analysis items. **False positives, adjudicated by execution.**

**"Code is unreachable" at `directive_registry.py:498/519/525"** — pre-existing loader code, untouched by round 3 (shifted +27 by additions above it). I instrumented the module with a line tracer and loaded the **real** registry:

```
loaded: 5 directives, errors: 0
lines executed in the loader region (488-531):
[488, 489, 492, 493, 497, 499, 500, 501, 502, 505, 508, 509, 515, 516, 517, 518, 519, 524, 525, 526]
```

**499, 519 and 525 all execute.** (498 is a pure comment and emits no bytecode; the statement it introduces, 499, executes.) The non-executed lines are error branches not taken against a clean registry — correct behaviour, not dead code. **No unreachable guard exists here.**

Corroborating: Pyright reports **zero** diagnostics for `tools/directive_registry.py`, the only file with logic changes:

```
$ pyright --outputjson tools/directive_registry.py
"generalDiagnostics": [],  errorCount: 0, warningCount: 0
```

Across all four changed files it reports 136 errors — `project_control.py: 110`, `test_directive_compliance.py: 19`, `test_project_control.py: 7` — with **none** of category "unreachable" or "unused". The 110 in `project_control.py` are the known pre-existing Optional-access cluster, pre-existing **by construction** given the docstring-only change proven above.

**"Unused locals"** — Ruff finds exactly three, none on a round-3 added line: `test_project_control.py:2437` (`head2`, introduced M0-T034 round 1, cosmetic — the `git_commit_all` side effect is what the test needs and subsequent code reads HEAD via `head_of(tmp)`); `test_directive_compliance.py:807` (`reg`, M0-T023, cosmetic); `test_directive_compliance.py:341` (`m2`, M0-T023 — see observation 1).

This matches round-1's finding that earlier static-analysis escalations were false positives, but I reached it by execution and a second linter rather than by assuming either way.

## Observations (non-blocking, for the record)

1. **A pre-existing weak test, surfaced by the unused-local check.** `test_manifest_is_order_independent_and_content_based` at `<REPO>/tools/test_directive_compliance.py:339-346` computes `m2 = dr.content_manifest(["a/y.txt", "a/x.py"], ...)` with a deliberately different order and path spec, then never compares it — the sole assertion compares `content_manifest(["a"])` against `m1`, i.e. the same call to itself. The test's name and its own comment both claim order-independence, and **that property is not actually asserted**. Introduced by M0-T023 (`41957bb`, 2026-07-23), untouched by M0-T034, entirely outside this task's scope. **Not chargeable to this producer**; recorded so it is not lost.
2. **One stale prose residue:** `<REPO>/tools/test_project_control.py:2206` still says "Each of the **five** conjunctive conditions is broken in turn". Every authoritative statement of the rule says six (`directive_registry.py:62`, `:240`, `:248`; `project_control.py:70`; `test_directive_compliance.py:816`, `:860`), and the test does exercise condition (6) as case (xi), so AS-12 is met.
3. **Three normalization conventions coexist in one classifier**: (1) strips `act_class`, (2) strips and casefolds identities, (5) does neither, (6) does neither. All four defensible; three documented, condition (1)'s strip still the undocumented one. Carried unchanged from round 2.
4. **`unresolved_requirements` (`<REPO>/tools/directive_registry.py:715`) is dead code** — zero callers repo-wide — while its docstring says it "is used as EVIDENCE by `accept()`". `accept()` in fact uses `task_verification_result` / `task_unresolved_requirements`. Pre-existing, carried unchanged from round 2.
5. `_row_is_satisfied` still documents an independence it does not check (approver vs producer). Pre-existing convention, carried unchanged from round 2.
6. The `project_control.py` docstring names `MATERIAL_FIELDS` without noting it lives in `directive_registry.py`. Trivial.

## Outstanding for acceptance (not G3 defects, not the producer's)

- **AS-10** — the independent verifier's per-row classification of D-004-R322, R323, R388, R389, R486, R487, R488, R501. This is the `directive-compliance-verifier`'s judgment under D-004-R632 and **I deliberately did not make it**, as round-2 G3 also declined to. The code correctly names none of the eight — asserted by the AST scan at `<REPO>/tools/test_directive_compliance.py:1127-1133`.
- **AS-13** — `<REPO>/project-control/reports/M0-T034-lifecycle-classification.md` does not exist at this SHA. The packet assigns it to the orchestrator, written verbatim from the verifier's AS-10 return. Outstanding for acceptance.
- **AS-5** — owner ruling C2 is binding and cited, not re-litigated: the literal clause is NOT MET and PROVEN UNMEETABLE, the substituted mechanism is ACCEPTED in substance, and the ruling endorses the approach but **not** the 43-field list, which owner decision C1 queues separately.

## What I verified independently vs. could not verify

**Verified by my own execution at the frozen SHA:** HEAD and clean tree; all three suite/validator runs with real exit codes and counts; the D3 sweeps (tracked-file and added/removed diff sides, both slash conventions); the AST docstring-stripped equality proving zero behaviour change; the exhaustive function-level delta proving the round-2 fixes untouched; the 10-check condition-(6) probe through `task_verification_result`; the 5-check CLI probe with positive control; the 24,000-shape fuzz; the 4-check v1-path probe; the 6-case end-to-end union probe reproducing the F4 residual; the `MATERIAL_FIELDS` membership check; the non-circularity of the identity passed to condition (6); the 26-value outside-denylist probe including `state: []`; conditions (1)-(5) under 52 adversarial values; rider-1 direction; the test-function set comparison; the AS-2 count arithmetic; the containment diffs; the line-tracer refutation of the "unreachable" claim; Pyright and Ruff; and the F4/F8 record cross-check against both round-2 reports.

**Could not verify:** the exhaustive per-requirement pass over D-004's `ALL` set (the `directive-compliance-verifier`'s lane, recorded in `verification.json`); the AS-10 classification, deliberately not made; AS-13, not in the tree; and identity values at the **merged** head, whose `reviewed_sha` will differ once this branch lands.

**Sandbox refusals and substitute routes (none omitted, no check dropped).** My read-only guard refused several probe payloads on pattern grounds, and the `Write` tool is unavailable in this context, so I could not create a Pyright config to force hint-level diagnostics. Substitutes in every case: runtime line tracing instead of static reachability analysis (a stronger result); Ruff's F-rules for unused locals; `git diff` piped into `python` from the shell where in-process invocation was refused; and, for the absent-state-key case, the equivalent `None` value plus the CLI-level suite case at `:2294-2301`. Probes wrote only inside `tempfile.mkdtemp` scratch directories. I ran **no** write-producing command — no `tools/project_control.py` against the ledger, no git write, no `gh`. Read-only git inspection only.

## Reviewer conclusion

Round 3 is a genuine cure on all three returned items, and it holds up under independent re-derivation rather than resting on the producer's narrative. D3 is fixed structurally — the patterns are described rather than quoted, so the sentence can no longer falsify itself — with zero occurrences on the added side and in every tracked file. F5 is closed with a properly stated sixth condition whose comparison I proved non-circular, bound at both call sites, refusing by default on every axis I could construct, and driven to refusal from both the verification layer and the CLI with positive controls proving the stale stamp is the sole cause. C3 is now an honest statement of a real residual, delivering neither more nor less than the code does, with the union's logic provably untouched.

The round-2 fixes survived verbatim: the exhaustive delta to the three changed functions is the new parameter, the condition-(6) block, one new record field and two call-site pass-throughs, with F2's discharge function byte-identical and the F3 empty-producer logic outside the delta entirely. Condition (5) is a genuine allowlist that refuses 26 values beyond the two the old denylist enumerated, and the unhashable `state: []` that crashed round 1 now refuses without raising.

The producer disclosed six contestable choices and every one survives scrutiny; two of them I converted from argument to proof by exercising the paths directly. Rider 1 of the task packet — that a classifier one notch too permissive is the worst outcome this task can produce — is satisfied in the strongest direction available: releases require all six conditions simultaneously, and across 24,000 hostile shapes exactly four releases occurred, every one fully conformant.

F4 and F8 are ruled on explicitly: they do not block, and G3 accepts them into the named C1 follow-up bundle under the three conditions stated in rider 4 — if that bundle is not contracted, this disposition does not carry and they revert to blocking findings. AS-10 and AS-13 remain outstanding and belong to the independent verifier and the orchestrator respectively; they gate acceptance, not this gate.

**VERDICT: PASS.**

--- END PART 3 of 3 — report complete ---
