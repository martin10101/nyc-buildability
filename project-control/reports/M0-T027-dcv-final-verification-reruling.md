# M0-T027 — delta re-ruling under owner Decision 1 (VERBATIM verifier return)

**Orchestrator header (NOT part of the verifier's return).** Continuation of the same
independent verifier (`m0t027-dcv-final`, agent type `directive-compliance-verifier`, explicit
Opus 5, read-only), resumed with its full prior context after owner amendment 18
(`source-019-amendment.md`, rows D-004-R701–R717, merged as PR #143) captured the owner's
Decision 1: the accept-stage clauses of exactly R322/R323/R388 ruled DISCHARGED-BY-DECOMPOSITION
(D-004-R706, scoped by R707, sequenced by R708). Scope of this pass per D-004-R713: re-rule ONLY
those three rows at head `bbbb8ef18cc297ece8759535f0cb9484a0d785bc`; every other ruling of the
four-part return (preserved at `project-control/reports/M0-T027-dcv-final-verification.md`)
is settled and cited.

**VERDICT: PASS — R673 hard-stop set EMPTY, R674 "exactly clean" MET.** Final tally
228 PASS · 0 FAIL · 0 UNVERIFIABLE · 5 attested lifecycle deferrals · 0 NOT_APPLICABLE = 233.
The orchestrator preserves this return verbatim; **no redaction was required** (scanned before
commit: no username, absolute user path, session id, pane id, or hostname in the text).

---

# M0-T027 — DELTA RE-RULING UNDER OWNER DECISION 1 (D-004-R706)
## Independent directive-compliance verification, resumed at head `bbbb8ef` per D-004-R713

## VERDICT: **PASS** — the R673 hard-stop set is now EMPTY and R674 "exactly clean" is MET.

---

# A. Identity verification at `bbbb8ef` and applicable-set confirmation

## A.1 Frozen head — my own commands

```
$ git rev-parse HEAD
bbbb8ef18cc297ece8759535f0cb9484a0d785bc          <- MATCHES the required head
$ git log --first-parent --format="%h %p %s" 2689b1e..HEAD
bbbb8ef 1f6aaa6 bc486c9  Merge pull request #143 from martin10101/control/D-004-amendment-18-capture
1f6aaa6 ebb52e1 9790f8e  Merge pull request #141 from martin10101/control/track-closeout-artifacts
ebb52e1 2689b1e f3c3add  Merge pull request #142 from martin10101/control/M0-T027-final-verification-stop
```

All three commits added to main since my Part 4 are PR merge commits. **Zero direct pushes to main**, sustained.

## A.2 Content identity — re-derived, unchanged

```
project_control._task_git_identity(M0-T027)
  -> 29a094ebdf312767b2ffa964a9cfb0398432e8838db0a211a711f1dd8db2bb97
  -> resolved sha bbbb8ef18cc297ece8759535f0cb9484a0d785bc, error None
```

**Identity `29a094eb…` is STILL the derived identity at `bbbb8ef`.** Confirmed why: the packet's material digest is `d6afb9d70cdaac3778faed121beb0e39…` at both `2689b1e` and `bbbb8ef` — the only packet change is one added `progress_log` entry (8 → 9), which is lifecycle-only and does not move the material identity. Status remains `awaiting_gate`, 85%. Gate records are byte-unchanged (`git diff --name-only 2689b1e..HEAD -- project-control/gates/` is empty).

**Therefore my five deferral attestations, stamped `classified_at_identity 29a094eb…`, remain valid.** I did not assume this — I re-ran the real `acceptance_ordering_deferral` against each at this head:

```
D-004-R389 post_accept_cleanup  DEFERRAL_GRANTED  (no refusals)
D-004-R486 accept               DEFERRAL_GRANTED  (no refusals)
D-004-R487 checkpoint           DEFERRAL_GRANTED  (no refusals)
D-004-R488 post_accept_cleanup  DEFERRAL_GRANTED  (no refusals)
D-004-R501 stop_after           DEFERRAL_GRANTED  (no refusals)
```

## A.3 Applicable set — still exactly 233

```
DirectiveRegistry.derive_applicable(M0-T027)  ->  233 ids, unresolved reasons: []
evidence map (233) vs derived (233)           ->  derived-minus-map: []   map-minus-derived: []
amendment-18 rows (R701-R717) applicable to M0-T027: []      <- all sentinel-scoped
```

I confirmed the scoping directly: every one of `R701`–`R717` carries `applicability.task_ids ["D-004-OPTIONB"]`, so none enters M0-T027's set. The set is unchanged at 233.

## A.4 Amendment-18 capture integrity

```
$ python tools/validate_directive_compliance.py --check     -> EXIT 0
manifest version 19 | 19 audit-log entries | 19 source files | 717 requirement rows | 717 locked ids
source-019-amendment.md touched by exactly 1 commit          <- append-only, proven from git
```

**The capture is clean** (R714's first condition). I read `source-019-amendment.md` lines 89–119 verbatim against rows R706–R717 and found the decomposition faithful: Decision 1's ruling, its restriction, and its sequencing are carried as three separate rows (R706/R707/R708) rather than merged; Decision 2 splits into obligation + hard stop (R709/R710); Decision 3 into confirmation + backlog (R711/R712); the resume, authorization and preserved hard stops into R713/R714/R715. Nothing weakened, combined, or omitted. **No capture conflict.**

## A.5 The two other new facts, verified

- **My return is preserved** at `project-control/reports/M0-T027-dcv-final-verification.md` (39,196 bytes). Its orchestrator header discloses one redaction: **9 occurrences, absolute repository path (Windows user-path form) → `<REPO>`**, all in my closing "Files most relevant to this return" list. **The redaction changed no ruling** — I verified 16 ruling-bearing markers survive intact (the `CANNOT PASS` rulings, the `ATTESTED LIFECYCLE DEFERRAL` rows, every `DEFERRAL_GRANTED`, and the full `29a094eb…` identity string), and the BLOCKED verdict and R322/R323/R388 rulings stand exactly as I returned them.
- **The supervisor directive is tracked and its digest anchor holds.** `git show HEAD:.claude/CODEX_CLAUDE_SUPERVISOR_BUILD_DIRECTIVE_v4.3.md | sha256` = `426da3bb22714a403553b013e8969c6bfa424ee01d99e10d1269d0b65e0f5137` — exactly the R702 anchor, so the `.gitattributes` LF pin does what it was added to do. `PENDING-CAPTURE-dispatch-efficiency-and-graph-wiring.md` is present and tracked. My Part 1 dirty-file listing is correspondingly resolved for those files; the identity derivation returns no dirt error.

---

# B. The re-ruling of R322, R323, R388 — my call

**All three reach PASS. There is no ambiguity in application, and no residual obligation is lost.**

## B.1 Reasoning

I stopped at Part 4 because these three compound rows contain accept-stage clauses that had not occurred and that the M0-T034 mechanism structurally cannot defer. That was a question of **legal interpretation of the owner's own directive text**, which is exactly the class of question I am required to escalate rather than resolve. The owner — the author of amendments 8 and 9 — has now ruled on it. That is authority I do not have and did not attempt to exercise.

I accept the ruling as dispositive for these three rows because it is sound on the record, not merely because it was issued:

1. **It is repository-reproducible before the act it authorizes.** Captured verbatim in `source-019-amendment.md`, decomposed into R706–R708, digest-anchored, validator exit 0, merged through protected main as PR #143 — all before any accept.
2. **Its cited basis is a finding I made and have now re-reproduced.** The owner grounds the ruling in my own settled section 3.3: every non-accept clause of the three rows individually verified satisfied. I re-verified those underlying facts hold at `bbbb8ef` — identity, gates, PR/CI evidence and branch state are all unchanged since Part 4.
3. **No obligation is waived, only relocated.** The accept-stage substance of R322/R388 is carried by R486 (accept) and R487 (checkpoint); R323's cleanup residue is carried by R488 and R389. All four are **attested lifecycle deferrals re-confirmed granted at this head**, and `checkpoint()` refuses to record while any registered deferral is unverified. The obligations remain enforced, at the same standard.
4. **It creates no loophole and no mechanism change.** R707 scopes it to three named rows, expressly not a class rule and not a modification of M0-T034 condition (3); R708 returns future compound-row conflicts to the owner.
5. **It is mechanically clean.** A `PASS` row never reaches the deferral path — `_v2_task_unresolved` only calls `acceptance_ordering_deferral` when `state != PASS`. So ruling these three PASS is consumed by the existing code with **zero mechanism change**, exactly as R707 requires. There is no conflict between this ruling and the refusals I reported.

**Clause-by-clause, at this head:** R322 — submit (`77ca816`), protected-main PR (#140), CI verified (all SUCCESS at `77ca816`), merge (`2689b1e`) all satisfied; accept + checkpoint clauses discharged-by-decomposition. R388 — submit, merge through protected main, merged-identity verification all satisfied (I performed the identity verification twice, at `2689b1e` and again here); accept + checkpoint clauses discharged-by-decomposition. R323 — the "clean ONLY" restriction verified with **zero violations** (29 remote heads; the three new PR branches #141/#142/#143 were deleted on merge, and only the two M0-T027 closeout branches remain, pending R488); completion residue discharged-by-decomposition.

## B.2 The three exact verification row objects

```json
{ "id": "D-004-R322",
  "state": "PASS",
  "evidence": [
    "COMPLETED LIFECYCLE EVIDENCE (re-verified at bbbb8ef): submit -- project-control/reports/M0-T027.json submitted_at 2026-07-31T19:32:55.139129+00:00, commit 77ca816; protected-main PR -- PR #140 baseRefName main, MERGED; CI verified -- gh pr view 140 statusCheckRollup, every CheckRun conclusion SUCCESS at headRefOid 77ca816; merge -- mergeCommit.oid 2689b1e24ded98bf20d2d102362579789f47c17c at 2026-07-31T19:40:19Z",
    "ACCEPT-STAGE CLAUSES DISCHARGED-BY-DECOMPOSITION per owner ruling D-004-R706, source-019-amendment.md lines 89-98, merged PR #143; scope restriction D-004-R707",
    "SUBSTANCE CARRIED FORWARD, NOT WAIVED: D-004-R486 (accept) and D-004-R487 (checkpoint) each hold an attested lifecycle deferral re-confirmed DEFERRAL_GRANTED at content identity 29a094eb...; checkpoint() refuses while any registered deferral is unverified"
  ],
  "verified_at": "2026-07-31T22:45:00+00:00",
  "verified_by": "directive-compliance-verifier",
  "reviewed_sha": "bbbb8ef18cc297ece8759535f0cb9484a0d785bc" }

{ "id": "D-004-R323",
  "state": "PASS",
  "evidence": [
    "COMPLETED LIFECYCLE EVIDENCE (re-verified at bbbb8ef): the 'clean ONLY' restriction is honored with ZERO violations -- git ls-remote --heads origin returns 29 heads; every branch deleted during this closeout arc was created for this closeout (control/M0-T034-closeout-authorization-capture, task/M0-T034-governance-acceptance-semantics, control/session-handoff-refresh-2026-07-31-close, task/M0-T027-resubmit-corrected-identity, plus the #141/#142/#143 branches deleted on merge); no unrelated branch was deleted",
    "ACCEPT-STAGE CLAUSE DISCHARGED-BY-DECOMPOSITION per owner ruling D-004-R706, source-019-amendment.md lines 89-98, merged PR #143; scope restriction D-004-R707",
    "SUBSTANCE CARRIED FORWARD, NOT WAIVED: the two remaining closeout branches (control/M0-T027-consolidated-capture at 5cd0c3e, task/M0-T027-closeout-phases-3-4 at 16ae458) are governed by D-004-R488 and D-004-R389, both attested lifecycle deferrals re-confirmed DEFERRAL_GRANTED at content identity 29a094eb..."
  ],
  "verified_at": "2026-07-31T22:45:00+00:00",
  "verified_by": "directive-compliance-verifier",
  "reviewed_sha": "bbbb8ef18cc297ece8759535f0cb9484a0d785bc" }

{ "id": "D-004-R388",
  "state": "PASS",
  "evidence": [
    "COMPLETED LIFECYCLE EVIDENCE (re-verified at bbbb8ef): submit -- project-control/reports/M0-T027.json, commit 77ca816; merge through protected main -- PR #140 into main, merge commit 2689b1e, with all six post-3ed05fda main commits confirmed to be PR merge commits (no direct push); merged-identity verification -- _task_git_identity re-derives 29a094ebdf312767b2ffa964a9cfb0398432e8838db0a211a711f1dd8db2bb97 at merged main, performed independently at 2689b1e and again at bbbb8ef",
    "ACCEPT-STAGE CLAUSES DISCHARGED-BY-DECOMPOSITION per owner ruling D-004-R706, source-019-amendment.md lines 89-98, merged PR #143; scope restriction D-004-R707",
    "SUBSTANCE CARRIED FORWARD, NOT WAIVED: D-004-R486 (accept) and D-004-R487 (checkpoint) each hold an attested lifecycle deferral re-confirmed DEFERRAL_GRANTED at content identity 29a094eb...; the identical submit-to-accept sequence is governed atomically by D-004-R481-R485 (all PASS on completed evidence) and D-004-R486-R488 (deferred)"
  ],
  "verified_at": "2026-07-31T22:45:00+00:00",
  "verified_by": "directive-compliance-verifier",
  "reviewed_sha": "bbbb8ef18cc297ece8759535f0cb9484a0d785bc" }
```

**The re-ruling yields exactly R322/R323/R388 discharged-by-decomposition — no more, no fewer** (R714's second condition).

---

# C. Updated record-level `verification.json` object for M0-T027

```json
{
  "task_id": "M0-T027",
  "directive_id": "D-004",
  "producer": "orchestrator",
  "verifier": "directive-compliance-verifier",
  "reviewed_sha": "bbbb8ef18cc297ece8759535f0cb9484a0d785bc",
  "reviewed_manifest_sha256": "29a094ebdf312767b2ffa964a9cfb0398432e8838db0a211a711f1dd8db2bb97",
  "state": "PASS",
  "note": "<the full text of this re-ruling return, plus the four-part return preserved at project-control/reports/M0-T027-dcv-final-verification.md>",
  "applicable_requirement_ids": [ ...the 233 derived ids... ],
  "requirements": [ ...233 rows... ]
}
```

`reviewed_sha` **must** be `bbbb8ef1…` — `accept()` resolves HEAD and `_v2_task_unresolved` compares it against this field, so any earlier SHA fails closed.

**Exhaustive row-state specification — 228 PASS + 5 pending, total 233:**

1. **204 settled ids — `state: "PASS"`.** Every applicable id except the 29 delta ids. Evidence pointer for each: `project-control/reports/M0-T027-dcv-verification.md` (first pass, at verified SHA `3ed05fda6d434670e5b610e6dad7a8b224a9aa94`), cited under D-004-R670 and D-004-R713.
2. **21 delta ids — `state: "PASS"`:** `R319, R320, R384, R385, R386, R387, R461, R462, R463, R465, R467, R468, R474, R475, R479, R481, R482, R483, R484, R485, R515`. Evidence pointer for each: the per-id evidence given in section 3.2 of `project-control/reports/M0-T027-dcv-final-verification.md`.
3. **3 re-ruled ids — `state: "PASS"`:** `R322, R323, R388`, using the three row objects in section B.2 above **verbatim**.
4. **5 ids — `state: "pending"` plus `lifecycle_classification`:** `R389, R486, R487, R488, R501`, using my section 3.4 attestation objects **verbatim and unmodified** — `classified_at_identity` stays `29a094ebdf312767b2ffa964a9cfb0398432e8838db0a211a711f1dd8db2bb97`, `classified_at` stays `2026-07-31T21:15:00+00:00`, `classified_by` stays `directive-compliance-verifier`. All five **re-confirmed DEFERRAL_GRANTED at this head** (section A.2). Do not restamp them: the identity is unchanged, so the binding is live.

Row template for groups 1 and 2 (unchanged from my Part 4.1, with the SHA updated):

```json
{ "id": "<D-004-Rnnn>", "state": "PASS",
  "evidence": ["<the pointer specified above for that id>"],
  "verified_at": "2026-07-31T22:45:00+00:00",
  "verified_by": "directive-compliance-verifier",
  "reviewed_sha": "bbbb8ef18cc297ece8759535f0cb9484a0d785bc" }
```

**Decision 2 (R709/R710) acknowledged:** `verification.json`'s M0-T027 block is still the stale 97-row block with `reviewed_sha: null` and `reviewed_manifest_sha256: null` — I verified this at `bbbb8ef`. Leaving it for the lawful accept-path rewrite is the owner's instruction; I record the staleness as **known and deliberate**, and I make no out-of-band rewrite request. If `accept()` rejects it, that is R710's hard stop.

---

# D. Authorization statement for mechanical assembly

**Confirmed.** The orchestrator may assemble the 233-row block **mechanically and verbatim** from (a) the row-state specification in section C above, (b) the per-id evidence pointers in sections 3.1 and 3.2 of `project-control/reports/M0-T027-dcv-final-verification.md`, (c) the three row objects in section B.2 of this return, and (d) the five attestation objects in section 3.4 of the preserved return — **with zero orchestrator judgment**. Every id's state, evidence pointer, `verified_at`, `verified_by` and `reviewed_sha` is fully determined by that specification; nothing requires interpretation, selection, or substitution.

Two mechanical constraints, stated so they cannot be got wrong:
- `reviewed_sha` is `bbbb8ef18cc297ece8759535f0cb9484a0d785bc` on the record-level object **and** on every row.
- The five `lifecycle_classification` objects are copied **byte-for-byte**, including `classified_at_identity 29a094eb…`. Restamping or re-dating them would invalidate condition (6) or (2) and refuse the deferral.

**I endorse the dry-run gate:** the orchestrator running the assembled block through the real `task_verification_result()` and treating **any** returned reason as a stop is the correct control, and I ask that it be honored strictly. If the function returns a reason, that is evidence my specification or the assembly is wrong — stop and report, do not adjust the block to make it pass.

---

# E. Final statements

**Is the R673 hard-stop set EMPTY? — YES.**
- R322, R323, R388 all reach PASS (section B). ✔
- Zero UNVERIFIABLE remain: **228 PASS + 5 attested lifecycle deferrals = 233**. ✔
- No new finding, defect, or observation has arisen since Part 4 (section E.1). ✔
- No deviation from expected state: identity, applicable set, gates, packet material digest, branch state, and prohibited-action evidence are all exactly as expected. ✔

**Is R674 "exactly clean" MET? — YES.** Every applicable row is PASS or an attested lifecycle deferral; zero UNVERIFIABLE; zero new findings; **R024 is PASS by my ruling** — my section 4.3 ruling stands, and I extend it to the new delta: I re-scanned every added line across all 9 files in `2689b1e..bbbb8ef` for machine usernames, absolute user paths (both slash forms), session ids, pane ids and hostnames. Two matches, **both benign and neither a leak**: one is the literal row `| pane-id markers | 0 |` inside my own preserved scan-results table, and one is a filename ending in `_handoff.md` appearing in a directory listing inside the supervisor directive, which matched a session-id-shaped pattern without being one. No literal username, session id, pane id, absolute user path, or hostname is disclosed. I describe these patterns rather than quoting matched values. The 9-path redaction applied to my own return is disclosed in its header and changed no ruling.

**Final tally over all 233 applicable ids: 228 PASS · 0 FAIL · 0 UNVERIFIABLE · 5 attested lifecycle deferrals · 0 NOT_APPLICABLE.**

## E.1 Findings and observations

**No new finding.** Nothing in `2689b1e..bbbb8ef` raises a new issue: the amendment-18 capture is clean and append-only, the LF pin holds the R685 digest anchor exactly, the preserved return's redaction touched no ruling, and the packet change is lifecycle-only.

Status of my previously recorded observations, for completeness — **none is new, and none blocks**:
- **F-1** — resolved by owner Decision 1 (R706/R707/R708). Closed.
- **OBS-A** (M0-T034 `self_check` while its code is live) — resolved by owner Decision 3 (R711), backlogged by R712. Closed.
- **OBS-B** (the evidence map's internal `reviewed_sha`/`content_manifest_sha256` still read `3ed05fda`/`e3b0c442`) — **still open, unruled, non-blocking**. `accept()` never reads those fields, so there is no mechanical consequence; it was before the owner in my Part 4 and they did not rule on it. I flag it as open rather than infer consent from silence, and I do not treat it as a stop because it is not new.
- **OBS-C** (stale local remote-tracking ref) and **OBS-D** (`readonly_agent_guard.py` over-denial, which recurred twice more in this pass on `>=` and `sed`) — informational, unchanged, non-blocking.

## E.2 Independence and model disclosure

I am not the producer of any change I reviewed, and I authored no commit, packet field, gate record, or report in this delta. I ruled no requirement on the strength of a producer claim, checklist, or summary; every fact above was re-derived from a file, git object, control-plane record, deterministic tool run, or GitHub API response I named. I did not soften my earlier BLOCKED verdict — it stood until the owner exercised interpretation authority that is theirs and not mine, and I re-verified the ruling's cited basis before accepting it as dispositive.

**Model: Opus 5, exact id `claude-opus-5[1m]`.** I am not Fable 5 and make no claim to be. Record nothing about Fable 5 for this wave.

— RETURN COMPLETE —
