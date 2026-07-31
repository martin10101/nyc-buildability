<!--
PRESERVATION RECORD (orchestrator, 2026-07-31)
This file preserves the complete M0-T034 G3 gate return exactly as the independent reviewer
agent `m0t034-g3` delivered it to the orchestrator via SendMessage in the prior session. That
agent has been stopped; the text below was recovered verbatim from the stored session
transcript of that delivery, not retyped from memory.
EXACTLY ONE alteration was made at preservation time: an R024 redaction (absolute machine
path -> <REPO>), applied where it occurs and annotated inline at that spot. Nothing else was
changed. Two quoted grep-pattern literals mentioning "C:/Users" later in the report are the
reviewer's own leak-measurement commands, contain no username, and are preserved verbatim.
-->

# Gate Report — M0-T034 G3 (independent)

- **Gate ID:** G3
- **Task ID:** M0-T034
- **Reviewer:** `m0t034-g3` (independent; not the producer)
- **Model actually running:** **Opus 5**, exact model id `claude-opus-5[1m]`, dispatched at explicit Opus 5 under D-004-R307. I am not Fable 5 and do not claim to be.
- **`git rev-parse HEAD`:** `1298f4b85edcc81409afbde23d570a22bbc389ff` — matches the frozen identity exactly. Branch `task/M0-T034-governance-acceptance-semantics`. Commits under review: `a965c21` (producer output), `1298f4b` (orchestrator lifecycle); base `05ee1917`.
- **Producer:** `backend-engineer` (worktree `.claude/worktrees/agent-a8497f73f558bac2a`), ported by orchestrator-only integration.

## VERDICT: **FAIL**

One blocking defect (D1) in the code that decides what gets accepted, plus one blocking hygiene defect (D2). D1 releases a row **out** of the gate set on a **schema-valid, validator-valid** verification state. This is the exact failure class the owner said to reject: a classifier one notch too permissive, silently lowering the acceptance bar for every future task.

**Correction to my own first pass:** I found this locus and rated it LOW, reasoning that the behavior is stated in the code and that `checkpoint()` still demands PASS. That was too generous — the release happens at *acceptance*, which is the bar in question, and it needs no malformed input at all. The correct severity is BLOCKING. I corroborate G5's FAIL on the same axis, and my probe found one case G5 did not report.

---

## D1 (BLOCKING) — condition (5) is denylist-shaped; a valid `UNVERIFIABLE` state releases a row out of the gate set

`tools/directive_registry.py:236`:

```python
state = verification_row.get("state")
if state in NEGATIVE_VERIFICATION_STATES:   # frozenset({"FAIL", "BLOCKED"})
    refusals.append(...)
```

Every other condition in this module is an **allowlist** (`act_class in ACCEPTANCE_ORDERING_ACT_CLASSES`, `classification in LIFECYCLE_ELIGIBLE_CLASSIFICATIONS`, `events ⊆ {"accept"}`). Condition (5) alone is a **denylist**: anything not literally `"FAIL"` or `"BLOCKED"` is treated as a non-negative finding and permits release. That is the same default-out inversion rider 1 forbids, applied to the state axis instead of the attestation axis.

I tested end-to-end through `_v2_task_unresolved` — the function `accept()` actually calls — not through the classifier helper in isolation. Fixture: one `sequencing` row bound solely to `accept`, carrying a fully well-formed independent attestation (`act_class="accept"`, `classified_by="rev"` ≠ producer `"prod"`, non-empty justification), i.e. conditions (1)–(4) all satisfied. Only `state` varies:

```
NEGATIVE_VERIFICATION_STATES   = ['BLOCKED', 'FAIL']
UNRESOLVED_VERIFICATION_STATES = ['BLOCKED', 'FAIL', 'UNVERIFIABLE', 'pending']

  state='pending'          (intended case)          accept_BLOCKED=False deferrals=1
  state='FAIL'             (guarded)                accept_BLOCKED=True  deferrals=0
  state='BLOCKED'          (guarded)                accept_BLOCKED=True  deferrals=0
  state='UNVERIFIABLE'     verifier could not verify accept_BLOCKED=False deferrals=1
  state='fail'             LOWERCASE fail           accept_BLOCKED=False deferrals=1
  state='blocked'          LOWERCASE blocked        accept_BLOCKED=False deferrals=1
  state='FAIL '            trailing space           accept_BLOCKED=False deferrals=1
  state=' FAIL'            leading space            accept_BLOCKED=False deferrals=1
  state='__MISSING__'      state key ABSENT         accept_BLOCKED=False deferrals=1
  state=None               state = null             accept_BLOCKED=False deferrals=1
  state='garbage'          arbitrary garbage        accept_BLOCKED=False deferrals=1
  state='not_applicable'   lowercase NOT_APPLICABLE accept_BLOCKED=False deferrals=1
  state=0                  integer zero             accept_BLOCKED=False deferrals=1
  state=False              boolean false            accept_BLOCKED=False deferrals=1
  state=[]                 empty list               *** UNCAUGHT TypeError ***
```

