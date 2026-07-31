# D-004 — source-014 (owner amendment 13, verbatim)

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message. Amends `source-001.md`.
Frozen baseline unchanged: `421265709f81a40e20f3d890609907ed932967dd`.

Head at capture time: `task/M0-T027-closeout-phases-3-4` =
`f4c7c3be0e45c125c2bf1bf4790fc8e5ab053424`; `origin/main` =
`11f3540c602849f4100517f35b7b93eca6742a8d` (unchanged).

Requirement IDs added by this amendment start at `D-004-R553`; no existing source file or
requirement row is edited.

## R024 redaction inside owner-verbatim text (owner-approved, 2026-07-30)

**One substitution was applied to the verbatim owner message below**, at the line beginning
"session id (…)":

| occurrences | substitution |
|---|---|
| 1 | truncated session-id prefix -> `<REDACTED-SESSION-ID>` |

This substitution sits **inside owner-verbatim text**, which is a different and more serious
category than the reviewer-return redactions cured elsewhere in this closeout, and it was therefore
applied only on the owner's explicit approval rather than on the orchestrator's judgement. **The
original text at that position named the identifier being redacted** — the owner was specifying
which string to remove — so the line now reads self-referentially. Nothing else in the capture was
altered: no instruction, constraint, prohibition, deferral, or ordering was changed, added, or
removed. The substitution exists so that the identifier does not survive in the repository through
the very amendment that ordered its removal.

## Scope

Continuing the owner's standing instruction for execution authorizations in this arc
(`source-013-amendment.md`), every row below carries `task_ids: ["D-004-OPTIONB"]` — the session
sentinel. This is execution authority, not new M0-T027 task-content. Verified after the write:
M0-T027's resolver-derived applicable set remains **233** and no row of this amendment enters it.

## Context — what this authorizes

The second-pass independent verification returned **FAIL**: 217 PASS, **1 VIOLATED**
(`D-004-R024`, evidence hygiene), 15 UNVERIFIABLE. The violation is in two reviewer-return files
the orchestrator authored on this branch, which carry the machine username in absolute paths and,
in one case, a session identifier. The owner authorizes the cure for those two files **only**, and
expressly prohibits touching the 75 pre-existing files on `origin/main` that carry the same
pattern — those are accepted, immutable work, and the standing-interpretation question is deferred
to a separate owner decision.

---

## Owner message (verbatim, complete as received)

Authorized — item 1 only, with the constraints below.

ITEM 1 (execute now): Cure R024 in the two files you authored on this branch —
M0-T027-G3-report.md and M0-T027-G5-report.md — and in the verifier addendum if it
will be written to a tracked file. Redact both classes using D-004's native
convention: machine username → <REDACTED-USER>, absolute paths → <REPO>/…,
session id (<REDACTED-SESSION-ID>…) → <REDACTED-SESSION-ID>. Annotate each redaction
inline so preservation stays honest. Change no substance, no ruled evidence, no
verbatim reviewer content beyond the redaction tokens themselves. Touch only files
authored in this unmerged branch.

ITEM 2 (do NOT touch): Leave the 75 pre-existing files on origin/main alone. They are
accepted, immutable work; rewriting them here would breach the closeout's containment.
Log the inconsistent-R024-enforcement question and OBS-6 (the harness reports absolute
paths while R024 forbids them) as a separate directive-amendment item for my later
decision. Do not fix-forward or reinterpret R024 under this GO.

ORDERING: Apply the redaction first, then rebuild verification.json — it may not record
R024 as PASS while any leak stands. Do not submit, push, merge, or accept.

After the redaction: STOP and show me (a) the exact diff of what you changed,
(b) confirmation that git grep for the username and the session-id string returns zero
matches in your branch's tracked files, and (c) the rebuilt R024 status. Wait for my
review before anything is pushed or accepted.

Deferred to a later turn, do not act on now: your §13.11 enum-precision note, the
stale current_d004_locked_total refresh, and the AS-9 disclosure completion. One thing
at a time — the R024 cure is the blocker; the rest after I've reviewed the diff.
