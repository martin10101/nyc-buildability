# D-004 — source-017 (owner amendment 16, verbatim) — consolidated capture batch

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message. Amends `source-001.md`.
Frozen baseline unchanged: `421265709f81a40e20f3d890609907ed932967dd`.

Head at capture time: `control/M0-T027-consolidated-capture` branched from `origin/main` =
`ffacee91b738cd742e72d8c52091e8400d932a87` (the merge commit of PR #135).

Requirement IDs added by this amendment start at `D-004-R593`; no existing source file or
requirement row is edited.

## Scope

Per the owner's standing instruction, every row below carries `task_ids: ["D-004-OPTIONB"]` — the
session sentinel. Execution authority, not M0-T027 task-content. Verified after the write:
M0-T027's resolver-derived applicable set is unchanged and no row of this amendment enters it.

## Commencement clause (owner, Message F item 1)

The owner directs: *"Include the commencement clause: this captured text itself authorizes the
batch commit AND the merge of its PR once CI is green and the diff has been shown to me."*
Accordingly **this capture authorizes its own commit and the merge of its pull request**, subject to
the two stated conditions: CI green, and the diff shown to the owner first. No further amendment is
owed to justify this batch. This is the same self-referential construction the fourth independent
pass examined and ruled genuinely terminating rather than viciously circular.

## What this batch cures

1. **`D-004-R479` was left unsupported.** R479 requires stopping on any FAIL, BLOCKED, or unresolved
   requirement. PR #135 was merged while 11 requirements were UNVERIFIABLE and the pass-5 verdict
   was FAIL. The fifth verifier declined to adjudicate, correctly: *"I cannot adjudicate it without
   seeing the owner authorization that released the merge lane."* That authorization is **Message E**
   below; it now exists in the repository, so R479 stands on evidence rather than narrative.
2. **`D-004-R578`'s misattribution** is corrected by an authoritative new row (R578's own text is
   append-only and stands unedited as the owner-ruled erratum).
3. **Message A and Message B obligations that were omitted or combined** get their own atomic rows —
   the exact defect class (weakened / combined / omitted) the fourth pass identified.
4. **The `source-012` arithmetic erratum** ("97 ids recorded vs 150 derived") is corrected on the
   record: the evidence map held **128** at `origin/main` and the resolver derives **233**.
5. **The Message C confirmation** — the owner has confirmed Messages A, B and C as owner-issued and
   does not repudiate head `f08769e1`, resolving the standing condition the fourth pass placed on
   `R573`/`R575`.

## Redaction

No redaction was required in this capture: none of the three owner messages below contains a
session identifier, machine username, absolute user path, or hostname. Verified by scan before
commit.

---

## MESSAGE D — decisions on the three open items (verbatim, complete)

Decisions on all three open items:

1. MESSAGE C CONFIRMED. Messages A, B, and C are mine, issued by me in the owner
   channel. I have now reviewed HEAD f08769e and I do not repudiate it. The standing
   condition on R573/R575 is resolved. Capture this confirmation in the final
   consolidated batch (item 2), not now.

2. R578 STANDS as a recorded erratum — no source-017 this round. The correct
   attribution is plainly stated in dcv4's preserved return and it creates no
   enforcement gap. Defer ALL pending capture work to ONE final consolidated batch
   at the end of the closeout: the R578 attribution-correction rows, the missing
   Message A/B obligation rows, this confirmation, and every authorization still
   uncaptured. One batch, once, shown to me before commit.

3. SUBMIT LANE RELEASED. Push the task branch (never main) and open the PR — do NOT
   merge. Run the normal gate sequence up to but not including merge/accept, so the
   15 UNVERIFIABLE rows become verifiable. I acknowledge the commit trailers carry
   the session id, consistent with existing trailer practice on main (OBS-5); accepted,
   with the systemic trailer question staying parked under R561.

Then dispatch the verification.json rebuild with this scope: evidence limited to files
changed since the last verified HEAD plus the newly-verifiable rows and R024's status;
cite dcv2–dcv4's delivered rulings at their HEADs as settled rather than re-deriving
them, flagging anything you must reopen with the new evidence that reopens it. Goal:
233/233 independently verified, R024 recorded PASS by the verifier — never by you.

STOP when the PR is open and CI has reported, and show me: PR link, CI status, and the
rebuild verdict. No merge, no accept, no final capture batch until I review.

---

## MESSAGE E — the merge authorization and path-3 decision (verbatim, complete)

Decisions on the rebuild verdict:

1. MERGE RELEASED. Merge PR #135 exactly as verified — head 16ae4589, no new commits
   to that branch first. This closes R484/R485 and unlocks R475.

2. PATH 3 CHOSEN — structural fix. Option B is NOT invoked and is not to be widened;
   the verifier was right not to stretch the trigger. Prepare an amendment re-scoping
   the eight genuinely circular rows (R322, R323, R388, R389, R486, R487, R488, R501)
   to the D-004-OPTIONB sentinel, following the R502-R51x precedent, with a per-row
   justification of why each is a session-lifecycle act. The independent verifier —
   not you — must confirm that classification for all eight before the re-scope counts.