### Reachability, ruled honestly — the cases are not equal

I checked whether the schema and the untouched validator bound these.

`project-control/directives/schema/v1/directive_verification.schema.json`:
```
.properties.requirements.items.properties.state :: {"enum": ["pending","PASS","FAIL","BLOCKED","UNVERIFIABLE","NOT_APPLICABLE"]}
```
`tools/validate_directive_compliance.py:45,100,168` enforces the same set on verification rows.

- **`UNVERIFIABLE` is schema-VALID and validator-VALID.** It is reachable through a completely clean registry with green CI, no malformation anywhere. **This case is unbounded and is the blocking defect.** `UNVERIFIABLE` means the verifier could not establish satisfaction — precisely a row that must keep gating acceptance. The module's own stated rule says "A row the verifier actively failed or found blocked keeps gating"; it does not contemplate the row the verifier could not verify, and the code lets it through. Note `UNVERIFIABLE` sits inside this module's own `UNRESOLVED_VERIFICATION_STATES`, so the module simultaneously classifies the state as unresolved and treats it as clean enough to defer.
- **Lowercase / garbage / missing / null / numeric states are schema-invalid**, so a registry carrying them would be caught by `validate_directive_compliance.py` in CI. But `accept()` does **not** run the validator — it reads `verification.json` through the resolver. So these are reachable in `accept()` whenever CI has not yet run, has been skipped, or the file is edited between CI and the accept call. That is a missing defense-in-depth layer in a module whose own docstring promises it "fails closed on every malformed shape."
- **`state: []` raises an uncaught `TypeError: unhashable type: 'list'`** at `tools/directive_registry.py:236`, propagating out of `_v2_task_unresolved` → `task_verification_result` → `_directive_accept_reasons` → `accept()`. `main()` ends in `raise SystemExit(a.fn(a))` with no top-level handler, so the CLI dies on a traceback. In effect this is fail-closed (non-zero exit, `save(p, t)` never reached), but it directly falsifies the `acceptance_ordering_deferral` docstring at `tools/directive_registry.py:167`: *"Fails closed on every malformed shape and never raises."* G5 did not report this case.

### Required fix (small, and it is the same shape as the rest of the module)

Invert condition (5) to an allowlist. Only an explicitly *pending* row is eligible for deferral; every other state — including `UNVERIFIABLE`, unknown, missing, null, wrong-case, and non-string — refuses. Roughly:

```python
DEFERRABLE_VERIFICATION_STATES = frozenset({"pending"})
...
state = verification_row.get("state")
if not isinstance(state, str) or state.strip() not in DEFERRABLE_VERIFICATION_STATES:
    refusals.append(f"{rid}: verification state {state!r} is not an open 'pending' "
                    f"finding; only a pending row may be deferred (fail closed)")
```

This also removes the `TypeError` and makes the docstring true. The stated-rule block at `tools/directive_registry.py:99-101` must be amended in the same change so AS-12 continues to describe actual behavior.

**Verification note for the rework gate:** the existing AS-2 suite passes *with the defect present*. `test_s11_non_lifecycle_rows_still_block_acceptance` covers condition (5) only via `("FAIL", "BLOCKED")` at `tools/test_project_control.py:2269`. The rework must add the state-axis cases above, or the suite will keep certifying the hole.

## D2 (BLOCKING) — absolute user path committed to a PUBLIC repository

`project-control/reports/M0-T034-producer-report.md:198`:
```
$ cd <REPO>/.claude/worktrees/agent-a8497f73f558bac2a
[R024 REDACTION - orchestrator, 2026-07-31: the absolute machine path in the line above was
replaced with <REPO> at preservation time. This is the ONLY alteration to this report.]
```

