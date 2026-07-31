<!--
PRESERVATION RECORD (orchestrator, 2026-07-31)
This file preserves the complete M0-T034 G5 ROUND-3 gate return exactly as the independent
reviewer agent `m0t034-g5-r3` delivered it to the orchestrator via SendMessage, in two
labelled parts ("PART 1 of 2", "PART 2 of 2"), preserved the moment they arrived. Both parts
are concatenated here in order, separated by a single blank line. NO alteration was made.
The R024 scan found nothing to redact: the reviewer never reproduced the username token
(runtime string-splicing with count-only output), and used synthetic fixture digests.
-->

# Gate Report — PART 1 of 2

- **Gate id:** G5 (security / control-integrity)
- **Task:** M0-T034 — governance acceptance semantics
- **Round:** 3
- **Reviewer:** m0t034-g5-r3 (role: security-reviewer; independent — not the producer, not a prior reviewer)
- **Date:** 2026-07-31
- **Verdict:** **PASS** (stated in full at the end of PART 2)

## Model disclosure

I am running as **Opus 5**, exact model id `claude-opus-5[1m]`. I am **not** Fable 5. Dispatched at explicit Opus 5 under D-004-R307.

## HEAD verification (first act)

```
$ git rev-parse HEAD
dbf0a887aabebb55958d9e96e8584c41e443258a
$ git status --porcelain
(empty)
$ git rev-parse --abbrev-ref HEAD
task/M0-T034-governance-acceptance-semantics
```

Matches the frozen SHA. Tree clean. Prior verdicts inherit nothing; every finding is re-derived here.

## R024 compliance of this report

All paths are `<REPO>`-relative. I did **not** reproduce the literal machine username anywhere. Where I had to search for it I built the token at runtime by string-splicing and used **count-only / filename-only / line-number-only** output modes, so the token never entered the transcript. Digests shown are synthetic fixtures (`"a"*64` etc.), not real content hashes.

---

# OWNER RIDERS — EXPLICIT DISPOSITIONS

Each rider is answered on the record; supporting evidence is in the axes in PART 2.

## Rider 1 — D1: the AS-2 suite probes OUTSIDE the old denylist, and `state: []` no longer raises

**DISPOSITION: SATISFIED.**

The producer's pointer is accurate but I did not rely on it. AS-2 case (vii) at `<REPO>/tools/test_project_control.py:2278-2301` deliberately reaches outside the old `{FAIL, BLOCKED}` denylist over 20 state values — `UNVERIFIABLE`, `FAIL`, `BLOCKED`, `fail`, `blocked`, `"FAIL "`, `Pending`, `"pending "`, `PASSED`, `""`, `wat`, `None`, `0`, `1`, `False`, `True`, `[]`, `["pending"]`, `{}`, `{"state": "pending"}` — plus a 21st case with the **state key entirely absent**. Each asserts both `"not an explicitly pending row" in err` and `"Traceback" not in err`, and these run as real CLI `accept` invocations, so the no-raise assertion is meaningful rather than decorative.

**I re-derived this myself rather than trusting the suite that previously certified the hole.** Probing the classifier directly over 22 state shapes (the 20 above plus `()` and `0.0`):

```
states probed: 22
problems: NONE - all gated, none raised
state=[] deferral: None | reason cites pending row: True
POSITIVE CONTROL state='pending' releases: True
```

The round-1 `TypeError` on the unhashable `state: []` is gone: it now returns `None` with the "explicitly pending" refusal. The mechanism is the ordering at `<REPO>/tools/directive_registry.py:339` — `if not isinstance(state, str) or state not in DEFERRABLE_VERIFICATION_STATES` puts the type guard **before** the membership test, so an unhashable value can never reach `in`. An absent key is equivalent to `None` via `.get()` and refuses identically. The positive control releases, so every refusal is caused by the condition under test and not by an unrelated precondition. **This suite does not certify the hole the prior one did.**

