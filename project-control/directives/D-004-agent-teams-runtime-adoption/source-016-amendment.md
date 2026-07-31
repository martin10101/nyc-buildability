# D-004 — source-016 (owner amendment 15, verbatim) — the approval chain, closed

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message. Amends `source-001.md`.
Frozen baseline unchanged: `421265709f81a40e20f3d890609907ed932967dd`.

Head at capture time: `task/M0-T027-closeout-phases-3-4` =
`0b8c0dceb08f9cda8cbd1fb2f7e55ea80a5d479c`; `origin/main` =
`11f3540c602849f4100517f35b7b93eca6742a8d` (unchanged).

Requirement IDs added by this amendment start at `D-004-R577`; no existing source file or
requirement row is edited.

## Why this amendment exists — the defect it cures

The third independent verification pass ruled **D-004-R024 PASS** but found a **NEW DEFECT**: rows
**`D-004-R573`** ("After the item-1 redaction STOP, still uncommitted") and **`D-004-R575`** ("Do
NOT commit, submit, push, merge, accept, or rebuild verification.json yet") are captured, binding
prohibitions — and commit **`0b8c0dc`** is a commit. The owner's approvals had lifted them, but
those approvals existed **only as orchestrator narrative** (in `source-015-amendment.md`,
`manifest.json` audit entry 14, and the `D-004-R572` row) and never as captured owner text. The
verifier grepped for the authorization and found three narrative locations and no source file, and
therefore ruled `R573`/`R575` **UNVERIFIABLE**: the prohibited act had occurred and the
authorization lifting it was not reproducible from repository evidence.

This amendment captures **all three** outstanding owner approvals verbatim — including the one that
authorizes this very commit — so that the approval chain is reproducible end to end from the
repository alone. **The recursion terminates here by the owner's explicit instruction** (item 2
below): the authorizing message and the act it authorizes land in the same commit, so no further
amendment is owed to justify this one.

## R024 redaction inside owner-verbatim text (owner-approved convention, applied again here)

| occurrences | substitution | location |
|---|---|---|
| 1 | truncated session-id prefix -> `<REDACTED-SESSION-ID>` | Message A, item 1 |

As in `source-014` and `source-015`, the substitution sits **inside owner-verbatim text** and the
original at that position was the owner **naming the identifier to be redacted**, so the line reads
self-referentially. Nothing else in any of the three captured messages was altered, added, or
removed — no instruction, constraint, prohibition, deferral, ordering, or approval.

## Corrections folded in by owner instruction

1. **Scope count 75 -> 76.** Prior narrative and `manifest.json` audit entry 13 state "75
   pre-existing files" carrying the machine username. The verified figure is **76**: 75 under
   `project-control/` plus **1** under `.claude/agent-memory/data-contract-verifier/`. All 76 are
   untouched by this branch. Audit entry 13 is committed and append-only, so the correction is
   recorded here and in a new audit entry rather than by editing it.
2. **G5 command-string clause.** Two of the G5 redaction substitutions fall inside fenced command
   blocks, so those command **strings** are no longer executable-as-printed. No command **output**
   was altered. The G5 annotation block said the latter but not the former; the clause is added
   there and recorded here.

---

## MESSAGE A — the Option-4 approval (verbatim, one disclosed redaction)

Option 4 — approved, applied to both pending captures.

1. source-014-amendment.md: redact the single <REDACTED-SESSION-ID> occurrence at line 41
   → <REDACTED-SESSION-ID>, same convention. Add the header note recording that this
   substitution sits inside owner-verbatim text and that the original named the
   identifier being redacted. Change nothing else in the capture.

2. Capture my two-redaction instruction (the prior message) as amendment-14/source-015
   the same way — redact any <REDACTED-SESSION-ID> prefix it contains, annotated as
   owner-verbatim, so the manifest doesn't cite an uncaptured source.

3. After both: re-run the full grep (full id, truncated prefix, username, email) across
   ALL tracked files including the two capture files, and confirm the validator
   (validate_directive_compliance.py) passes with the registry consistent — manifest
   digests matching the redacted files, R553–R567 source_refs resolving.

Then STOP and show me: the two capture diffs, the final grep table (expect zero across
the board), and the validator result. Do not commit until I've seen that.

Still no push, no merge, no accept, and do not set R024 in verification.json yourself —
that's the independent verifier's call after I release it.

---

## MESSAGE B — the commit approval (verbatim, complete)

Commit approved. source-015 email occurrence accepted — consistent with the R570
deferral; do not redact it, keep the email question uniform under R561. Commit the
R024 cure and both amendment captures now. Then release the independent verifier to
rule R024 in verification.json — I am not setting that status, the verifier is.
Still no push, no merge, no accept until the verifier returns.

---

## MESSAGE C — this authorization, which lifts R573/R575 for the source-016 commit (verbatim, complete)

Proceed with the M0-T027 closeout through the next safe checkpoint. Specifically:

1. Capture source-016-amendment.md: record both my prior approvals verbatim (the
   Option-4 approval and the commit approval), with rows stating exactly which
   prohibitions (R573, R575) they lifted and for which commit (0b8c0dc). Fold in the
   75→76 scope correction and the G5 command-string clause.

2. This authorization ITSELF lifts R573/R575 for the source-016 commit and authorizes
   that commit — capture THIS sentence too, so the approval chain is fully reproducible
   from the repository and the recursion terminates here.

3. Commit source-016. Confirm gitleaks clean, validator exit 0, tree frozen.

4. Re-run the independent directive-compliance verifier on the new HEAD, with the same
   adversarial framing as before. Let it rule R024 and the R573/R575 rows from repository
   evidence — do not set any verification.json status yourself.

5. Then STOP and show me: the source-016 diff, the frozen HEAD sha, and the verifier's
   full return. Nothing pushed, merged, or accepted.

If any NEW defect appears (as item 8 did last round), stop at step 5 and surface it
rather than fixing it unprompted.