I confirmed repository visibility rather than assuming it — `gh repo view --json visibility,nameWithOwner` returns `{"nameWithOwner":"martin10101/nyc-buildability","visibility":"PUBLIC"}`. G5 is correct; my working assumption from the global "private by default" convention was wrong for this repo. This leaks the OS username and home-directory layout.

Scope of the leak, measured: **exactly one occurrence.** Line 21 of the same report is already elided (`C:\...\.claude\worktrees\...`), and the rest of the diff is clean — `git diff 05ee1917 HEAD -- tools/ project-control/tasks/ | grep -c "C:/Users\|/c/Users\|C:\\Users"` returns `0`. Fix is a one-line redaction to `<REPO>/.claude/worktrees/agent-a8497f73f558bac2a`. Note the report is producer evidence: the orchestrator should have the producer amend it, not edit it in place under the report-preservation rule.

---

## RIDER 1 — sequencing allowlist: fail-closed direction verified FROM CODE. **No rejection under rider 1.**

I read `tools/directive_registry.py:152-251` rather than taking the report's word. The structure is:

```python
claim = verification_row.get(LIFECYCLE_CLASSIFICATION_KEY)
if claim is None:
    return None, []          # -> row GATES, exactly as before
...
if refusals:
    return None, refusals    # -> row GATES, loudly
return {deferral}, []        # -> released only when all five hold
```

The default is **into** the gate set. Attestation is purely **releasing**. There is no default-out-awaiting-attestation path. 23-shape probe against the frozen code:

```
sequencing@accept, NO attestation                  | GATES            | refusals=0
sequencing@accept, lc=None                         | GATES            | refusals=0
sequencing@accept, lc={}                           | GATES            | refusals=3
sequencing@accept, lc=True                         | GATES            | refusals=1
sequencing@accept, lc=string                       | GATES            | refusals=1
sequencing@accept, whitespace attestation          | GATES            | refusals=2
sequencing@accept, FULL attestation                | DEFER(released)  | refusals=0
sequencing@accept, attested BY producer            | GATES            | refusals=1
obligation@accept, FULL attestation                | DEFER(released)  | refusals=0
requirement row MISSING (None)                     | GATES            | refusals=1
row events [accept,gate]                           | GATES            | refusals=1
row events empty list                              | GATES            | refusals=1
row applicability missing                          | GATES            | refusals=1
prohibition@accept + FULL attestation              | GATES            | refusals=1
hold@accept + FULL attestation                     | GATES            | refusals=1
state=FAIL + FULL attestation                      | GATES            | refusals=1
state=BLOCKED + FULL attestation                   | GATES            | refusals=1
state=UNVERIFIABLE + FULL attestation              | DEFER(released)  | refusals=0   <-- D1
act_class case-variant Accept                      | GATES            | refusals=1
row events case-variant [Accept]                   | GATES            | refusals=1
row classification case-variant Sequencing         | GATES            | refusals=1
EMPTY producer, self-classified                    | DEFER(released)  | refusals=0   <-- O2
verification_row not a dict                        | GATES            | refusals=0
```

Ambiguous, unattested, malformed, and wrong-case rows all default into the gate set on the attestation axis. The `sequencing` KNOWN LIMIT is real but bounded three ways: release requires an independent verifier's reasoned per-row attestation; the limit is stated in code so a reviewer audits it rather than discovering it; and deferral is not waiver — `checkpoint()` still refuses until PASS. **Rider 1 passes.** D1 is a defect on a different axis, which is why it survived the rider-1 framing.

**O2 (non-blocking, pre-existing pattern):** condition (2) degrades when the record carries no producer. `producer` resolves `tv.producer → v.producer → requirements.producer`; if all three are empty, `elif producer and by == producer` never fires and a verifier could classify its own row. This mirrors the producer≠verifier check three lines above it, the schema lists `producer` as required, and the untouched validator enforces the separation (ran green). Narrow.

**Factual, explicitly NOT an AS-10 classification** — read straight from `requirements.json`: three of the eight candidate rows are **structurally ineligible** under condition (3) regardless of attestation — `D-004-R322` and `R323` bind `[progress, submit, gate, accept]`, `R388` binds `[submit, gate, accept]`. The other five bind `["accept"]` alone (`R389`/`R486`/`R488` = `obligation`; `R487`/`R501` = `sequencing`) and are mechanically eligible pending the verifier's judgment. The classifier is not a blanket release.