## Rider 2 — Condition (6): exact binding at both call sites; stale refuses and a re-stamp restores deferral for that reason alone

**DISPOSITION: SATISFIED.**

Both call sites bind, proven by execution with working positive controls, not by reading argument lists: **v2 live** at `<REPO>/tools/directive_registry.py:1042-1043` and **v1 dormant** at `:1095-1096`. Full probe results in Axis 2 (PART 2).

On the carried-forward tests specifically (`<REPO>/tools/test_directive_compliance.py:1163-1226`): they drive `task_verification_result()` — the path `accept()` actually calls — and are correctly constructed as a **three-part** argument. `test_an_attestation_defers_at_the_identity_it_was_made_at` establishes the positive control (`reasons == []`, one deferral, stamped identity carried into the record). `test_the_same_attestation_carried_forward_to_a_new_identity_no_longer_releases` refreshes the record's `reviewed_manifest_sha256` to a new identity while carrying the per-row attestation forward untouched, asserts zero deferrals plus a `classified_at_identity` reason plus `"not PASS"` (proving the row falls back to *ordinary* gating rather than vanishing), and then — the part the rider asks about — **re-stamps the same attestation at the new identity on the same fixture and asserts the deferral is restored with `reasons == []`**. That final step is what proves the refusal was caused by the stale stamp *and by nothing else*. `test_an_unavailable_expected_identity_gates_rather_than_releases` covers the missing-expectation case.

I reproduced the same three-part structure independently through both `_v2_task_unresolved` and `_v1_task_unresolved`.

## Rider 3 — Round-2 fixes survived round 3 unchanged

**DISPOSITION: SATISFIED, mechanically.**

The round-3 hunk ranges in `<REPO>/tools/directive_registry.py` (old-file line numbers) are exactly: 59, 124-130, 169-175, 208-216, 217-224, 226-233, 310-316, 317-324, 985-993, 1035-1043.

| Round-2 fix region cited | Inside any round-3 hunk? |
|---|---|
| F2 discharge, `:829-902` | **No** — untouched |
| F3 empty-producer, `:864-866` | **No** — untouched |
| F3 empty-producer, `:937-940` | **No** — untouched |
| F3 empty-producer, `:1007-1009` | **No** — nearby hunks cover 985-993 and 1035-1043 only |
| F3 empty-producer, `:255-258` | **No** — within the classifier, but between hunks (226-233 and 310-316) |

Corroborated two independent ways: the AST comparison shows **54 of 57 functions byte-identical** with the F2 discharge and F3 refusal sites among them, and within the changed classifier the **first 19 statements (conditions 1-5) are byte-identical**. Both behaviours also execute green in my own run — *"S11 deferral is not waiver — post-accept discharge held to the gate's own standard (9 cases incl. positive control)"* and *"S11 an unknown producer identity fails closed (independence is never inert)"*. F6's `_identity_key` (`:228`) is likewise unchanged.

## Rider 4 — Explicit ruling on F4 and F8

**DISPOSITION: NEITHER BLOCKS. Both are ACCEPTED as a named follow-up bundle. This is an affirmative disposition, not silence.**

**F4 — does NOT block.** The residual is real: both arms of the union are reached through the same task packet, so an edit retracting the deferral record **and** either `directive_refs` or `status == "accepted"` silences both, and neither field is in `MATERIAL_FIELDS`, so the material identity does not move. I do not treat it as blocking because (a) round 3 did not introduce or worsen it — `project_control.py` has **zero executable change** this round; (b) the code no longer overstates itself, which was my round-2 C3 — the docstring at `<REPO>/tools/project_control.py:596-612` now states what IS delivered, what is NOT, and where the residual is held; (c) the in-task alternative is strictly worse, and I verified the producer did **not** take it — dropping the `status == "accepted"` precondition would misclassify every pre-accept lifecycle row as a post-accept blocker; and (d) exploiting it requires an actor who already has control-plane write access and is willing to retract a task's accepted status or its directive citation — itself a conspicuous mutation against rules that make accepted tasks immutable. It is a defence-in-depth gap, not an acceptance-bar lowering.