3. CONSOLIDATED CAPTURE BATCH — one batch, after merge, on a fresh control branch via
   the normal PR flow. Contents: the path-3 re-scope amendment; the R578 attribution
   correction and missing Message A/B obligation rows; my Message C confirmation; my
   "97 vs 150" arithmetic erratum correction (actual: 128 -> 233); and this
   authorization, captured verbatim. Show me the batch diff before its commit.

4. BEFORE TRANSCRIPTION: have the verifier state what input yields
   reviewed_manifest_sha256 e3b0c442... . If it is the SHA-256 of the empty string,
   explain why an empty-input digest is the designed value or correct the input.
   Do not transcribe an unexplained empty-hash as an identity.

5. FINAL VERIFICATION at merged main: delta-scoped to the merge-closed rows, the
   re-scoped set, the capture batch, and R024's status. Cite the rebuild's delivered
   rulings at 16ae4589 as settled; reopen only with new evidence, flagged. Preserve
   this verifier's full return as a tracked file so it doesn't rest on transcription
   like pass 2 did. Target: every applicable row PASS at the adjusted set, R024
   recorded PASS by the verifier — never by you.

6. STOP before accept. Show me: merge confirmation, batch diff, re-scope confirmation,
   the e3b0c442 answer, and the final verdict. Acceptance is my call and I make it
   after seeing those — do not accept, checkpoint, or close.

---

## MESSAGE F — the execution-order decisions authorizing this batch (verbatim, complete)

Decisions, in execution order:

1. CAPTURE BATCH — IMMEDIATE, act one. Fresh control branch, normal PR flow. Contents:
   my merge authorization (curing R479); the R578 attribution-correction rows; the
   missing Message A/B obligation rows; my Message C confirmation; the 97-vs-150
   arithmetic erratum (actual: 128 -> 233); the prior authorization; and THIS
   authorization, captured verbatim. Include the commencement clause: this captured
   text itself authorizes the batch commit AND the merge of its PR once CI is green
   and the diff has been shown to me. Show me the batch diff, then proceed on my
   confirm. Decompose per the intake standard — do not weaken, combine, or omit
   (that is the defect class of R578/R579; do not repeat it).

2. PATH 3 = OPTION (ii), the tools/ fix. Do NOT edit any row's applicability in
   place — the append-only invariant is not to be holed, for five rows or eight.
   Contract one small controlled task ("governance acceptance semantics"), exact
   allowed paths under tools/, covering BOTH defects this round exposed:
   (a) lifecycle-aware acceptance: rows whose sole unmet obligations are
       acceptance-ordering lifecycle acts (accept, post-accept cleanup, checkpoint,
       stop-after) must not gate accept() — evaluated, not deleted; verified at the
       first post-accept opportunity instead;
   (b) close the vacuous-guard gap: governance-shaped tasks (allowed_paths entirely
       under project-control/) get real staleness/dirt guards, and reviewed_sha is
       actually compared.
   Normal gates apply. The independent verifier must confirm, per row, that each of
   the eight qualifies as acceptance-ordering under (a) — classification is theirs,
   not yours. Fact-check to include in the task packet: confirm whether option (iii)
   alone would have reached acceptance (I expect not, given R322/R323/R389 remain);
   record the answer either way.

3. FINAL VERIFICATION waits for item 2 to merge, then runs once at that head:
   delta-scoped to the merge-closed rows (R484/R485/R475), the lifecycle-classified
   set, the capture batch, and R024's status. Cite the rebuild's rulings at 16ae4589
   as settled; reopen only with flagged new evidence. The verifier must ALSO manually
   perform the guards accept() currently skips — reviewed_sha vs head, project-control
   tree state, identity freshness — and record them in its return. Preserve the full
   return as a tracked file; no more rulings resting on transcription.

4. STOP before accept, as before: show me batch-merge confirmation, the semantics-task
   acceptance, the (iii)-sufficiency answer, and the final verdict. Acceptance of
   M0-T027 remains my explicit call.

---

## CORRECTIONS OF RECORD

### C-1 — `D-004-R578` attribution (authoritative correction)

`D-004-R578` reads that Message A "authorized committing source-014". **That is incorrect.**
Message A's own closing is *"Do not commit until I've seen that."* The commit authorization for
`0b8c0dceb08f9cda8cbd1fb2f7e55ea80a5d479c` came from **Message B** ("Commit approved… Commit the
R024 cure and both amendment captures now"). Message A authorized only the *disposition* — that
`source-014` would be committed with the identifier redacted and annotated, superseding amendment
14's item 3 — **not the timing**. R578's text is locked and stands unedited by owner ruling; the
rows below are the authoritative correction.

### C-2 — `source-012` arithmetic erratum

`source-012-amendment.md` states *"97 ids recorded vs 150 derived"*. Neither figure is reproducible.
The evidence map held **128** entries at `origin/main`; the canonical resolver derives **233**; and
**97** is the row count of the stale `verification.json` M0-T027 block, a different artifact. The
binding obligation — *"Do not preserve the old count"* — is satisfied (128 → 233). The fifth
independent pass reopened `D-004-R515` from UNVERIFIABLE to PASS on exactly this reading.