## RIDER 2 — AS-5 material/lifecycle boundary: **the excluded set does contain fields that carry substance.**

`MATERIAL_FIELDS` (`tools/directive_registry.py:1296-1298`) is an **inclusion** allowlist of ten keys: `objective, inputs, outputs, dependencies, allowed_paths, forbidden_paths, acceptance_scenarios, required_gates, risks, blockers`. Everything else is excluded. Scanning all 77 real packets, **43 distinct keys are excluded**; I tamper-tested every key present in M0-T034's packet and none moved the digest. Full excluded list:

`acceptance_preconditions, accepted_at, accepted_by, additional_producers, age_gate_contract, allowed_paths_note, authorizing_directive, branch, business_reason, created_at, dependency_note, directive_refs, directive_regime_entered_at, directive_regime_note, directive_regime_version, disk_budget, execution_location, gate_notes, gate_reviewer_map, gate_role_map, harness_assignments, holds_honored, milestone_id, owner_review_state, planning_only, producer_agent, producer_hint, producer_note, producer_plan, progress_log, progress_percent, reconciliation, requirement_refs, reviewer_agents, scope_amendments, scope_notes, status, stop_conditions, task_id, task_type, title, updated_at, worktree`

Against your checklist:

| Category | Covered? |
|---|---|
| paths | **yes** — `allowed_paths`, `forbidden_paths` |
| gates | **partly** — `required_gates` yes; `gate_reviewer_map`, `gate_role_map`, `gate_notes` **no** |
| scope | **no** — `task_id`, `task_type`, `milestone_id` are three of the four applicability dimensions |
| reviewers | **no** — `reviewer_agents`, `producer_agent`, `additional_producers` |
| requirements | **no** — `directive_refs`, `requirement_refs`, `directive_regime_version` |

Also excluded and substantive-looking: `acceptance_preconditions`, `stop_conditions`, `holds_honored`, `authorizing_directive`, `planning_only`, `scope_amendments`.

**Ruling on smuggling, traced through code rather than asserted:**
- **Applicability tampering (`task_id`/`task_type`/`milestone_id`) fails closed elsewhere.** Shrinking the derived set trips the `extra` non-applicable-rows check; growing it trips `missing rows`; and `applicable_requirement_ids`, when declared, must equal the derived set (`tools/directive_registry.py:764-776`). Not exploitable.
- **Regime-field stripping fails closed elsewhere** — the task drops out of regime into `_legacy_grandfather_check`, which refuses anything absent from the frozen migration manifest.
- **`reviewer_agents` / `producer_agent` are caught by nothing.** `gate()` reads the roster from the working-tree packet (`tools/project_control.py:1030-1035`), and an **uncommitted** roster widening leaves the material digest unchanged, so `_is_lifecycle_only_packet_change` classifies it as *not dirt* and the identity does not move. **This is a genuine residual gap.**

Weighed honestly: **not a regression.** Before this change the entire control-plane tree contributed nothing to either guard, so all 43 fields were already invisible; the change strictly improves the position. But the boundary was authored for D-001 amendment-3 *grandfathering* and reused unchanged for *reviewed-identity*, and for that second purpose it is drawn too narrowly. Remedy: invert its direction for the identity use — exclude a closed set of lifecycle-owned keys (`status`, `progress_percent`, `updated_at`, `progress_log`, `accepted_at/by`, `worktree`, `branch`) so unlisted fields default **into** the identity. `MATERIAL_FIELDS` is the owner's own boundary and also drives grandfathering, so this needs a follow-up task and an owner decision, not an in-scope edit (**C1**).

## RIDER 3 — explicit rulings. Green suites were not my basis; I executed both paths.

**(a) `tools/directive_registry.py:683` wrong-arity — NOT a real defect. The flag is stale. It does NOT return to the producer.**