**F8 — does NOT block.** `lifecycle_classification` is still admitted only by `"additionalProperties": true` (`<REPO>/project-control/directives/schema/v1/directive_verification.schema.json:8,22`), and the validator knows neither key (`grep -c` over `<REPO>/tools/validate_directive_compliance.py` → **0**). This is a **containment success, not a defect**: both targets are in this task's `forbidden_paths` by design — the schema because registry writes are reserved to the orchestrator's D-001 capture authority, and the validator so it remains an *independent* check on the code being changed. A producer who had "fixed" F8 would have breached containment and failed AS-9. The residual risk is bounded and I measured it: the classifier validates every attestation field and fails closed on each malformed shape, so an unvalidated schema can yield only a refusal, never a spurious deferral — 50 hostile probes confirm it.

**The named follow-up bundle the gates accept in lieu of blocking:**

1. **FU-1 — `MATERIAL_FIELDS` boundary split** (owner decision C1, already queued). Absorbs the **F4** residual (two-key packet tamper, cases C/D) and the **c15 manifest-scope gap** (D-004's scope omits M0-T034).
2. **FU-2 — schema + validator mirror (F8).** Define `lifecycle_classification` in the v1 verification schema and mirror conditions (1), (2), (4), (5) **and now (6)** in `tools/validate_directive_compliance.py`, so CI checks the attestation independently of the code path it releases.
3. **FU-3 — OBS-6 systemic R024** redaction-at-preservation-time.
4. **FU-4 — D-001 capture convention (new, raised by me).** Any `lifecycle_classification` written from now on must include `classified_at_identity`. Zero live records carry either key today, so nothing is broken, but a record captured between this evidence and merge would refuse until re-stamped. The failure direction is **safe** (it gates, never releases), and the producer disclosed it at §11.6, but it belongs in the orchestrator's capture guidance, which the producer may not edit.

## Rider 5 — Ruling on the producer's disclosed items 1, 2 and 4

**All three: ACCEPTABLE. No rework.**

**Item 1 — exact string equality in condition (6) versus case-insensitive comparison in condition (2). ACCEPTABLE, and the inconsistency is principled rather than accidental.** The two fields are different kinds of thing and the two rules point the *same* way — toward refusal. A content identity is a machine-generated digest: every identity in this module originates from `hexdigest()` (`<REPO>/tools/directive_registry.py:383, 387, 1165, 1252, 1568`), which always emits lowercase hex, so an honestly produced stamp is byte-exact and case-insensitivity would only **add** permissiveness to a value that has no legitimate variants. An agent name is human-authored, where case and whitespace variants *are* the same identity — so insensitivity there makes the independence test **harder to defeat** by re-spelling. Strictness in (6) and leniency in (2) both enlarge the refusal set. The producer's stated worst case is correct and is the acceptable one: a verifier who pastes an identity with a stray newline gets a confusing refusal, never a permissive release. I verified the padded, case-variant and newline shapes all gate.

**Item 2 — binding the dormant v1 path as well. ACCEPTABLE; the offer to revert `:1096` should be DECLINED.** My dispatch instructions required verifying that *both* call sites bind, so reverting it would fail this gate's own axis. More substantively, leaving a dormant path unbound stores a fail-open for whoever re-wires it later, and the asymmetry would be invisible at the call site. Fixing both is the same call round 2 made for F3/F6 and was correct then. It is inside `allowed_paths`, and I proved by execution that the v1 path gates all six hostile variants while its positive control still releases — so the change is behaviour-preserving on the legitimate path.

**Item 4 — amending more of §9.9 than the single token G3 named. ACCEPTABLE.** The extra edit removes two further self-falsifying quotations of the *same* class in the *same* sentence. Leaving known R024 violations in place because only one was named would be a worse outcome and would have guaranteed a fourth recurrence. It is confined to the producer's own evidence file, which the report-preservation rule reserves to the producer, and it is annotated in place: `<REPO>/project-control/reports/M0-T034-producer-report.md:723-726` carries an explicit *"Round-3 amendment (producer, 2026-07-31)"* note recording what the sentence previously said and why it changed, so no reader can mistake the amended text for what was originally submitted. The result at `:716-720` describes the four patterns instead of quoting them and states the reason — fixing the *shape* of the mistake, not merely its instance. This is scope discipline, not scope creep.

*(Not asked, but on the record since they sit in the same list: item 3 — the `expected_identity` default — is acceptable; safety rests on the refusal, and I proved the 3-argument legacy call gates. Item 5 — the pinned AS-2 count of 48 — is a strengthening. Item 6 restates rider 4.)*

## Rider 6 — D3 redaction verified to the stated standard

**DISPOSITION: SATISFIED on all three limbs.**

| Limb | Evidence | Result |
|---|---|---|
| Zero literal matches on **added** lines | `git diff 5474b3e..dbf0a88 \| grep "^+" \| grep -ic <token>` | **0** (also **0** over `24d2d80..dbf0a88`) |
| Zero in tracked `tools/` | `git grep -il <token> -- tools/` | **empty — zero files** |
| Removed-side occurrences are the redacted lines themselves | see below | **confirmed** |

Exactly **one** removed line carries the token, and `git diff --stat -S<token>` localises it to `<REPO>/project-control/reports/M0-T034-producer-report.md` alone. I resolved its position without printing its content: it is **old line 716**, which falls inside **§9.9 "D2 — the absolute path in a public repo"** (old lines 706-719). That is precisely the sweep-pattern sentence my round-2 report flagged as line 716. So the sole removal is the redacted line itself — not a collateral deletion elsewhere.

At HEAD the token count is **0** in the whole producer report, **0** across all five touched files, and **0** under `tools/`. gitleaks over `24d2d80..dbf0a88`: 2 commits, ~115.80 KB, **no leaks found**.

END OF PART 1 — axes 1 through 7, sandbox constraints, scope limits and the verdict follow in PART 2.

# Gate Report — PART 2 of 2 (G5, M0-T034, round 3, reviewer m0t034-g5-r3)

# Axis 1 — R024 at this head (was G5 correction C1)

**FINDING: PASS. C1 discharged; the round-2 failure pattern did not recur, including inside the fix's own description of itself.**

Counts and gitleaks as in rider 6. The critical check — whether the cure re-committed the offence while describing itself, which is exactly how round 2 failed — comes out clean: `<REPO>/project-control/reports/M0-T034-producer-report.md:716-720` replaces the quoted pattern list with a description ("the machine username (named anywhere in this report only as `<user>`), the Git-Bash and the Windows absolute home-directory prefixes, and the home-directory path fragment") and states the reasoning inline. Verified by the zero-hit count, not by reading the claim.

**Absolute user paths, both slash forms.** Across the five touched files: no `C:/`, no `/c/Users`, no `/Users/`, no `Downloads`, no `USERPROFILE`/`HOMEPATH`/`APPDATA`. One residual elided form at `<REPO>/project-control/reports/M0-T034-producer-report.md:26` — `C:\...\.claude\worktrees\agent-<hex>` — has the user-identifying segment **already replaced by an ellipsis**, is attributed by `git log -S` to round-1 commit `a965c21`, and does not appear in the round-3 diff. Not new, and a bare drive letter is not machine-specific data.

**Session identifiers.** Zero. No `session-<hex>`, no UUID-shaped values.

**Agent worktree ids.** Six `agent-<hex>` references in the producer report (four already `<REPO>`-relative, at `:251`, `:713`, `:747`). Pre-existing and pervasive — **24 tracked files** under `<REPO>/project-control/reports/` carry the pattern, including immutable accepted reports. Repo-internal worktree names; not session ids; disclose nothing about the machine. Same disposition as round 2.

**Repo-wide backlog, stated honestly.** 76 tracked files still contain the token at HEAD, down from the 77 round 2 measured — this report is the one removed. That backlog sits in immutable accepted reports, is out of scope for M0-T034 (both prior G5 rounds recommended against loading a repo-wide sweep onto this task, and I reach the same conclusion independently), and is tracked as FU-3.

---

# Axis 2 — Condition (6) cannot be gamed

**FINDING: PASS. Fifty hostile shapes — 36 against the classifier, 14 through the two real call paths — all gate; nothing raises; every positive control releases.**

Rule at `<REPO>/tools/directive_registry.py:346-361`, constant at `:197`, header prose at `:127-146`, emitted key at `:370`.

```python
expected = expected_identity if isinstance(expected_identity, str) else ""
stamped = claim.get(ATTESTATION_IDENTITY_KEY)
if not expected.strip():
    refusals.append(...)                      # UNAVAILABLE expectation -> refuse
elif not isinstance(stamped, str) or stamped != expected:
    refusals.append(...)                      # type guard FIRST, then exact equality
```

**Hostile stamps, expectation available** (positive control releases first, then one mutation at a time): stale carried-forward digest, `None`, `""`, `"   "`, upper-case, mixed-case, leading-space, trailing-space, tab, newline, 63-char, 65-char, `int`, `float`, `True`, **list containing the right digest**, **tuple containing it**, **dict with it as value**, **dict keyed by it**, **bytes of it**, `bytearray`, `set`, `object()`, nested list, and the **entirely absent key** — **all 25 gate**, each with a condition-(6) reason, **zero raises**.

**Unavailable / hostile expectation, stamp perfect:** `None` (the default), `""`, `"   "`, `int`, `list`, `bytes`, `dict`, `object()`, `True`, `float`, and the **3-argument legacy call omitting `expected_identity` entirely** — **all 11 gate**. A missing expectation gates and never releases.

**Both call sites, by execution.** *Live v2* (`:1042-1043`): my first stub was invalid — it fed the task-verification dict where the whole record was expected, so its positive control failed on `"missing task_verifications[] (fail closed)"`. I diagnosed and corrected it rather than reporting a non-finding; with a working positive control, all **8** hostile variants gate with a condition-(6) reason. *Dormant v1* (`:1095-1096`): positive control releases; all **6** variants gate.

**The binding is meaningful, not self-referential — the load-bearing fact.** At `<REPO>/tools/project_control.py:541` `accept()` computes `identity, resolved_sha, ierr = _task_git_identity(reg_mod, t)`, **fails closed** on error at `:542-543`, and cross-checks it against the frozen report's `content_manifest_sha256` at `:552-555`; that same value flows to `task_verification_result(...)` at `:568` and into the classifier. So the stamp is compared against a **content-derived** value, not the record's own `reviewed_manifest_sha256`. That is what makes (6) a real control: refreshing a record's identity without re-stamping each row causes **every** attested row to refuse.

**Two informational notes, neither a defect nor a correction.** (a) A `str` **subclass** with a lying `__eq__` would pass both guards, but `json.load` cannot construct one, so it is unreachable through the real data path (`_load_json`, `:378-379`). (b) The refusal interpolates attacker-supplied `stamped!r` into the reasons list — the pre-existing pattern used by conditions (1) and (5), no new exposure class, output goes to the operator running `accept()`.

---

# Axis 3 — No weakening anywhere in the round-3 diff

**FINDING: PASS, proven mechanically rather than by inspection.**

**`<REPO>/tools/project_control.py` has ZERO executable change.** Parsing both revisions, stripping all docstrings, comparing ASTs:

```
project_control.py executable AST identical (docstrings stripped): True
```

All 37 changed lines are prose (module header `:67-90`; `_post_accept_verification_blockers` `:593-615`). This single result discharges several axes at once: **union behaviour provably unchanged** (C3 was prose-only, as claimed — I diffed the logic and there is none), **log redaction unchanged**, **`MATERIAL_FIELDS` consumers unchanged**, and the worse in-task F4 shortcut provably not taken.

**`<REPO>/tools/directive_registry.py` — three functions of 57 changed.**

```
functions old/new: 57 57
CHANGED or NEW: ['acceptance_ordering_deferral', '_v2_task_unresolved', '_v1_task_unresolved']
REMOVED: []
unchanged count: 54
```

**Conditions (1)-(5) untouched:**

```
classifier top-level statements  old: 21  new: 24
statements 1..19 (conditions 1-5, before the refusals guard) identical: True
added statements: 3
```

**Module constants — nothing loosened:**

```
module constants old/new: 20 21
NEW: ['ATTESTATION_IDENTITY_KEY']   CHANGED: []   REMOVED: []
```

So `ACCEPTANCE_ORDERING_ACT_CLASSES`, `LIFECYCLE_ELIGIBLE_CLASSIFICATIONS`, `DEFERRABLE_VERIFICATION_STATES`, `UNRESOLVED_VERIFICATION_STATES` and `MATERIAL_FIELDS` are provably unmoved — conditions (1), (4) and (5) cannot have been widened.

**No new attack surface.** No new imports; no `subprocess`/`eval(`/`exec(`/`__import__`/`os.system`/`shell=True`; no `os.environ`/`getenv`/new flag/`argv` (the single grep hit is docstring prose at `<REPO>/tools/project_control.py:71` asserting there is no such override, a claim the AST evidence corroborates). **No new regex** — `re.compile`/`match`/`search`/`sub` added → **0** — so **no new ReDoS surface**; condition (6) is pure string equality, linear and non-backtracking.

**Tests strengthened, not weakened.** Test functions removed: **0**. Added: `test_condition6_attestation_must_be_bound_to_the_reviewed_identity` plus class `CarriedForwardAttestationTests` (3 methods). Assertions: **29 added, 1 changed** — and the single change is `assert cases == 35` → `assert cases == 48`, a strengthening.

---

# Axis 4 — AS-8 retro-rejection

**FINDING: PASS. Condition (6) retro-rejects nothing.**

Across all **5** `verification.json` files under `<REPO>/project-control/directives/`, the count of files containing `lifecycle_classification` or `classified_at_identity` is **zero**. No live record engages the new condition.

Executing `_post_accept_verification_blockers()` read-only against the real ledger: **0 blockers**, across **53 accepted tasks**, of which **11** are accepted *and* in-regime.

Stored history is never re-evaluated — the classifier is reached only while evaluating the task currently being accepted, and accepted/canceled tasks are immutable (`.claude/rules/project-control.md` §5).

Grandfathering digests unmoved: `MATERIAL_FIELDS` (`<REPO>/tools/directive_registry.py:1559`) has its **definition untouched across the entire branch**; the 5 diff mentions are all prose describing the queued C1 follow-up.

Capture is not blocked going forward: `"additionalProperties": true` (schema `:8, :22`) already admits `classified_at_identity` with no schema change — see FU-4 for the convention consequence.

---

# Axis 5 — Containment exact

**FINDING: PASS.**

`5474b3e..dbf0a88` touches **exactly the five allowed files** in a single commit (`dbf0a88`): the producer report (+293), `directive_registry.py` (71), `project_control.py` (37), and the two test modules (181, 79) — 596 insertions, 65 deletions.

`git diff --name-only 5474b3e..dbf0a88 -- project-control/directives/ tools/validate_directive_compliance.py` → **empty**. The full branch touches 13 files; the 8 beyond the producer's five are orchestrator-authored control-plane records (gate JSONs, preserved round-1/round-2 gate reports, `state.json`, the task packet), none under `directives/`.

---

# Axis 6 — F4/F8 hold-open record, and round-2 observations not worsened

**FINDING: PASS.**

The orchestrator entry at `<REPO>/project-control/tasks/M0-T034.json` (`"at": "2026-07-31T16:55:24.148133+00:00"`) accurately reflects my round-2 corrections:

| My round-2 correction | Orchestrator record | Accurate? |
|---|---|---|
| **C1** — amend §9.9 to remove the literal username | "D3/H1 … producer must amend, one token, `<user>`-masked" | **Yes** — discharged |
| **C2** — F8 as its **own** task; forbidden paths, must not be widened into M0-T034 | "F8 … contracted as its own follow-up … **per G5 correction C2** — both targets are forbidden paths by containment design and MUST NOT be widened into M0-T034" | **Yes**, cited by name |
| **C3** — soften "no single mutable record"; consider stamping the attestation | "the union docstring's … claim will be softened by the producer in round 3"; the stamping half became the F5 rework | **Yes**, both halves |

**Round-2 observations verified not worsened.** (1) **c15 scope** — D-004's `manifest.scope.task_ids` is still `['M0-T027','M0-T028','M0-T029','M0-T033']`; M0-T034 remains absent. Unchanged, correctly deferred to FU-1. (2) **`_row_is_satisfied` wording** — `<REPO>/tools/directive_registry.py:850` (line-shifted from 757); zero diff hits; among the 54 AST-identical functions. (3) **Dead-code fail-open at `unresolved_requirements`** — `:715`; zero diff hits; likewise unchanged.

**Owner ruling C2 on AS-5 (cited, not re-litigated).** Per the task packet, the literal AS-5 clause is recorded **NOT MET and PROVEN UNMEETABLE**, the substituted material/lifecycle mechanism is **ACCEPTED in substance as a mechanism**, and the 43-field exclusion list is **explicitly NOT endorsed**, its boundary ordered tightened under the separate C1 follow-up. Binding; I apply it as written and make no independent AS-5 judgment.

---

# Axis 7 — Suites and validator, under my own execution

**FINDING: PASS.**

```
$ python tools/test_project_control.py
OK: all 22 project-control test groups passed
    ..."S11 unmet NON-lifecycle rows still block acceptance (AS-2, 48 cases incl. positive control)"

$ python tools/test_directive_compliance.py
Ran 102 tests in 66.020s
OK

$ python tools/validate_directive_compliance.py --check
REAL_EXIT=0
```

**22 groups**, **AS-2 at 48 cases**, **102 tests**, validator **exit 0** — all as expected. (My first validator attempt measured `tail`'s exit code through a pipeline; I re-ran without the pipe to obtain the process's own status.)

Condition-(6) coverage is genuinely end-to-end, not classifier-only: `<REPO>/tools/test_project_control.py:2326-2354` drives **13 real CLI `accept` invocations** in temporary repositories over stale/case-variant/padded/truncated/empty/non-string/absent stamps, each asserting `"classified_at_identity" in err`, `"not PASS" in err` and `"Traceback" not in err`, then a positive control that must accept.

## Sandbox constraints

The read-only guard blocked six command formulations (a `/tmp` redirect, and five probes whose text tripped its pattern matching, including any Python touching `os.environ`). I re-expressed each without writing files and obtained every result. **No check was skipped or routed around**, and I return BLOCKED for none of them. I did not run `tools/project_control.py`, git write commands, or `gh`.

## Not verified by me, stated plainly

- The exhaustive per-requirement pass over all D-004 requirements applicable to M0-T034 — the independent `directive-compliance-verifier`'s pass, recorded in `verification.json` (producer ≠ verifier). I verified the security-relevant behaviour of the rows this changeset implements.
- **AS-10** per-row classification of the candidate rows — the DCV's judgment under D-004-R632. I make no per-row call.
- **AS-13**'s tracked report `project-control/reports/M0-T034-lifecycle-classification.md` — assigned to the orchestrator; not assessed.
- Runtime behaviour of `accept()` / `checkpoint()` against the **live** ledger by CLI. I am read-only; I verified those paths by source reading, by executing `_post_accept_verification_blockers()` read-only against the real ledger (0 blockers), and via the S11 CLI tests which exercise them end-to-end in temporary repositories.
- That no caller of `acceptance_ordering_deferral` exists **outside** this repository. Inside it, grep confirms the two call sites plus tests are the complete set.

## Reviewer conclusion

Both returned defects are genuinely fixed, and I proved each adversarially rather than accepting the producer's account.

The redaction correction is discharged in the strongest available form. The round-3 commit removes the token and adds none — zero occurrences in all five touched files, zero in the whole producer report, zero anywhere under `tools/`, gitleaks clean over the range — and I confirmed the single removal is the flagged line itself, at old line 716 inside §9.9, rather than a collateral deletion. Critically, the failure mode that caused round 2 did not recur: the producer replaced the quoted pattern list with a description and annotated the amendment in place, fixing the shape of the mistake rather than its instance. Amending two further self-falsifying quotations beyond the one named was the right call, not scope creep.

Condition (6) is a real control and I could not game it. Fifty hostile shapes across the classifier and both genuine call paths all gate; nothing raises; every positive control releases, so the refusals are attributable to the condition under test. An absent expectation refuses rather than releases, including through the legacy three-argument call, so the function's safe default is to gate. The binding is not self-referential: the expectation is computed from git content, fails closed on error, and is cross-checked against the frozen evidence identity before reaching the classifier — which is what makes a refreshed record with stale per-row stamps refuse across the board. The carried-forward tests are correctly built as positive control, stale-refusal, and re-stamp-restores, so the refusal is pinned to the stale stamp and nothing else. Binding the dormant v1 path too was correct and should not be reverted.

The old denylist hole is closed and this suite does not certify it. Twenty-two state shapes reaching well outside `{FAIL, BLOCKED}` — `UNVERIFIABLE` above all, plus absent, null, empty-list, case and whitespace variants and non-strings — all gate, and the unhashable `state: []` that raised a `TypeError` in round 1 now returns a refusal, because the type guard was moved ahead of the membership test.

Nothing was weakened to achieve any of this, and that rests on mechanical evidence rather than reading. `project_control.py` has zero executable change — its entire 37-line diff is prose — which independently establishes that union behaviour, log redaction and the `MATERIAL_FIELDS` boundary are untouched and that the worse in-task F4 shortcut was not taken. In `directive_registry.py`, three of fifty-seven functions changed, the classifier's first nineteen statements are byte-identical, and the module gained exactly one constant with none changed or removed. No new imports, environment reads, bypass flags or regexes, so no new ReDoS surface. The round-2 fixes sit outside every round-3 hunk. The suites gained twenty-nine assertions and lost none.

The changeset retro-rejects nothing: no live record carries either key, the live ledger yields zero post-accept blockers across fifty-three accepted tasks, and the grandfathering digest list is untouched across the whole branch. Containment is exact at five files with the directives tree and validator untouched — the correct outcome, since a producer who had "fixed" F8 would have breached containment instead.

On the owner's fourth rider I rule affirmatively rather than by silence: neither F4 nor F8 blocks this gate, and both are accepted as the named four-item follow-up bundle (FU-1 through FU-4 in PART 1), to which I add the D-001 capture-convention item so future attestations are stamped at capture time. Both residuals fail in the safe direction — they gate, they do not release — and neither lowers the acceptance bar.

**G5 VERDICT: PASS.**

END OF PART 2 — end of report.
