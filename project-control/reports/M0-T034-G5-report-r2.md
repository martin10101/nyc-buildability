<!--
PRESERVATION RECORD (orchestrator, 2026-07-31)
This file preserves the complete M0-T034 G5 ROUND-2 gate return exactly as the independent
reviewer agent `m0t034-g5-r2` delivered it to the orchestrator via SendMessage, in two
labelled parts ("PART 1 of 2", "PART 2 of 2"), preserved the moment they arrived. Both parts
are concatenated here in order, separated by a single blank line. NO alteration was made.
The R024 scan found nothing to redact: the reviewer deliberately never reproduced the H1
username token, referring to it only as "the literal machine username", exactly so this
report could be preserved without reintroducing the leak it reports.
-->

G5 GATE REPORT — M0-T034 — ROUND 2 — **PART 1 of 2** (part 2 contains axes 4–6, the security-surface table, owner ruling C2, round-1 defect disposition, required corrections, what I did not verify, and the reviewer conclusion with the VERDICT)

```markdown
# Gate Report

- Gate ID: M0-T034-G5 (round 2)
- Task ID: M0-T034
- Reviewer: m0t034-g5-r2 (security-reviewer role, independent; NOT the producer, and NOT the round-1 G5 reviewer)
- Model disclosure: dispatched and running as **Opus 5**, exact model id `claude-opus-5[1m]`, per D-004-R307. I am **not** Fable 5 and make no such claim.
- Producer: backend-engineer (worktree-isolated; output ported byte-identically by orchestrator-only integration)
- Result: **PASS with required corrections** (recorded as **PASS** under the gate-verdict semantics in `.claude/rules/project-control.md`; corrections C1–C3 in part 2 are BLOCKING for acceptance)
- Environment: the review worktree at the frozen SHA, read-only throughout

## Identity verification (first act)

    $ git rev-parse HEAD
    24d2d8034a753bbe89642ddf35dee13c7bb1aeb9
    $ git status --porcelain
    (empty)
    $ git log --oneline -3
    24d2d80 M0-T034: producer rework round 2 - D1, D2, F2, F3 (after two FAIL gates)
    659cdde M0-T034: merge the recorded G3/G5 FAIL gates (recorded at the reviewed commit)
    af5c083 M0-T034: preserve the G3 and G5 FAIL returns verbatim and record both gates

MATCHES the frozen SHA `24d2d8034a753bbe89642ddf35dee13c7bb1aeb9`, working tree clean. Proceeded. This is a **fresh** round-2 review: I did not inherit any round-1 finding as settled, and I re-derived every axis at this SHA.

## R024 redaction note, stated up front

This report is written for a PUBLIC repository. All paths are `<REPO>`-relative. Finding H1 in part 2 concerns a literal machine username committed in the rework; I refer to it only as "the literal machine username" and **never reproduce the string**, precisely so that preserving this report does not re-commit the token it reports. No hostnames or session identifiers appear anywhere in this report.

## Sandbox constraints and substitute routes (none omitted, none routed around)

The read-only guard refused (a) all shell file-writes, including to the scratchpad, (b) the `Write` tool entirely, (c) heredoc-piped Python, and (d) `python -c` invocations above roughly 900 characters or containing `exec(`/`setattr`/`__new__`. **Substitutes used:** every probe below was re-expressed as a short single-line `python -c` using list comprehensions and lambda fixtures, which the guard permits; long probe batteries were split into several short commands. Test execution, `git` reads and `gitleaks` were permitted directly. **No evidence gap remains** — every claim in this report rests on a command I executed or a source line I read at the frozen SHA.

---

# Axis 1 — Condition (5) must be a pending-only allowlist, refusal by DEFAULT

**FINDING: PASS. The round-1 defect F1 and G3's `state=[]` TypeError (D1) are both fixed, and I reproduced the fix adversarially rather than reading the producer's claim.**

The denylist is gone and the constant is inverted:

    $ python -c "... print(sorted(dr.DEFERRABLE_VERIFICATION_STATES), hasattr(dr,'NEGATIVE_VERIFICATION_STATES'))"
    ['pending'] False

`DEFERRABLE_VERIFICATION_STATES = frozenset({"pending"})` at `<REPO>/tools/directive_registry.py:174`, tested as `if not isinstance(state, str) or state not in DEFERRABLE_VERIFICATION_STATES:` at `<REPO>/tools/directive_registry.py:305`. The `isinstance` test comes **first**, which is what makes the unhashable case safe rather than merely lucky.

**Probe battery A — 25 hostile states directly against `acceptance_ordering_deferral`.** Every state except the literal `"pending"` must gate; none may raise.

| state | outcome | | state | outcome |
|---|---|---|---|---|
| `"pending"` (positive control) | **DEFERRED** | | `0`, `1`, `True`, `1.5` | gates |
| `"UNVERIFIABLE"` | gates | | `[]` (unhashable) | gates, **no raise** |
| key absent entirely | gates | | `{}`, `set()` | gates |
| `None` | gates | | `["pending"]`, `("pending",)` | gates |
| `"TODO"` (unknown) | gates | | `b"pending"` | gates |
| `"Pending"`, `"PENDING"` | gates | | `"fail"`, `"blocked"` (lowercase) | gates |
| `"PENDING "`, `" pending"`, `"pending "`, `"pending\t"` | gates | | `"FAIL"`, `"BLOCKED"`, `"PASS"` | gates |

**Probe battery B — the same states through `accept()`'s REAL path**, `_v2_task_unresolved` (`<REPO>/tools/directive_registry.py:914-997`), driven with a synthetic directive whose requirement row is `sequencing`/`["accept"]` and whose attestation is otherwise perfect:

    $ python -c "... dr.DirectiveRegistry._v2_task_unresolved(None, d, mkv(s), 'D-X','M0-T999', {'R1'}, 'ID1','SHA1') ..."
    [('pending','DEFERRED'), ('UNVERIFIABLE','GATES(2 reasons)'), ('@ABSENT@','GATES(2 reasons)'),
     (None,'GATES(2 reasons)'), ([],'GATES(2 reasons)'), ({},'GATES(2 reasons)'), ('TODO','GATES(2 reasons)'),
     ('Pending','GATES(2 reasons)'), ('PENDING','GATES(2 reasons)'), ('PENDING ','GATES(2 reasons)'),
     (' pending','GATES(2 reasons)'), ('pending ','GATES(2 reasons)'), (0,'GATES(2 reasons)'),
     (True,'GATES(2 reasons)'), (1.5,'GATES(2 reasons)'), ('fail','GATES(2 reasons)'),
     ('blocked','GATES(2 reasons)'), ('FAIL','GATES(2 reasons)'), ('BLOCKED','GATES(2 reasons)'),
     (['pending'],'GATES(2 reasons)'), (b'pending','GATES(2 reasons)')]

Every hostile state produces **two** accumulated reasons (the named refusal plus the ordinary not-PASS reason) — strictly louder than no attestation at all — and **`state=[]` does not raise**, which is the specific regression G3 found in round 1. The `UNVERIFIABLE` case, the single most important one (an independent verifier stating it could not verify), now keeps gating.

The stated rule and the code agree, which is what AS-12 exists to make auditable: the rewritten condition (5) text at `<REPO>/tools/directive_registry.py:105-124` states the allowlist, names `UNVERIFIABLE` explicitly as the value most dangerous to forget, and calls the `isinstance` guard "load-bearing rather than defensive decoration." I audited that stated rule against behavior and found no divergence.

The pinning test is genuine rather than tautological — `test_condition5_only_an_explicitly_pending_state_is_deferrable` (`<REPO>/tools/test_directive_compliance.py`) asserts the positive control still defers, then iterates 23 hostile values **including** `UNVERIFIABLE`, case variants, whitespace variants, non-strings and `[]`, and additionally pops the `state` key. Round 1's complaint that the test merely restated the constant is resolved.

---

# Axis 2 — F2: deferral is not waiver, enforced in code

**FINDING: PASS.** The post-accept discharge is no longer a bare `state == PASS` read. `requirement_verification_state()` is now explicitly demoted to "a PLAIN READ … NOT sufficient to discharge" (`<REPO>/tools/directive_registry.py:747-756`), and discharge routes through the new `deferred_requirement_discharge()` (`<REPO>/tools/directive_registry.py:829-902`), called from `_post_accept_verification_blockers()` at `<REPO>/tools/project_control.py:648-649`.

**Probe battery C — 15 attempts to defeat the discharge.** Fixture: a v2 record with `producer='prod-P'`, `verifier='rev-X'`, identity `ID1`, sha `SHA1`, row `R1` = `PASS`; discharge requested with `expected_identity='ID1'`, `expected_sha='SHA1'`.

| Attack | discharged | Refusal |
|---|---|---|
| honest, fully-standard record (positive control) | **True** | — |
| **forge a bare PASS**: verifier absent | False | "no independent verifier recorded" |
| **producer discharges its own deferral**: `verifier == producer` | False | "verifier … equals producer … independent verification required" |
| producer-as-verifier via **case variant** (`'Prod-P'` vs `'prod-P'`) | False | same (case/whitespace-insensitive) |
| **no producer identity anywhere** (container, doc, and `requirements` all empty) | False | "no producer identity recorded … independence cannot be established" |
| **discharge at a different content identity** (`ID2`) | False | recorded-at-identity mismatch |
| identity absent (`None`) | False | mismatch |
| **discharge at a different reviewed commit** (`SHA2`) | False | recorded-at-commit mismatch |
| reviewed_sha absent (`None`) | False | mismatch |
| **delete the row** to discharge by deletion | False | "a deferred obligation cannot be discharged by its own deletion" |
| row `FAIL` | False | not PASS |
| row still `pending` | False | not PASS |
| row `pass` (lowercase) | False | not PASS |
| `NOT_APPLICABLE` bare | False | not justified/approved |
| `NOT_APPLICABLE` + justification + approver | True | (parity with the accept-time gate) |

The four safeguards round-1 F2 said were missing — verifier independence, content identity, `reviewed_sha`, and a real state test — are all present and all reproduce. **The deferred obligation is now held to the same bar as the gate that deferred it**, which is the substantive half of D-004-R629.

**The union re-derivation.** `_post_accept_verification_blockers()` (`<REPO>/tools/project_control.py:584-673`) now builds the outstanding set from two places: the deferral records `accept()` wrote onto the packet, **and** `outstanding_lifecycle_claims()` (`<REPO>/tools/directive_registry.py:904-921`) re-derived from the registry for every accepted in-regime task. Probed directly:

    pending + lifecycle claim -> [('R1','pending')]   # surfaced from the registry alone
    PASS + claim              -> []                    # satisfied, correctly silent
    FAIL + claim              -> [('R1','FAIL')]       # surfaced
    no claim                  -> []
    unreadable record         -> [(None, "<error>")]   # caller emits a fail-closed blocker

So **deleting the packet key no longer erases the obligation** — the registry re-derivation surfaces it independently. That is the exact harm round-1 F4 named, and it is closed. See F4-R in part 2 for the residual.

**Live-ledger regression check.** `_post_accept_verification_blockers()` returns **0 blockers** against the real ledger at this SHA, so the new fail-closed coupling in `checkpoint` blocks nothing today. The producer disclosed this coupling (report §9.4: registry now loads on every checkpoint when any accepted in-regime task exists, fail-closed on registry error) rather than burying it; I confirm it is a real availability trade, correctly chosen consistently with the rest of the module, and currently inert.

---

# Axis 3 — F3 (empty producer fails closed) and F6 (case-insensitive independence)

**FINDING: PASS on both.**

**Probe battery D — 15 identity shapes against condition (2).**

| `classified_by` | `producer` | outcome |
|---|---|---|
| `'rev-X'` | `'prod-P'` | DEFERRED (positive control) |
| `'prod-P'` | `'prod-P'` | gates |
| `'Prod-P'` / `'PROD-P'` / `' prod-P '` | `'prod-P'` | **gates** (F6 fixed) |
| `'prod-p'` | `'PROD-P'` | **gates** |
| `'rev-X'` | `''` / `None` / `'   '` / `0` / `[]` | **gates** (F3 fixed) |
| `''` / `'   '` / `None` / `0` | `'prod-P'` | gates |

Round-1 probes C, D and V — the three that produced DEFERRED and should not have — now all gate. The fix is symmetric across both verification paths: the fail-closed producer reason appears in `_v2_task_unresolved` at `<REPO>/tools/directive_registry.py:937-940` and identically in `_v1_task_unresolved` at `<REPO>/tools/directive_registry.py:1007-1009`, and record-level independence uses `_identity_key()` (casefold + strip) at `:943` and `:1012`. The dormant v1 path is fixed alongside the live v2 one, which is the right call.

Confirmed with the all-sources-empty case through the discharge path:

    (False, 'PASS', ['D-X/T: no producer identity recorded on the verification record;
                     verifier independence cannot be established'])

A record that would previously have silently disabled its own independence check now refuses.
```

END OF PART 1. Part 2 follows immediately.

G5 GATE REPORT — M0-T034 — ROUND 2 — **PART 2 of 2** (continues directly from part 1)

```markdown
# Axis 4 — F4, F5, F8 status

**F4 — SUBSTANTIALLY CLOSED, with a disclosed residual (F4-R, MEDIUM, non-blocking).**

The union genuinely closes F4's stated harm: deleting `post_accept_verification` alone no longer erases the obligation, because path (b) re-derives it from `verification.json`. I verified this by probe (part 1, axis 2) and by source.

**The residual, stated precisely because the docstring overstates the guarantee.** `<REPO>/tools/project_control.py:593-598` claims the set is read "from TWO independent places … so no single mutable record can erase an obligation." Both derivations are in fact keyed off **the same mutable file**: path (a) reads the packet's `post_accept_verification`, and path (b) is reachable only through that same packet's `status == "accepted"`, `_task_in_regime()`, and non-empty `directive_refs` (`<REPO>/tools/project_control.py:619-624`). Deleting **two** keys from one packet — `post_accept_verification` and `directive_refs` — defeats both, and neither key is in `MATERIAL_FIELDS` (I enumerated it: 10 fields, `['acceptance_scenarios','allowed_paths','blockers','dependencies','forbidden_paths','inputs','objective','outputs','required_gates','risks']`), so the material digest does not move.

Partial compensating control, which I checked rather than assumed: validator check **c15** (`<REPO>/tools/validate_directive_compliance.py:431-453`) errors when an accepted task in a directive's scope stops citing that directive — catching exactly this tamper, in CI, independently of `accept()`. But c15 iterates `manifest.scope.task_ids`, and I read the live manifests: D-004's scope is `['M0-T027','M0-T028','M0-T029','M0-T033']`. **M0-T034 itself is not in it**, so c15 would not cover a tamper on this very task. Net assessment: the union is a real improvement and closes the reported hole; the "no single mutable record" claim is one notch stronger than the code delivers. Fold into the C1 follow-up.

**F5 — SUBSTANTIALLY ADDRESSED, residual disclosed and containment-justified (non-blocking).** `classified_at` is no longer copied through unvalidated. `_is_dated_attestation()` (`<REPO>/tools/directive_registry.py:181-192`) requires a well-shaped **and calendar-valid** date-and-time. Probed:

    '2026-07-31T10:00:00+00:00' True | '2026-07-31T10:00:00Z' True | '2026-07-31 10:00' True
    '2026-07-31' False (bare date) | '2026-13-99T99:99:99+00:00' False | '2026-02-30T10:00:00Z' False
    '' False | 't' False | None False | 0 False | [] False | '9999-99-99' False

Identity binding is achieved **indirectly but checkably**: `accept()` stamps `deferred_at_identity` / `deferred_at_sha` onto each deferral (`<REPO>/tools/project_control.py:569-571`), the blockers path refuses any deferral record lacking them (`:640-646`), and the discharge compares both. The attestation **object** still carries no identity stamp, so it remains transportable between records of the same task at the same identity. The producer stated this plainly (report §9.5) rather than claiming a clean fix, and correctly declined to invent a `classified_at_sha` field because the verification schema is a forbidden path. I accept the reasoning; residual for the C1 follow-up.

Security check I added: the new `ATTESTATION_TIMESTAMP_RE` is not ReDoS-exploitable — a 200,021-character adversarial input returns `False` in under 1 ms, as does a 100,000-character offset-flood.

**F8 — NOT DONE, and correctly not done. This is a containment success, not a defect of the rework.** `lifecycle_classification` is still admitted only by `"additionalProperties": true` in `<REPO>/project-control/directives/schema/v1/directive_verification.schema.json` (lines 8 and 22), and `grep -c lifecycle_classification <REPO>/tools/validate_directive_compliance.py` returns **0**. Both targets are in this task's `forbidden_paths` — the schema lives under `project-control/directives/**` (registry writes reserved to the orchestrator's D-001 capture authority), and the validator is forbidden **by design** so it stays an independent check on the code being changed. A producer that had "fixed" F8 would have breached containment and failed AS-9. The residual risk is bounded: the classifier validates every field of the attestation and fails closed on each malformed shape, so an invalid attestation can only produce a refusal, never a deferral. **F8 must be raised as its own follow-up task** (naturally folded into the C1 follow-up, which already touches this area); it cannot be discharged by this producer.

**One finding of my own, LOW, informational — the "independent approver" wording overstates the check.** `_row_is_satisfied()` (`<REPO>/tools/directive_registry.py:757-766`) accepts `NOT_APPLICABLE` on non-emptiness of `not_applicable_approved_by` alone:

    NA approved by producer: True
    NA approved by other   : True

The surrounding docstrings say "independent approver" (`<REPO>/tools/directive_registry.py:848-849`, `<REPO>/tools/project_control.py:590-591`). **This is not a lowering** — it is exact parity with the pre-existing accept-time path (`<REPO>/tools/directive_registry.py:983-986`), which likewise checks only presence, and parity is precisely what F2 demanded. Record-level independence (`verifier != producer`) still applies. Flagged only so the prose is not later mistaken for an enforced control.

---

# Axis 5 — R024 hygiene at this head

**FINDING: the round-1 F7 leak is CURED, but the rework introduced one new occurrence of the literal machine username. Graded LOW; correction C1 below.**

**gitleaks:** version 8.30.1, `gitleaks git --log-opts="a965c21..24d2d80" --no-banner` → 4 commits scanned, ~162 KB, **no leaks found**, exit 0.

**F7 cured.** The absolute `cd` transcript at producer-report line 198 is gone; `git grep` for `/c/Users` and `C:\Users` returns **nothing** in `<REPO>/project-control/reports/M0-T034-producer-report.md`. The producer amended its own evidence rather than having the orchestrator edit it, which respects the report-preservation rule.

**H1 — LOW — new occurrence introduced.** `<REPO>/project-control/reports/M0-T034-producer-report.md` line 716 (§9.9) describes the cure and, in doing so, quotes the literal machine username as one of its four sweep patterns. The sentence concludes "**no matches remain**" — a claim the sentence itself falsifies. I have not reproduced the token here. Introduced in the round-2 commit (`git diff 659cdde..24d2d80` on that file, added line 358).

Grading, with the counter-evidence stated: the token appears in **77 tracked files** at HEAD, including immutable accepted reports; it discloses a local account name only — no credential, token, path traversal or key material; gitleaks is clean. Round-1 G5 graded the identical class LOW and explicitly recommended against loading a repo-wide sweep onto M0-T034. I reach the same grading independently. It is a one-token prose redaction, not a design defect, and does not warrant a second full FAIL/rework cycle on a changeset whose security substance is now correct — but it must not be waived, hence correction C1.

**Other identifiers:** the producer report contains 8 worktree agent ids of the form `agent-<hex>`. That pattern is pre-existing and pervasive (29 tracked report files under `project-control/reports/`), discloses nothing about the machine, and I do not treat it as a defect. **Zero** `session_*` identifiers were introduced (`git diff a965c21..24d2d80 | grep -cE '^\+.*session_[0-9a-zA-Z]{10,}'` → 0). The two preserved round-1 gate reports carry only `<user>`-redacted forms and pattern strings, no literal username.

---

# Axis 6 — No new attack surface; suites and validator green

**FINDING: PASS.**

**No bypass flags, no env overrides, no task-id special-casing (AS-3).** The only `os.environ` use in either module remains `GIT_LITERAL_PATHSPECS=1` (`<REPO>/tools/directive_registry.py:1147`) — a pathspec-magic hardening, not a bypass. No `getenv`, no new CLI flag, no argparse change in the round-2 diff. Every `M0-T…` / `D-004-R…` literal in both modules is a docstring, comment, or error-message example — no requirement id or task id reaches a conditional. The round-2 diff adds **no** `subprocess`, `eval(`, `exec(`, `pickle`, `__import__`, `os.system` or `shell=True`. New imports are `datetime` and `re`, both stdlib; `StdlibOnlyTests` still passes.

**Over-breadth guard (AS-2/AS-3, rider 1's central concern) re-probed independently** with an otherwise-perfect attestation on a `pending` row:

    ('prohibition', ['accept'])         -> gates    # structurally unreachable
    ('hold',        ['accept'])         -> gates    # structurally unreachable
    ('obligation',  ['accept'])         -> DEFERRED
    ('sequencing',  ['accept'])         -> DEFERRED
    ('sequencing',  ['submit','accept'])-> gates    # the "SOLE" reading does real work
    ('sequencing',  [])                 -> gates
    ('sequencing',  ['gate'])           -> gates
    ('obligation',  ['claim','accept']) -> gates

The classifier still discriminates on the requirement row's own recorded semantics; nothing about the round-2 change widened it.

**Stored history never retro-rejected (AS-8).** No `lifecycle_classification` exists anywhere in the live registry (`grep -rl` → no files), so the new `classified_at` requirement retro-rejects nothing. All 5 active directives are `directive_verification/v2` and every one records a producer at both the document and requirements level, so the new fail-closed producer rule refuses no existing record. S7 parses 366 real ledger files. Accepted tasks are not re-evaluated.

**Containment (AS-9).** `git diff-tree` on 24d2d80 → exactly 5 files: the producer report and the four `tools/` files, all inside `allowed_paths`. `git diff --name-only main..24d2d80 -- project-control/directives/` is **empty** — no requirement row's applicability was edited, D-004-R627's prohibition holds.

**Log redaction.** `accept()` prints only `requirement_id[act_class]` per deferral (`<REPO>/tools/project_control.py:1262-1264`); justification text is never echoed.

**Suites and validator, executed by me at the frozen SHA:**

    $ python tools/test_project_control.py     -> PC_SUITE_EXIT=0, "all 22 project-control test groups passed"
        (was 20 groups; two new: "S11 deferral is not waiver -- post-accept discharge held to the
         gate's own standard (9 cases incl. positive control)" and "S11 an unknown producer identity
         fails closed (independence is never inert)"; AS-2 cases grew 10 -> 35)
        S10 [D-004-R413/R414]: 10/10 blocks, 118 assertion cases, per-block counts UNCHANGED
    $ python tools/test_directive_compliance.py -> DC_SUITE_EXIT=0, "Ran 98 tests", OK (was 83)
    $ python tools/validate_directive_compliance.py
      directive registry OK: 5 directive(s), 5 active; source hashes, ID append-only,
      and producer/verifier separation verified.                          VALIDATOR_EXIT=0
    $ python tools/validate_directive_compliance.py --check               VALIDATOR_EXIT=0

S10's unchanged 118 assertion cases and per-block counts are themselves no-regression evidence.

---

# Standard security surface

| Check | Applies | Basis |
|---|---|---|
| Privilege boundary / authority escalation | **YES — primary** | `accept()` is the acceptance authority; probed, no escalation path |
| Fail-closed on malformed input | **YES** | 76 adversarial shapes across batteries A–D; every one refuses, none raises |
| Producer/verifier separation | **YES** | condition (2) + record level + discharge level; all three now case-insensitive and fail-closed on unknown producer |
| Guard genuine vs cosmetic | **YES** | round-1 G5 quantified this against the real repo; unchanged and still green here |
| Evidence hygiene (public repo) | **YES** | F7 cured; H1 introduced (LOW) |
| Secrets / supply chain | **YES (clean)** | gitleaks exit 0; **zero** dependency manifests or lockfiles in the diff; both modules stdlib-only |
| ReDoS on new regex | **YES (clean)** | 200k-char adversarial inputs, sub-millisecond |
| Log redaction | **YES (clean)** | requirement id + act_class only |
| Cross-tenant isolation (RLS) | NO | no database, no Supabase, no tenant model touched |
| Service-role key secrecy | NO | no secrets or key material in scope |
| Private storage / bucket policy | NO | no storage layer |
| SSRF / URL fetching | NO | no network; `subprocess` invokes only local `git` with list argv, no `shell=True` |
| SQL / command injection | NO (verified) | `_run_git` list argv + `GIT_LITERAL_PATHSPECS=1` + 60s timeout, unchanged |
| Upload controls | NO | no upload path |
| Prompt-injection defenses | NO | no LLM call, no model input, no retrieved content in scope |

## Owner ruling C2 (cited, not re-litigated)

Per the binding ruling recorded in the AS-5 scenario text of `<REPO>/project-control/tasks/M0-T034.json`: the literal clause of AS-5 is **NOT MET and PROVEN UNMEETABLE**, and the substituted material/lifecycle reading is **ACCEPTED as satisfying AS-5 in substance, as a mechanism**. The ruling endorses the **field-scoped-identity approach** and explicitly does **not** endorse the 43-field boundary, which owner decision C1 queues as a separate follow-up task. I treat the approach as settled and did not re-derive it; the `MATERIAL_FIELDS` observations in F4-R above are offered as input to that queued task, not as a challenge to C2.

## Round-1 blocking defects — disposition

| Round-1 | Status at 24d2d80 | Evidence |
|---|---|---|
| **F1** (condition 5 denylist admits UNVERIFIABLE/absent/unknown/case variants) | **FIXED** | axis 1, batteries A and B |
| **D1** (G3: `state=[]` raises uncaught TypeError) | **FIXED** | `[]` gates, no raise, in both direct and real paths |
| **F2** (discharge weaker than the gate it deferred) | **FIXED** | axis 2, battery C, 15 attacks refused |
| **F3** (empty producer makes condition 2 inert) | **FIXED** | axis 3, battery D |
| **F6** (case-sensitive independence) | **FIXED** | axis 3, battery D |
| **D2/F7** (absolute user path in a public repo) | **FIXED**, but see H1 | `git grep` clean for path forms; new username token at §9.9 |
| **F4** (single mutable obligation record) | **SUBSTANTIALLY CLOSED**, residual F4-R (MEDIUM) | union re-derivation proven; both derivations still key off one packet |
| **F5** (attestation not bound to its identity) | **SUBSTANTIALLY ADDRESSED**, residual (LOW) | dating validated; discharge bound to identity + sha; object unstamped |
| **F8** (attestation outside schema/CI) | **NOT DONE — correctly**, containment-blocked | both targets are forbidden paths; must become a follow-up task |

## Required corrections — BLOCKING for acceptance (recorded as PASS-with-corrections)

1. **C1 (H1, LOW)** — have the producer amend `<REPO>/project-control/reports/M0-T034-producer-report.md` §9.9 to remove the literal machine username from the sweep-pattern list (a `<user>`-masked form suffices), so the sentence's own "no matches remain" claim becomes true. Producer evidence stays producer-amended, per the report-preservation rule.
2. **C2 (F8)** — raise the schema/validator work as its own controlled task: define `lifecycle_classification` in the v1 verification schema and mirror conditions (1), (2), (4) and (5) in `tools/validate_directive_compliance.py`, so CI checks the attestation independently of the code path it releases. It cannot be done inside M0-T034 without breaching containment.
3. **C3 (F4-R, F5 residual)** — fold into the queued C1-boundary follow-up: either give the obligation a record outside the task packet, or soften the "no single mutable record" wording at `<REPO>/tools/project_control.py:593-598` to match what the code delivers; and consider stamping the attestation with the identity it was made at.

Correction C1 is a prose redaction. C2 and C3 are new-task items that M0-T034's own containment forbids it from performing.

## Not verified by me, stated plainly

- The exhaustive per-requirement pass over all 233 D-004 requirements applicable to M0-T034. That is the independent `directive-compliance-verifier`'s pass, recorded in `verification.json` (producer ≠ verifier). I verified the security-relevant behavior of the rows this changeset implements.
- The **AS-10** per-row classification of the eight candidate rows — the DCV's judgment under D-004-R632. I made no classification call and report no per-row verdict.
- **AS-13**'s tracked report `project-control/reports/M0-T034-lifecycle-classification.md` does not exist at this SHA. Expected (the packet assigns it to the orchestrator, written from the verifier's return), but outstanding for acceptance.
- Runtime behavior of `accept()` and `checkpoint()` against the **live** ledger — I am read-only and must not run `tools/project_control.py`. I verified those paths by source reading, by executing `_post_accept_verification_blockers()` read-only against the real ledger (0 blockers), and via the S11 CLI tests, which exercise them end-to-end in temporary repositories.

## Reviewer conclusion

All three defects that failed this task in round 1 are genuinely fixed, and I proved each adversarially rather than accepting the producer's account. Condition (5) is now a pending-only allowlist in which refusal is the default: across 46 hostile state shapes — including `UNVERIFIABLE`, absent, null, unknown strings, case and whitespace variants, and non-string types — only the literal `"pending"` defers, nothing raises, and the same result holds through `accept()`'s real `_v2_task_unresolved` path rather than only against the classifier in isolation. The post-accept discharge now carries all four safeguards the accept-time gate applies, and fifteen separate attempts to defeat it — bare PASS, producer-as-verifier, case-shifted producer, unknown producer, wrong identity, wrong commit, and discharge-by-row-deletion — were each refused with a named reason. Independence is fail-closed when the producer is unknown and can no longer be defeated by re-spelling a name, in both the live v2 path and the dormant v1 one.

Two residuals deserve naming rather than burying. The union re-derivation does close the hole F4 reported — deleting the packet key no longer erases an obligation — but both derivations are still reached through the same task packet, so the code's claim that "no single mutable record can erase an obligation" is a notch stronger than what it delivers, and the validator check that would otherwise cover the gap does not list M0-T034 in its scope. F8 is untouched, and that is the right outcome: both of its targets are forbidden paths, and a producer who had fixed it would have failed containment instead. Neither residual is a mechanism that lowers the acceptance bar; both are follow-up work the owner's C1 decision has already queued.

The one new defect is a one-token hygiene slip: the paragraph documenting the removal of an absolute user path quotes the machine username as a search pattern and then declares no matches remain. The leak it was fixing is genuinely gone, gitleaks is clean, no credential is exposed, and the same token sits in 77 already-tracked files. Under the project's gate-verdict semantics that is the textbook case for PASS with a blocking correction rather than a second FAIL: the owner's standing instruction that a rejected classifier is cheaper than a permissive one bears on the classifier's design, and this changeset's classifier is now correct in exactly the direction that instruction points — unattested and ambiguous rows default **into** the gate set, and attestation only ever releases.

Containment is exact, the directives tree is untouched, no requirement row's applicability was edited, both suites pass at 22 groups and 98 tests with exit 0 under my own execution, the validator passes, and the live ledger gains zero new blockers.

**G5 VERDICT: PASS with required corrections C1–C3 (recorded as PASS; C1–C3 are BLOCKING for acceptance and for the next gate).**
```

END OF PART 2 — end of report.

**Orchestrator-facing summary (not part of the report):**
- HEAD verified `24d2d8034a753bbe89642ddf35dee13c7bb1aeb9`, clean tree. Running as **Opus 5** (`claude-opus-5[1m]`), not Fable 5.
- **Verdict: PASS with required corrections C1–C3** (record as PASS; C1–C3 blocking for acceptance).
- Round-1 blockers F1, D1, F2, F3 (and F6) are all **fixed and independently reproduced** — 76 adversarial probes across four batteries.
- F4 substantially closed with a MEDIUM residual (both derivations key off the same packet; validator c15 does not cover M0-T034 because D-004's manifest scope is `['M0-T027','M0-T028','M0-T029','M0-T033']`). F5 substantially addressed. **F8 correctly NOT done** — its two targets are forbidden paths, so it needs its own task.
- One new LOW defect (H1): the producer report §9.9 sweep sentence quotes the literal machine username; I did not reproduce the token. gitleaks clean.
- Suites green at 22 groups / 98 tests, validator exit 0, containment exact, directives tree untouched, live ledger gains 0 blockers.