The call passes 6 arguments; the definition at `:798` takes 6. Runtime check:
```
v1 sig: (self, d, v, directive_id, applicable, reviewed_manifest_sha256, reviewed_sha=None)
```
At the base commit the signature was 5-wide — `git show 05ee1917:tools/directive_registry.py` line 524 reads `def _v1_task_unresolved(self, d, v, directive_id, applicable, reviewed_manifest_sha256):`. Commit `a965c21` updated definition and call site together; the analyzer matched the old definition. I executed the path end to end:
```
--- v1 path, reviewed_sha MATCHING ---   reasons: []   deferrals: ['D-900-R001']
--- v1 path, reviewed_sha STALE ---      reasons: ['D-900: verification reviewed_sha is stale --
                                          recorded at commit SHA1, current reviewed commit is SHA2 (fail closed)']
--- v1 path, reviewed_sha ABSENT ---     reasons: ['... recorded at commit None ... (fail closed)']
--- legacy 4-arg call (no reviewed_sha) --- []
```
No `TypeError`, correct arity, correct fail-closed behavior, back-compatible when the sha is omitted.

**(b) `tools/project_control.py:258-264` Optional cluster — NOT a defect on a reachable path, and NOT this task's code.**

`git blame -L 255,267` attributes every line to `3e5e6e50` (M0-T014, 2026-07-17). The M0-T034 hunks in this file are at `55, 337, 359, 504, 551, 1169, 1185, 1214`; the region is untouched, its line numbers shifted only by the 32-line docstring addition. It is a type-checker narrowing false positive: callers narrow on `rerr`, not `rp`. The runtime invariant holds — every error return is `(None, None, msg)`, the sole success return is `(rel, abs_path, None)`. Verified over 18 adversarial inputs (absolute, drive-relative `C:x`, UNC, traversal, backslash-escaped, wrong subtree, empty, doubled separators):
```
INVARIANT VIOLATIONS: 0
```
All three call sites (`:485`, `:958`, `:1039`) return on `rerr` before dereferencing.

## AS-2 / AS-3 / AS-8 / AS-9 / AS-12 / AS-10

- **AS-2 — PASS as written, but the suite does not cover the D1 axis.** The 10 producer cases re-ran green and are genuinely strong (each of the five conditions broken in turn, each asserting the task stays `awaiting_gate` with no `post_accept_verification` written, plus a positive control proving the nine refusals were caused by the broken condition and not by a fixture defect). My independent 23-shape probe found no shape reaching deferral without conditions (1)–(4). The gap is condition (5)'s state axis, tested only with `("FAIL","BLOCKED")` at `tools/test_project_control.py:2269`.
- **AS-3 — PASS.** Verified independently, not just via the test: AST-parsed bodies of `_directive_accept_reasons`, `_post_accept_verification_blockers`, `_confirmed_post_accept_verifications`, `accept`, `checkpoint`, `_task_git_identity` and `acceptance_ordering_deferral` contain no ledger task id, no requirement id, and none of `getenv/environ/force/bypass/override/allowlist`. `project_control.py` never reads the environment. `accept -h` exposes exactly `{--help, --task-id, --agent}` and `checkpoint -h` exactly `{--help, --checkpoint-id, --commit, --branch, --summary}` — no new flag. Classification derives from row semantics only. Matches the `invalid_unblock_roster` standard (`tools/project_control.py:837-859`).
- **AS-8 — PASS.** Both suites green at the frozen SHA (real exit codes below), the untouched validator green against the real registry, S10's 118 assertion cases and per-block counts unchanged, and ordinary scopes byte-identical — I recomputed three myself:
  ```
  ['tools/project_control.py'] old=527534cba51d74a2 new=527534cba51d74a2 identical=True
  ['tools/']                   old=2310e245cdfab85b new=2310e245cdfab85b identical=True
  ['docs/']                    old=90a8c7a3552dedd3 new=90a8c7a3552dedd3 identical=True
  ```
