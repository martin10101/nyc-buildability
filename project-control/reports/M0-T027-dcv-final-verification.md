# M0-T027 — FINAL independent directive-compliance verification (VERBATIM verifier return)

**Orchestrator header (NOT part of the verifier's return).** Dispatched read-only at the frozen
merged head `2689b1e24ded98bf20d2d102362579789f47c17c` (main, the merge of PR #140) under the
closeout authorization D-004 amendment 17 STEP 3 (D-004-R670–R673). Agent type
`directive-compliance-verifier`, spawn name `m0t027-dcv-final`. Model value passed at spawn:
**explicit Opus 5** (D-004-R307 regime); the verifier independently discloses its actual model
below and it matches. No Fable 5 is claimed for this wave.

**VERDICT: BLOCKED.** The orchestrator records this result unaltered and did **not** accept
M0-T027 (D-004-R678: any deviation from "exactly clean" stops before accept). The R673 hard-stop
set is NOT empty: R322/R323/R388 cannot reach PASS through the completed lifecycle evidence, three
UNVERIFIABLE rows remain, and two new observations (OBS-A, OBS-B) require owner judgment. Zero
requirements are violated: 225/233 PASS, 0 FAIL, 5 attested lifecycle deferrals.

The return arrived in four parts and is reproduced below in order, verbatim (D-004-R385/R468); the
orchestrator altered nothing **except the single R024 evidence-hygiene redaction enumerated
immediately below** (public repository; owner amendments 13/14 precedent, applied at
preservation time):

| occurrences | substitution |
|---|---|
| 9 | absolute repository path (Windows user-path form) -> `<REPO>` |

All nine occurrences sit in the verifier's own closing "Files most relevant to this return" list
in Part 4, which named files by absolute path. **Nothing else changed** — no verdict, ruling,
tally, requirement id, attestation object, or observation was altered, and the BLOCKED verdict
and the R322/R323/R388 rulings stand exactly as returned.

---

# M0-T027 FINAL DIRECTIVE-COMPLIANCE VERIFICATION — D-004, delta-scoped at merged main
# PART 1 of 4 — Identity verification, derived set, method, model disclosure

## VERDICT (stated up front, detailed in Part 4): **BLOCKED** — halt and report under D-004-R673. Do not accept.

Zero requirements are violated. **225 of 233 PASS**, 5 attested lifecycle deferrals, and **3 rows (R322, R323, R388) cannot reach PASS through the completed lifecycle evidence** — which is verbatim the owner's first hard-stop clause. Two further new observations requiring owner judgment independently trigger R673's second clause.

---

## 1.1 Frozen head — verified by my own commands

```
$ git rev-parse HEAD
2689b1e24ded98bf20d2d102362579789f47c17c          <- MATCHES the required frozen head
$ git status --porcelain=v1 -b | head -1
## main...origin/main                              <- branch main, main checkout
$ git log --oneline -2
2689b1e Merge pull request #140 from martin10101/task/M0-T027-resubmit-corrected-identity
77ca816 M0-T027: re-submit under the corrected content identity (closeout Step 2, D-004-R669)
```

Working tree carries untracked/modified files only under `.claude/agent-memory/**`, `.npmrc`, and one untracked `.claude/CODEX_..._v4.3 (1).md` — none intersects M0-T027's `allowed_paths`, confirmed by the clean-identity derivation below returning no dirt error.

## 1.2 Content identity — re-derived through the canonical functions

Run through `project_control._task_git_identity` (which delegates to `directive_registry.frozen_git_identity` with `_MANIFEST_EXCLUDE_PREFIXES` and `_CONTROL_PLANE_MATERIAL_PREFIXES`) — the same single function submit, gate and accept all call:

```
LIVE (reviewed_sha=None)         -> 29a094ebdf312767b2ffa964a9cfb0398432e8838db0a211a711f1dd8db2bb97
                                    resolved sha 2689b1e24ded98bf20d2d102362579789f47c17c, error None
explicit reviewed_sha=2689b1e...  -> 29a094ebdf312767b2ffa964a9cfb0398432e8838db0a211a711f1dd8db2bb97
```

**MATCHES `29a094eb...` exactly. No drift.** Five control-plane material entries contribute (`cp_entry_count 5`), which is why the value is no longer the pre-M0-T034 empty-set hash.

Identity trajectory under the *new* rule, which I computed at each delta commit:

| commit | identity under the merged M0-T034 rule |
|---|---|
| `3ed05fda` (first-pass frozen head) | `fdbdadd4c5b33d37ffe278ee...` |
| `f301421` (G3 rework + reviews recorded) | `29a094ebdf312767b2ffa964...` |
| `16ae458`, `3b3964f`, `2689b1e` | `29a094ebdf312767b2ffa964...` |

M0-T027's reviewed content has been **byte-stable since `f301421`**. The packet's material digest is `d6afb9d70cdaac3778faed121beb0e39...` at `3ed05fda`, `f301421` **and** `2689b1e` — unchanged across the entire delta.

## 1.3 Applicable set — derived, not trusted

```
DirectiveRegistry.derive_applicable(M0-T027)  ->  233 ids, unresolved reasons: []
evaluate_task_refs                            ->  ok=True, 233 applicable, reasons []
evidence map key set (233)  vs  derived (233) ->  derived-minus-map: []   map-minus-derived: []
```

The evidence map at `project-control/reports/M0-T027-evidence-map.json` claimed 233; I derived 233 independently and the sets are **exactly equal in both directions**. Because that map file is byte-unchanged since `3ed05fda`, this also proves the applicable set did not shift across the delta — amendments 13-17 added rows `R553-R700` but **none** became applicable to M0-T027.

I also confirmed that amendment 17's own STEP 3 rows are scoped away from this task: `R669`-`R674` all carry `applicability.task_ids ["D-004-OPTIONB"]`, the non-ledger sentinel. They bind me and the orchestrator by owner instruction, **not** through `accept()` — the same structural pattern the first pass recorded as OBS-6.

## 1.4 Method

Every ruling below rests on a file, git object, control-plane record, or command output I reproduced myself. I used the producer report and evidence map **only as an index**. Under the R670 delta scope I cite the first pass's settled rulings at their verified SHA rather than re-deriving them, and I re-verified the delta exhaustively.

## 1.5 Model disclosure (D-004-R307 regime) — honest

My runtime environment block reports: **Claude Opus 5 (1M context), exact model id `claude-opus-5[1m]`**. That is the value I disclose. I am **not** Fable 5 and make no claim to be. (My generic system identity paragraph names a different tier; I am reporting the concrete runtime value, which is the one that matters for R307/R465.)

— END PART 1 of 4 —

---

# M0-T027 FINAL DIRECTIVE-COMPLIANCE VERIFICATION — PART 2 of 4
## Delta analysis, validator + harness status

## 2.1 Registry integrity, re-derived from bytes

```
$ python tools/validate_directive_compliance.py --check     -> EXIT 0
manifest version 18 | 18 audit-log entries | 18 source files | 700 requirement rows
re-derived requirements_id_digest_sha256      1884bf7966aa879b5f401044e7fcc7bedc9c06f156f560473f2906b20b51fdb0  == manifest  MATCH
re-derived requirements_content_digest_sha256 afa8b8bb4cfb753d04ef09d922e8d6ef35201c7e6086f5f380bddc0676c8d76d  == manifest  MATCH
locked_requirement_ids (700) == sorted row ids (700)   True | duplicate ids: 0
all 18 source content_digest_sha256 re-derived from on-disk bytes: 0 mismatches
```

**Append-only proven from git objects, not from the manifest's claim:** every one of `source-001` through `source-018` is touched by **exactly one commit** in the entire history. Amendments 12-17 (`source-013` through `source-018`) each satisfy this individually.

Note on `0b8c0dc`: it created `source-014` and `source-015` *with* their owner-approved redactions already applied in that same commit, so no committed source was ever edited after activation. Append-only is intact.

## 2.2 Harness outputs — run by me

```
python tools/test_directive_compliance.py   Ran 102 tests   OK    exit 0
python tools/test_project_control.py        all 22 project-control test groups passed  exit 0
    (incl. "S11 reviewed_sha comparison + no-regression (AS-7, AS-8)",
           "S11 deferral is not waiver -- post-accept discharge held to the gate's own standard (9 cases incl. positive control)",
           "S11 an unknown producer identity fails closed (independence is never inert)",
           "S11 no special-casing; classification rule stated in code (AS-3, AS-12)")
python tools/test_directive_reminder.py     Ran 12 tests    OK    exit 0
python tools/validate_directive_compliance.py --check              exit 0
```

## 2.3 What changed after each cited settled ruling

The first pass is preserved verbatim at `project-control/reports/M0-T027-dcv-verification.md` (204/233 PASS, 0 FAIL, 29 UNVERIFIABLE, at frozen identity `3ed05fda6d434670e5b610e6dad7a8b224a9aa94`). Commits since:

`f301421` (four reviews + G3 rework) -> `f4c7c3b` (amendment 12) -> `0b8c0dc` (R024 cure + amendments 13/14) -> `f08769e` (amendment 15) -> `16ae458` (submit) -> PR #135 merge `ffacee9` -> `5cd0c3e` (amendment 16) -> PR #136 merge `dc842e8` -> `e0ce313` (amendment 17) -> PR #137 merge `457ddcc` -> M0-T034 chain (`05ee191`, `a965c21`, `1298f4b`, `3c5ecc5`, `af5c083`, `659cdde`, `24d2d80`, `5474b3e`, `dbf0a88`, `3745fd2`) -> PR #138 merge `1fc8a03` -> `627affe` handoff -> PR #139 merge `3b3964f` -> `77ca816` (re-submit) -> PR #140 merge `2689b1e`.

**No settled ruling was invalidated.** I checked the four ways one could have been:

- *Reviewed content* — the producer report changed only in `f301421`, hunk header `@@ -435,3 +435,88 @@`: **85 insertions, zero deletions**, a pure append of sections 13.11 and 13.12. Sections 1-12 are byte-preserved (D-004-R132). The append is exactly the G3-required rework D-1/D-4 plus the review-outcome record. `git log 3ed05fda..HEAD -- <producer report> <packet>` lists only `f301421`, `16ae458`, `77ca816` — the latter two being CLI lifecycle writes.
- *Tool-dependent rulings* — re-verified live at this head: `invalid_unblock_roster(M0-T027)` returns `None`; `_task_in_regime` returns `True`; `material_digest` unchanged at `d6afb9d7...`; `covers_governance` `True`. So the settled R450, R453 and grandfathering-reachability rulings still hold under the changed `tools/`.
- *Registry* — append-only and both digests reproduced above; the 233-id applicable set is unchanged.
- *Reviewer-return bytes* — `0b8c0dc` modified three return files for the R024 cure. **No settled ruling rested on those bytes**: the first pass ruled R385/R468 UNVERIFIABLE, so nothing was overturned, and each file discloses its redaction inline under owner amendments 13/14 (`16 absolute repository paths -> <REPO>` in G3; `16 paths, 2 session ids, 1 bare username` in G5; `1 truncated session-id prefix` in the DCV file).

## 2.4 Protected-main workflow — verified negatively and positively

Every commit on main's first-parent line since `3ed05fda` is a merge commit:

```
2689b1e 3b3964f 77ca816  Merge pull request #140
3b3964f 1fc8a03 627affe  Merge pull request #139
1fc8a03 457ddcc 3745fd2  Merge pull request #138
457ddcc dc842e8 e0ce313  Merge pull request #137
dc842e8 ffacee9 5cd0c3e  Merge pull request #136
ffacee9 11f3540 16ae458  Merge pull request #135
```

**Zero direct pushes to main.**

PR #140: `headRefOid 77ca816daa4f25c1c31a574f52bddfeb9e2d9a33`, `mergeCommit.oid 2689b1e24ded98bf20d2d102362579789f47c17c`, state MERGED, base `main`. Full `statusCheckRollup`: **every CheckRun `conclusion SUCCESS`**, completing between `19:34:23Z` and `19:37:14Z`; `mergedAt 2026-07-31T19:40:19Z` — green strictly before merge.

## 2.5 Control-plane state (prohibited-action evidence)

- `state.json`: 53 accepted tasks; **`M0-T027` absent from `accepted_tasks`**; `last_checkpoint CP-0035`; `current_milestone M4`.
- Packet `project-control/tasks/M0-T027.json`: `status awaiting_gate`, `progress_percent 85`.
- Dependency `M0-T024`: `accepted`.
- Blockers referencing M0-T027 — `B-015` and `B-016` — both `status: resolved`; **zero open blockers**.
- Nothing merged/accepted/dispatched/deployed/installed/purchased/closed beyond the owner-authorized Step-1 and Step-2 acts.

## 2.6 Branch/worktree state at this head

`git ls-remote --heads origin` returns **29 heads**. Deleted on origin during this closeout arc: `control/M0-T034-closeout-authorization-capture`, `task/M0-T034-governance-acceptance-semantics`, `control/session-handoff-refresh-2026-07-31-close`, `task/M0-T027-resubmit-corrected-identity` — **all four were created for this closeout**. Still present on origin: `control/M0-T027-consolidated-capture` (`5cd0c3e`) and `task/M0-T027-closeout-phases-3-4` (`16ae458`). No unrelated branch was deleted.

— END PART 2 of 4 —

---

# M0-T027 FINAL DIRECTIVE-COMPLIANCE VERIFICATION — PART 3 of 4
## Per-requirement rulings for all 233 applicable ids, plus the exact deferral attestation objects

## 3.1 Settled group — 204 ids cited at verified SHA `3ed05fda6d434670e5b610e6dad7a8b224a9aa94`

The 204 ids ruled PASS by the first independent pass, preserved verbatim at `project-control/reports/M0-T027-dcv-verification.md` (Part 3 close: "Ruled: 233. Derived applicable: 233. Equal. 204 PASS / 0 FAIL / 0 BLOCKED / 29 UNVERIFIABLE / 0 NOT_APPLICABLE"). They are every applicable id **except** the 29 listed in section 3.2. Cited under D-004-R670 and re-confirmed valid at `2689b1e` by Part 2 section 2.3.

Settled owner rulings I cite and do **not** re-litigate: the **AS-5 owner ruling C2** in the scenario record; **R578** standing as a recorded erratum by owner decision (submit commit `16ae458` message, amendment 16); the **R090** Step-1 model-tier deviation and its owner disposition; and the **AS-6** remediation-arc semantics (owner amendment 11).

## 3.2 Delta rows — the 29 previously-UNVERIFIABLE ids, ruled individually at `29a094eb...` / `2689b1e...`

Deferral eligibility was computed from code, per row, by running the real `directive_registry.acceptance_ordering_deferral` function against a well-formed attestation for each candidate. The eligibility rule is conditions (3)+(4): `classification` in {obligation, sequencing} AND `applicability.lifecycle_events` a subset of {`accept`}.

| id | ruling | primary evidence I reproduced |
|---|---|---|
| R319 | **PASS** | `gates/M0-T027-G2.json`, `-G3.json`, `-G5.json` each carry `reviewed_sha 3ed05fda6d434670e5b610e6dad7a8b224a9aa94`; the first-pass DCV header (line 4) names the same SHA. Gate wave + independent directive verification at ONE frozen identity. G0 is administrative/historical (`da0d42b6`). |
| R320 | **PASS** | All four returns self-disclose their model: `M0-T027-G3-report.md:39` "Opus 5, read-only"; `-G5-report.md:45` `claude-opus-5[1m]`; `-control-plane-verification.md:19` `claude-opus-5[1m]`; `-dcv-verification.md:555` "I ran as Opus 5, `claude-opus-5[1m]`". Independent of the producer's dispatch ledger. |
| **R322** | **CANNOT PASS** | See section 3.3. |
| **R323** | **CANNOT PASS** | See section 3.3. |
| R384 | **PASS** | Same four self-disclosures, plus `gates/M0-T027-G3.json` `reviewer code-reviewer` and `-G5.json` `reviewer security-reviewer`. |
| R385 | **PASS** | Four tracked verbatim returns exist; each header discloses its R024 redaction rather than concealing it, and the redaction changed no verdict, finding, SHA, digest or count. |
| R386 | **PASS** | A completed independent directive verification exists as a tracked file at HEAD (`M0-T027-dcv-verification.md`, 560 lines, verifier != producer). The obligation is to *run* it, not that it pass. |
| R387 | **PASS** | Commit `f301421` "STOPPED on BLOCKED verification"; packet `progress_log` 90% entry; M0-T027 was not submitted/merged/accepted at that point. |
| **R388** | **CANNOT PASS** | See section 3.3. |
| R389 | **ATTESTED LIFECYCLE DEFERRAL** | `obligation` + `lifecycle_events ['accept']`; function returns DEFERRAL_GRANTED. |
| R461 | **PASS** | `gates/M0-T027-G3.json`: `reviewer code-reviewer`, `role independent_review`, `result PASS`. |
| R462 | **PASS** | `gates/M0-T027-G5.json`: `reviewer security-reviewer`, `role independent_review`, `result PASS`. |
| R463 | **PASS** | `M0-T027-control-plane-verification.md:13` — agent type `control-plane-verifier`, read-only, producer under review `orchestrator`, "Reviewer != producer: CONFIRMED". |
| R465 | **PASS** | As R320 — all four disclosed independently, all matching the value passed at spawn. |
| R467 | **PASS** | Each return documents its own primary-evidence re-derivation: G3 re-derives a blob SHA-256 and reads `MATERIAL_FIELDS` at named source lines; G5 shows its own command transcripts; the control-plane return states every claim was re-derived from primary artifacts; the DCV return carries an explicit independence statement (its section 12). |
| R468 | **PASS** | As R385. |
| R474 | **PASS** | Four PASS records. Lawfulness checked against `tools/project_control.py:162-163` — `ADMINISTRATIVE_GATES {G0,G7}`, `INDEPENDENT_GATES {G1,G3,G4,G5,G6}`. G0 administrative; G2 not independent-class; G3/G5 `role independent_review` with reviewer != producer `orchestrator`. |
| R475 | **PASS** | The *confirmation act* is performed by this pass: 233 derived == 233 rows in my block == 233 evidence-map keys, verified in both set directions. Stated dependency in Part 4 section 4.5. |
| R479 | **PASS** | The recorded stop at `f301421`; amendment 16 (`5cd0c3e`) cures it. |
| R481 | **PASS** | `project-control/reports/M0-T027.json` — `submitted_at 2026-07-31T19:32:55.139129+00:00`, `requested_status awaiting_gate`, written by the CLI in commit `77ca816`. |
| R482 | **PASS** | PR #140, `baseRefName main`, state MERGED (and PR #135 before it). |
| R483 | **PASS** | `gh pr view 140 --json statusCheckRollup` — every CheckRun `conclusion SUCCESS` at `headRefOid 77ca816`, the exact PR head. |
| R484 | **PASS** | Checks completed `19:34:23Z`-`19:37:14Z`; `mergedAt 19:40:19Z`. Merge strictly after green. (Deferral-eligible, but it already PASSES, so no deferral is claimed.) |
| R485 | **PASS** | This pass performed it: identity `29a094eb...` re-derived at merged main `2689b1e`, and the 233-id applicable set re-derived through the resolver. |
| R486 | **ATTESTED LIFECYCLE DEFERRAL** | `obligation` + `['accept']`; DEFERRAL_GRANTED. |
| R487 | **ATTESTED LIFECYCLE DEFERRAL** | `sequencing` + `['accept']`; DEFERRAL_GRANTED. |
| R488 | **ATTESTED LIFECYCLE DEFERRAL** | `obligation` + `['accept']`; DEFERRAL_GRANTED. |
| R501 | **ATTESTED LIFECYCLE DEFERRAL** | `sequencing` + `['accept']`; DEFERRAL_GRANTED. |
| R515 | **PASS** | The row's named subject is *the evidence map*. `M0-T027-evidence-map.json` holds 233 keys with `derivation.carried_forward_from_previous_map 128`, `newly_covered 105`, `previous_map_ids_no_longer_applicable []`. The old count is **not** preserved anywhere in it. The 97 figure the first pass flagged lives in `verification.json`, which is R475's subject, not R515's. |

Rows the function **refused** a deferral for, quoting its own reason text:
- R322/R323: `lifecycle_events ['accept','gate','progress','submit'] bind obligations outside acceptance ordering (gate, progress, submit), so this row's unmet obligations are not SOLELY acceptance-ordering acts`
- R388: same refusal for `['accept','gate','submit']`
- R483/R485: `requirement classification 'evidence' cannot describe an acceptance-ordering ACT`
- R319: `'harness'` classification **and** events outside; R320: events outside

## 3.3 The three rows that cannot reach PASS — D-004-R673 clause 1

This is my call, made on the row texts and the completed evidence, not on the expectation.

**D-004-R322** — *"Closeout step 6: only if everything passes - submit, use the protected-main PR workflow, verify CI, merge, **accept M0-T027 through project control**, and create a checkpoint ONLY if the established policy requires one."*
Submit satisfied (`77ca816`), protected-main PR satisfied (#140), CI verified satisfied (all SUCCESS at `77ca816`), merge satisfied (`2689b1e`). **The accept clause has not occurred** — packet status is `awaiting_gate` and `M0-T027` is absent from `state.json.accepted_tasks`. The checkpoint clause is conditional and not yet due. Not deferral-eligible. **Ruling: UNVERIFIABLE on the accept clause; cannot PASS at this identity.**

**D-004-R388** — *"PHASE 4 step 8: if every gate passes - submit, merge through protected main, verify the merged identity, **accept M0-T027 through the CLI**, and checkpoint ONLY if policy requires it."*
Submit satisfied, merge through protected main satisfied, merged identity verified satisfied (this pass). **The accept clause has not occurred.** Not deferral-eligible. **Ruling: UNVERIFIABLE on the accept clause; cannot PASS at this identity.**

**D-004-R323** — *"Closeout step 7: clean ONLY branches/worktrees created for this closeout."*
The **restriction** is honored with zero violations: four branches were deleted on origin and all four were created for this closeout; 29 remote heads remain and no unrelated branch was deleted. But the **cleaning act is incomplete** — `control/M0-T027-consolidated-capture` and `task/M0-T027-closeout-phases-3-4` are still on origin, with their cleanup scheduled post-accept by STEP 4 / R488. Not deferral-eligible. **Ruling: partially discharged; cannot PASS at this identity.**

**Root cause, stated as a finding rather than an obstacle.** R322, R323 and R388 are **compound** rows: each states a whole submit-to-accept sequence in one requirement, so its `applicability.lifecycle_events` necessarily spans `progress`/`submit`/`gate` as well as `accept`. Condition (3) of the merged M0-T034 mechanism refuses to defer any row whose unmet obligations are "not SOLELY acceptance-ordering acts" — correct policy for a genuine mixed row, but for a compound row whose non-accept clauses are *already satisfied* it produces a permanent gate that no attestation can lift. Amendment 9 later decomposed the same sequence into atomic rows R481-R488, and those decomposed rows behave correctly (R481-R485 PASS on completed evidence; R486/R487/R488 defer cleanly). The compound predecessors did not get the same treatment. **This needs an owner decision; I will not paper over it, and I do not recommend any workaround.**

For the record: M0-T034's own AS-10 asks the independent verifier to classify each of the eight candidate rows "per row, with reasons", explicitly forbidding producer pre-classification. My split — R389/R486/R487/R488/R501 eligible, R322/R323/R388 not — is the honest execution of that instruction, and it is the mechanism behaving exactly as written, **not** a defect in the M0-T034 code.

## 3.4 Exact attestation objects for the 5 deferrals

Machine-consumable, matching the shape `acceptance_ordering_deferral` consumes. Each belongs inside its verification row under key `lifecycle_classification`; each row's `state` must be exactly `"pending"`.

```json
{ "id": "D-004-R389", "state": "pending",
  "lifecycle_classification": {
    "act_class": "post_accept_cleanup",
    "classified_by": "directive-compliance-verifier",
    "classified_at": "2026-07-31T21:15:00+00:00",
    "classified_at_identity": "29a094ebdf312767b2ffa964a9cfb0398432e8838db0a211a711f1dd8db2bb97",
    "justification": "Cleaning the branches/worktrees created for the two authorized tasks is an act that can only be performed after acceptance; the row is bound solely to the accept lifecycle event and is an obligation, not a bar on acceptance." } }

{ "id": "D-004-R486", "state": "pending",
  "lifecycle_classification": {
    "act_class": "accept",
    "classified_by": "directive-compliance-verifier",
    "classified_at": "2026-07-31T21:15:00+00:00",
    "classified_at_identity": "29a094ebdf312767b2ffa964a9cfb0398432e8838db0a211a711f1dd8db2bb97",
    "justification": "Accepting M0-T027 through the CLI is the acceptance act itself; its evidence cannot exist before accept() runs. Bound solely to accept, classified obligation." } }

{ "id": "D-004-R487", "state": "pending",
  "lifecycle_classification": {
    "act_class": "checkpoint",
    "classified_by": "directive-compliance-verifier",
    "classified_at": "2026-07-31T21:15:00+00:00",
    "classified_at_identity": "29a094ebdf312767b2ffa964a9cfb0398432e8838db0a211a711f1dd8db2bb97",
    "justification": "Creating a checkpoint only if policy requires one is a conditional post-accept act; checkpoint() is the first post-accept opportunity at which it can be evaluated. Bound solely to accept, classified sequencing." } }

{ "id": "D-004-R488", "state": "pending",
  "lifecycle_classification": {
    "act_class": "post_accept_cleanup",
    "classified_by": "directive-compliance-verifier",
    "classified_at": "2026-07-31T21:15:00+00:00",
    "classified_at_identity": "29a094ebdf312767b2ffa964a9cfb0398432e8838db0a211a711f1dd8db2bb97",
    "justification": "Cleaning only the M0-T027 closeout branches/worktrees follows acceptance; two closeout branches remain on origin by design pending that act. Bound solely to accept, classified obligation." } }

{ "id": "D-004-R501", "state": "pending",
  "lifecycle_classification": {
    "act_class": "stop_after",
    "classified_by": "directive-compliance-verifier",
    "classified_at": "2026-07-31T21:15:00+00:00",
    "classified_at_identity": "29a094ebdf312767b2ffa964a9cfb0398432e8838db0a211a711f1dd8db2bb97",
    "justification": "Stopping after M0-T027 is either accepted or genuinely blocked is by construction an act at or after the acceptance decision. Bound solely to accept, classified sequencing." } }
```

Each satisfies all six conditions at this identity: enumerated `act_class`; `classified_by` != producer `orchestrator`; dated ISO-8601 instant; reasoned; row classification and `lifecycle_events` eligible; `state` exactly `pending`; and `classified_at_identity` **exactly** `29a094eb...`.

**These attestations are emitted for completeness of the matrix. Because the verdict is BLOCKED, none of them should be written to `verification.json` yet** — see Part 4 section 4.6.

— END PART 3 of 4 —

---

# M0-T027 FINAL DIRECTIVE-COMPLIANCE VERIFICATION — PART 4 of 4
## verification.json entry, R672 guard record, R024 ruling, findings, FINAL VERDICT

## 4.1 The `verification.json` `task_verifications` entry

Schema `directive_verification/v2`, matching the field shape of the existing M0-T033 entry.

**Record-level object:**

```json
{
  "task_id": "M0-T027",
  "directive_id": "D-004",
  "producer": "orchestrator",
  "verifier": "directive-compliance-verifier",
  "reviewed_sha": "2689b1e24ded98bf20d2d102362579789f47c17c",
  "reviewed_manifest_sha256": "29a094ebdf312767b2ffa964a9cfb0398432e8838db0a211a711f1dd8db2bb97",
  "state": "BLOCKED",
  "note": "<the full text of this four-part return>",
  "applicable_requirement_ids": [ ...the 233 derived ids... ],
  "requirements": [ ...233 rows... ]
}
```

**`reviewed_sha` must be `2689b1e2...`, not `3b3964f3...`.** The submit record `project-control/reports/M0-T027.json` stamps `reviewed_sha 3b3964f354088353f6f8a261700c94bdb1295bb0` (HEAD when submit ran). `accept()` compares only the *report record's* `content_manifest_sha256` against the live identity (it matches, `29a094eb...`), but it passes the freshly resolved HEAD into `task_verification_result`, and `_v2_task_unresolved` compares that against the **verification record's** `reviewed_sha`. A verification entry stamped `3b3964f` would fail closed.

**Row template** (identical to the M0-T033 rows):

```json
{ "id": "<D-004-Rnnn>", "state": "PASS",
  "evidence": ["<the file/field/record cited for that id in Part 3>"],
  "verified_at": "2026-07-31T21:15:00+00:00",
  "verified_by": "directive-compliance-verifier",
  "reviewed_sha": "2689b1e24ded98bf20d2d102362579789f47c17c" }
```

**Row states, exhaustively:**
- `PASS` — the 204 settled ids of section 3.1 (evidence: `project-control/reports/M0-T027-dcv-verification.md` at `3ed05fda...`, cited under D-004-R670) plus the 21 delta ids `R319, R320, R384, R385, R386, R387, R461, R462, R463, R465, R467, R468, R474, R475, R479, R481, R482, R483, R484, R485, R515` with the evidence given in section 3.2. **225 rows.**
- `pending` **plus** `lifecycle_classification` exactly as in section 3.4 — `R389, R486, R487, R488, R501`. **5 rows.**
- `UNVERIFIABLE` — `R322, R323, R388`. **3 rows.** These are not deferrable and will keep gating acceptance, which is the correct fail-closed behavior.

## 4.2 Guards I performed manually (D-004-R672)

From reading `accept()` at this head (`tools/project_control.py:1180-1280`), these checks **are** mechanically executed for this packet's shape (governance, orchestrator producer, in-regime) and I confirmed each independently: orchestrator-only caller; `status == awaiting_gate` OK; required gates PASS with independence OK; dependency `M0-T024` accepted OK; no open blocker references the task OK (B-015, B-016 both `resolved`); in-regime directive refs, identity freshness and per-task verification OK.

These are **skipped or absent from the accept path** — I performed each by hand and record the result:

1. **Gate-record identity binding.** `accept()` never compares a gate record's `content_manifest_sha256`/`reviewed_sha` to the current identity. G3 and G5 are stamped at `e3b0c442...`/`3ed05fda`; current is `29a094eb...`/`2689b1e`. **Performed:** the reviewed-content delta between the gate identity and the accept identity is exactly the 85-line pure append to the producer report (`@@ -435,3 +435,88 @@`, zero deletions) — the very rework the G3 gate itself demanded (D-1/D-4) plus the review-outcome record — together with lifecycle-only packet fields. Packet material digest unchanged (`d6afb9d7...`). **Result: no unreviewed substantive change.**
2. **Evidence-map freshness at accept.** Checked only at submit; `accept()` never re-reads it. **Performed:** key set == derived set exactly, both directions. **Result: pass, but** the map's own `reviewed_sha`/`content_manifest_sha256` fields still read `3ed05fda`/`e3b0c442`, stale relative to the re-submit (OBS-B).
3. **Governance-directive coverage.** Checked at claim, not accept. **Performed:** `covers_governance(M0-T027)` returns `True`.
4. **Unblock-roster guard.** Runs only at unblock. **Performed:** `invalid_unblock_roster(M0-T027)` returns `None` at this head.
5. **Regime membership.** **Performed:** `_task_in_regime` returns `True`, so the legacy-grandfathering branch is unreachable and `material_digest` has no acceptance consequence.
6. **Containment / AS-9 vs R477.** No mechanical check exists. **Performed:** `0b8c0dc` touched `project-control/directives/**` and three reviewer-return report files; `16ae458` and `77ca816` each touched `reports/M0-T027.json`, `state.json`, `tasks/M0-T027.json`. Only `tasks/M0-T027.json` is in `allowed_paths`; the rest are CLI lifecycle artifacts and the orchestrator's D-001 capture authority. **Result:** this is the **already-settled** AS-9/R477 wording gap (G3 defect D-4, control-plane O-1, first-pass OBS-2), disclosed in producer-report section 13.11 and left to a follow-up by owner ruling. Not a new finding; I do not re-litigate it.
7. **Protected-main workflow / no direct push.** No mechanical check. **Performed:** first-parent analysis — all six commits on main since `3ed05fda` are PR merge commits. **Result: pass.**
8. **CI green at the exact PR head.** No mechanical check. **Performed:** full `statusCheckRollup` for PR #140, every check SUCCESS at `77ca816`, all completing before the merge timestamp. **Result: pass.**
9. **Producer != verifier, in substance.** The code compares identity strings only. **Performed:** I produced none of the changes I reviewed; I authored no commit, report, packet field, or gate record in this delta. **Result: pass.**
10. **R024 evidence hygiene.** No mechanical check anywhere. **Performed:** section 4.3.

## 4.3 R024 ruling — mine, not the orchestrator's (D-004-R674)

**D-004-R024: PASS for the delta.**

I scanned every added line across all 34 delta files under `project-control/`, `docs/` and `tools/` between `3ed05fda` and `2689b1e`:

| pattern class | added-line hits |
|---|---|
| machine username token | 0 |
| absolute Windows user path (both slash forms) | 1 — **not a leak** |
| session id | 0 |
| `claude.ai/code/session` URL in file content | 0 |
| pane-id markers | 0 |
| home-directory layout fragment | 3 — **not leaks** |
| hostname markers | 1 — **not a leak** |

Every non-zero hit is a **grep pattern string quoted inside a reviewer's own hygiene-scan command, or a redaction description**, located in `M0-T034-G3-report.md:107`, `M0-T034-G3-report-r2.md:91-95`, and `M0-T027-G5-report.md:200-205`. No literal username, session id, pane id, absolute user path, or hostname is disclosed. Where a reviewer needed to name the offending token it appears as a placeholder, not the value. I describe these patterns rather than quoting matched values.

The **D3 redaction** ordered by amendment 17 item 6 is confirmed cured: zero literal username matches on added lines anywhere in the delta, including tracked `tools/`.

Excluded from scope as instructed and by standing precedent: the `Claude-Session` commit trailer (standing precedent throughout main's history, with the recorded owner consistency ruling in the first pass's header), and the 76 pre-existing username-bearing files that R560 prohibits touching.

## 4.4 Findings and observations requiring owner judgment (R673 clause 2)

- **F-1 (blocking, new).** Compound rows R322, R323 and R388 cannot reach PASS and cannot be deferred — section 3.3. Their non-accept clauses are fully discharged; only the accept/post-accept clause remains, and condition (3) structurally refuses it. Owner decision required.
- **OBS-A (new).** **M0-T034's own task is `status: self_check`** with no submit record (`project-control/reports/M0-T034.json` does not exist) and it is absent from `accepted_tasks`, yet its code — including deferral condition (6), on which M0-T027's acceptance depends — is merged and live on main via PR #138. Owner STEP 1 ordered the merge and did not order acceptance, so this may be intended; I record it because M0-T027 would be accepted on the strength of a mechanism whose own task lifecycle is incomplete.
- **OBS-B (new, minor).** The evidence map's internal `reviewed_sha`/`content_manifest_sha256` fields (`3ed05fda`/`e3b0c442`) disagree with the submit record's (`3b3964f`/`29a094eb`). `accept()` never reads the map's fields, so there is no mechanical inconsistency, but two tracked artifacts describing the same submission disagree.
- **OBS-C (informational).** The local remote-tracking ref `remotes/origin/task/M0-T027-resubmit-corrected-identity` is stale — the branch is deleted on origin (absent from `git ls-remote --heads`, 29 heads total). Cosmetic; a prune clears it.
- **OBS-D (informational).** `readonly_agent_guard.py` over-denied three of my purely read-only commands, tripping on `->` and `#` inside Python/sed string literals. Over-denial, not under-denial — containment is not weakened, and every check was completed by a substitute read-only route. This reproduces the first pass's OBS-4 at a higher rate; `.claude/hooks/**` is outside this task's scope, so it belongs in the same follow-up.

## 4.5 Stated dependency on R475

I ruled R475 PASS on the **confirmation act**, which I performed. The **recorded** artifact still lags: `verification.json`'s M0-T027 block holds **97 rows** at this head against 233 derived, with `reviewed_sha: null` and `reviewed_manifest_sha256: null`. That gap closes only when the orchestrator transcribes this block. I state the dependency openly rather than hiding it, and note it is mechanically backstopped: `_v2_task_unresolved` fails closed independently on declared-set inequality, missing rows, non-PASS state, content-identity staleness **and** `reviewed_sha` staleness.

## 4.6 FINAL VERDICT and tallies

**Tally over all 233 applicable ids:**

- **225 PASS** (204 settled at `3ed05fda...` + 21 delta rows verified at `29a094eb...`/`2689b1e...`)
- **0 FAIL** — zero requirements are violated
- **3 UNVERIFIABLE** — R322, R323, R388
- **5 attested lifecycle deferrals** — R389, R486, R487, R488, R501
- **0 NOT_APPLICABLE**
- **0 BLOCKED-by-defect**

225 + 3 + 5 = 233 = the derived applicable set. I ruled every id individually; **no id was covered by sampling**.

**R673 hard-stop set: NOT empty.** R322, R323 and R388 cannot reach PASS through the completed lifecycle evidence, and three UNVERIFIABLE rows remain. Two new observations (OBS-A, OBS-B) independently require owner judgment. Three of the four hard-stop clauses fire.

**R674 "exactly clean" condition: NOT met.** Acceptance of M0-T027 is **not** authorized. STEP 4 must not execute. Because the verdict is BLOCKED, the 233-row block should **not** be written to `verification.json` as if clean; if it is recorded at all it must carry `state: BLOCKED` with R322/R323/R388 as `UNVERIFIABLE`, which `accept()` will correctly refuse.

**VERDICT: BLOCKED** — meaning *not yet certifiable*, not *defective*. Nothing is violated; the closeout evidence is complete, the merged identity is correct and stable, CI was green before every merge, no direct push touched main, evidence hygiene is clean, and 225 of 233 rows PASS on evidence I reproduced myself. What blocks acceptance is a structural gap in how three compound amendment-8/9 rows interact with the merged M0-T034 deferral mechanism. That is the owner's call to make, and I halt and report rather than proceed.

---

**Independence statement.** I am not the producer of any change I reviewed. I ruled no requirement using the producer's compliance matrix, evidence map, self-assessment, or summary as proof — the evidence map served only as an index, and every ruling was re-derived from the source file, git object, deterministic test, control-plane record, or GitHub API response I have named. Where the producer's analysis was correct I say so because I reproduced it. My model was **Opus 5, `claude-opus-5[1m]`**; record that, and record nothing about Fable 5 for this wave.

**Files most relevant to this return (paths redacted at preservation time per R024, annotation in the orchestrator header):**
- `<REPO>\project-control\tasks\M0-T027.json`
- `<REPO>\project-control\reports\M0-T027.json`
- `<REPO>\project-control\reports\M0-T027-dcv-verification.md`
- `<REPO>\project-control\reports\M0-T027-evidence-map.json`
- `<REPO>\project-control\directives\D-004-agent-teams-runtime-adoption\requirements.json`
- `<REPO>\project-control\directives\D-004-agent-teams-runtime-adoption\verification.json`
- `<REPO>\project-control\directives\D-004-agent-teams-runtime-adoption\source-018-amendment.md`
- `<REPO>\tools\directive_registry.py`
- `<REPO>\tools\project_control.py`

— END PART 4 of 4 — RETURN COMPLETE —