- **AS-9 — PASS with two notes.** 7 files changed. `git diff --name-only 05ee1917 HEAD -- project-control/directives tools/validate_directive_compliance.py` returns **0 files**: `project-control/directives/**` is untouched and the validator is unmodified. No requirement row's `applicability` was edited (every `applicability` token in the diff is code *reading* the field). Notes: (i) `project-control/state.json` appears in the diff, written by the orchestrator's own CLI in `1298f4b` — `forbidden_paths` designates it "orchestrator lifecycle only", but `allowed_paths_note` explains only the packet, not `state.json`; (ii) D2's absolute path is inside an allowed file.
- **AS-12 — PASS on form, but the stated rule will be falsified by the D1 fix.** The rule is stated at `tools/directive_registry.py:46-126` as five conjunctive conditions with a self-disclosed KNOWN LIMIT — a reviewer audits a stated rule, not inferred behavior, which is exactly why I could locate D1 by reading it. Condition (5)'s text ("A row the verifier actively failed or found blocked...") must be amended alongside the code fix.
- **AS-10 — CONFIRMED, the producer did NOT classify the eight.** The ids `D-004-R322, R323, R388, R389, R486, R487, R488, R501` appear only as (a) raw `task_ids` data in the AS-11 table under an explicit written disclaimer ("I am not classifying any of these rows as an acceptance-ordering lifecycle act or not — that is AS-10, the independent verifier's call"), and (b) negative assertions in both suites that the ids must **not** appear in the implementation modules. No classification claim anywhere.

## Both suite runs, real exit codes

```
$ python tools/test_directive_compliance.py
  Ran 83 tests in 58.620s / OK
  exit 0   (captured via PIPESTATUS)

$ python tools/test_project_control.py
  OK: all 20 project-control test groups passed
  S10 [D-004-R413/R414]: 10/10 blocks executed, 118 assertion cases   (unchanged)
  S11 groups: AS-1/AS-4, AS-2 (10 cases), AS-5/AS-6, AS-7/AS-8, AS-3/AS-12 — all OK
  exit 0   (captured via PIPESTATUS)

$ python tools/validate_directive_compliance.py
  directive registry OK: 5 directive(s), 5 active; source hashes,
  ID append-only, and producer/verifier separation verified.
  exit 0
```

Both suites reproduce green. **Green suites are not a ruling** — D1 is invisible to them because AS-2's condition-(5) coverage stops at `("FAIL","BLOCKED")`.

## Other independently verified facts

- **The vacuous guard was real, not merely asserted.** M0-T027's pre-fix identity is literally the empty-set hash `e3b0c442…` over **0** manifest entries; post-fix it is `29a094eb…` over **5** entries.
- **Producer finding F2 confirmed true and correctly left unfixed (AS-14 honored).** M0-T027's submit record stamps `e3b0c442…`, which no longer matches. M0-T027 must be re-submitted and re-verified before acceptance.
- **AS-5 literal clause reproduced — NOT met, and the producer's disclosure is accurate.**
  ```
  keys differing between f08769e1 and 16ae4589 in project-control/tasks/M0-T027.json
      progress_percent : 90 - 85
      status : 'in_progress' - 'awaiting_gate'
      updated_at : '2026-07-30T20:24:27...' - '2026-07-31T04:40:02...'
  all differing keys are OUTSIDE MATERIAL_FIELDS: True
  new identity at f08769e1 : 29a094eb...  new identity at 16ae4589 : 29a094eb...
  LITERAL AS-5 SATISFIED (identity moves on that delta): False
  ```
  The impossibility argument is **sound** — I verified its premise in the control flow: `submit()` stamps the identity at `tools/project_control.py:498` and *then* writes `t["status"]`/`t["progress_percent"]` and `save(p, t)` at `:985-990`, so a raw-blob packet identity is stale the instant it is recorded. The substantive clause is met. Because the packet's wording is not met on its face, this needs an explicit owner ruling on the record rather than passing silently (**C2**).
- **AS-11 verified correct.** I re-read the registry rows; the producer's `task_ids` table is exact, and the answer **NO** follows — `R322`/`R323` also bind `D-004-STEP4CLOSE`, `R389` also binds `M0-T033`.
- **Port fidelity confirmed — no orchestrator edit crept into producer output.** The four `tools/` files initially hashed differently against `HEAD`; that resolves entirely to line endings (worktree CRLF, git blobs LF):
  ```
  tools/directive_registry.py          CRLF_worktree=1390 CRLF_blob=0  normalized_identical=True
  tools/project_control.py             CRLF_worktree=1350 CRLF_blob=0  normalized_identical=True
  tools/test_directive_compliance.py   CRLF_worktree=1253 CRLF_blob=0  normalized_identical=True
  tools/test_project_control.py        CRLF_worktree=2549 CRLF_blob=0  normalized_identical=True
  project-control/reports/M0-T034-producer-report.md   SHA-256 identical byte-for-byte
  ```
  TREE-IDENTICAL holds at the git-canonical level the repo's own identity functions use.
- **This change binds itself.** M0-T034's identity at `1298f4b` is `9a95fdfe…` (4 raw-blob + 2 control-plane entries); its derived applicable set is **empty (0 rows, 0 unresolved)**. But `_directive_accept_reasons` iterates every cited directive regardless (`tools/project_control.py:548-557`), so acceptance still needs a D-004 `task_verification` row for `M0-T034` with `applicable_requirement_ids: []`, verifier ≠ producer, matching `reviewed_manifest_sha256`, **and** a `reviewed_sha` matching the *merged* HEAD. Same shape as the D-001 empty-set row precedent in `0155831`.

## Required rework (blocking)

1. **D1** — invert condition (5) to an allowlist (`pending` only; non-string/unknown/missing/`UNVERIFIABLE` refuse), amend the stated rule at `tools/directive_registry.py:99-101` to match, and extend `test_s11_non_lifecycle_rows_still_block_acceptance` with the state-axis cases so the suite can no longer certify the hole. Returns to the producer.
2. **D2** — producer amends `project-control/reports/M0-T034-producer-report.md:198` to a `<REPO>`-relative path. Public repo confirmed.
3. **C1** — follow-up task + owner decision to invert the packet-field boundary for the reviewed-identity use; name the `reviewer_agents`/`producer_agent` residual gap explicitly.
4. **C2** — record an explicit owner ruling that the substituted material/lifecycle reading satisfies AS-5, with the literal clause recorded as not met and proven unmeetable.
5. **C3/C4 (operational)** — re-submit and re-verify M0-T027 at the corrected identity; stamp D-004 `task_verification` rows for both M0-T027 and M0-T034 at the **final merged HEAD**; commit every in-scope evidence file (including `project-control/reports/M0-T034-lifecycle-classification.md`) before submit/gate/accept, or those calls fail closed.

Non-blocking, for the record: O2 above; and the `state.json` note under AS-9.

## Verified independently vs. could not verify

**Independently verified:** frozen HEAD; both suite runs and the validator run with real exit codes; the classifier's fail-closed direction from source; the 23-shape and 15-state probes; the v1-path arity by `inspect.signature` and by execution; the `validate_report_arg` invariant over 18 inputs and its `git blame` provenance; the excluded-field enumeration across all 77 packets with per-field tamper tests; M0-T027's pre/post identities and the F2 mismatch; the literal AS-5 delta; AS-11's registry data; AS-3's source proofs; port fidelity by SHA-256 with newline normalization; schema and validator state-enum enforcement; repository visibility via `gh repo view`.

**Could not verify:** AS-13 (orchestrator-written from the DCV's return, not yet in the tree); the full D-004 `ALL` per-requirement pass, which is the `directive-compliance-verifier`'s lane — M0-T034's own derived applicable set is empty, and I verified `D-004-R627..R633` individually instead; and the identity values at the *merged* head, which will differ in `reviewed_sha` once this branch lands.

**Sandbox refusals and substitute routes:** three Bash calls were refused by the read-only guard — a `>` output redirect, a heredoc, and a `python -c` payload containing a `>` character in a format string. Substitute route in every case: `python -c "…"` with piped stdout and no `>` character anywhere in the payload. No check was dropped or weakened. I ran no write-producing command — no `tools/project_control.py` against the repo ledger, no git write, no `gh` write. The suites do drive the CLI, but only inside `tempfile.mkdtemp` scratch projects.

## Reviewer conclusion

The design is sound on the axis the riders anticipated: the classifier fails closed on the attestation axis, prohibitions/holds/authorizations are excluded structurally so no attestation can reach them, deferral is not waiver, the staleness and dirt guards are genuinely non-vacuous where they were provably constant, `reviewed_sha` is genuinely compared on both paths, ordinary scopes are untouched, and the producer disclosed its weakest choice and its unmet literal clause rather than claiming clean — behavior this gate should reward.

But condition (5) is denylist-shaped in a module that is allowlist-shaped everywhere else, and the consequence is that a schema-valid `UNVERIFIABLE` row — one the verifier could not verify — is released out of the gate set at acceptance. That is a permissive classifier passing, which the owner has said is the more expensive failure. The fix is small and local.

**FAIL.** Returns to the producer for D1 and D2.
