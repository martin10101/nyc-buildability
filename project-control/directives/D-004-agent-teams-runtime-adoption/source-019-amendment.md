# D-004 — source-019 (owner amendment 18, verbatim) — F-1 disposition, three owner decisions, and the conditional resume of the amendment-17 closeout

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message (direct prompt to the
orchestrator session). Amends `source-001.md`.
Frozen baseline unchanged: `421265709f81a40e20f3d890609907ed932967dd`.

Head at capture time: `control/D-004-amendment-18-capture` branched from
`origin/main` = `1f6aaa6553c649c5717823b53526eb1e6e462463` (the merge commit of PR #141).

Requirement IDs added by this amendment start at `D-004-R701`; no existing source file or
requirement row is edited.

## Context

Delivered immediately after the STEP 3/STEP 4 stop of the amendment-17 closeout: the final
independent verification (preserved verbatim as
`project-control/reports/M0-T027-dcv-final-verification.md`, merged in PR #142) returned
BLOCKED — 225/233 PASS, 0 FAIL, 5 attested lifecycle deferrals, 3 UNVERIFIABLE
(R322/R323/R388, finding F-1: compound rows the merged M0-T034 deferral mechanism correctly
refuses), plus OBS-A/OBS-B for owner judgment. This amendment carries the owner's rulings on
F-1 (Decision 1), verification.json handling (Decision 2), OBS-A (Decision 3), a re-orientation
correcting the orchestrator's prior report, and the conditional resume authorization replacing
the show-me stop with a self-check gate.

## Scope

Per the owner's standing instruction, every row of this amendment carries
`task_ids: ["D-004-OPTIONB"]` — the session sentinel. Execution authority and owner rulings,
not M0-T027 task-content. Verified after the write: M0-T027's resolver-derived applicable set
is unchanged at 233 and no row of this amendment enters it.

## External-fact anchors, verified at capture time

- `origin/main` = `1f6aaa6` (PR #141 merged by the owner at `2026-07-31T20:57:18Z`).
- `148d13b` is an ancestor of `ebb52e1` (verified `git merge-base --is-ancestor`): the
  orchestrator's stop branch was built on the owner's commit, so the tracked supervisor
  directive and pending-capture record reached main via the PR #142 merge, exactly as the
  owner's re-orientation states. PR #141's net delta was `9790f8e` (the `.gitattributes` LF
  pin) alone.
- `.claude/CODEX_CLAUDE_SUPERVISOR_BUILD_DIRECTIVE_v4.3.md` hashes to
  `426da3bb22714a403553b013e8969c6bfa424ee01d99e10d1269d0b65e0f5137` — MATCHES the R685
  anchor.
- `project-control/directives/PENDING-CAPTURE-dispatch-efficiency-and-graph-wiring.md` is
  present and tracked.
- `OWNER_DIRECTIVE_DRAFT_dispatch-efficiency-and-graph-wiring.md` (repo root, untracked by
  design) hashes to `bd6c4ec2151202bb5209ee62f4cc2a3f94538cd40b695604ceff0e32d1c22b6b` —
  MATCHES the R679 anchor.
- Local branch `control/track-closeout-artifacts` was already deleted by the owner's
  `gh pr merge 141 --delete-branch`; the deletion the owner directs is verified rather than
  re-performed. `bad-amend-backup` exists and is untouched.

## Redaction

No redaction was required: the captured text contains no session identifier, machine
username, absolute user path, or hostname. Verified by scan before commit.

---

## THE OWNER MESSAGE (verbatim, complete)

OWNER DECISIONS AND RESUME — D-004 amendment 17 closeout, F-1 disposition.
Capture this message verbatim through directive compliance (append-only D-004
amendment) before acting on any part of it.

RE-ORIENT FIRST (read/sync only) — corrections to your last report, verified
by me against origin: the branch you discovered was never local-only. It was
pushed and had an open PR (#141) the whole time; and its first commit 148d13b
is already reachable from ebb52e1, because your own stop branch was built on
it — the tracked supervisor directive v4.3 and the tracked pending-capture
record are ALREADY on main via the #142 merge. The branch's only net delta
was 9790f8e, the .gitattributes LF pin protecting the R685 digest anchor
from autocrlf checkouts, and I have now merged that as PR #141. This answers
your first standing question; nothing about that branch remains for you to
push or hold. Now: pull main; verify
.claude/CODEX_CLAUDE_SUPERVISOR_BUILD_DIRECTIVE_v4.3.md hashes to
426da3bb22714a403553b013e8969c6bfa424ee01d99e10d1269d0b65e0f5137 and
project-control/directives/PENDING-CAPTURE-dispatch-efficiency-and-graph-wiring.md
is present; on any mismatch, stop and report. Delete the merged local branch
control/track-closeout-artifacts only. Known owner-plane local state, not
yours to touch, clean, or reconcile: the local branch bad-amend-backup (my
bookmark), the modified tracked agent-memory file (the 2026-07-29 M0-T031
worktree-isolation learning — preserved by me off-repo, backlogged for a
controlled reconciliation), the untracked agent-memory files, and the
untracked root efficiency draft (untracked by design). Report the KEY NAMES
ONLY (no values) of the untracked root .npmrc, without modifying or deleting
it.

DECISION 1 — F-1, route (a), scoped: the accept-stage clauses of exactly
R322, R323, and R388 are ruled DISCHARGED-BY-DECOMPOSITION. Basis, cited as
settled findings from project-control/reports/M0-T027-dcv-final-verification.md
section 3.3: every non-accept clause of the three rows is individually
verified satisfied, and amendment 9's atomic rows R481-R488 govern the
identical submit-to-accept sequence correctly (R481-R485 PASS on completed
evidence; R486-R488 defer with attestations). This ruling names those three
rows only; it is not a class rule, not precedent for future compound rows,
and does not modify M0-T034 condition (3) or any mechanism. Any future
compound-row conflict returns to me.

DECISION 2 — verification.json: leave the stale block in place; do not write
BLOCKED. The lawful accept path rewrites it at acceptance; record that this
staleness is known and deliberate. If the accept path rejects the stale file,
stop and report — do not rewrite it out of band.

DECISION 3 — OBS-A: confirmed as the intended Step-1 posture. M0-T034's
mechanism is trusted through PR #138's merged, G3/G5-passed, CI-green state;
its lifecycle record is process debt. Add "drive M0-T034 to submit/accept" to
the owner backlog; do not act on it now.

THEN RESUME amendment 17 where it stopped: re-rule only the F-1-affected rows
at current head (delta-scoped; every other Step 3 finding is settled and
cited, not re-derived). On my explicit instruction to minimize owner touches,
a self-check gate replaces a show-me stop: if the amendment capture is clean
and the re-ruling yields exactly R322/R323/R388 discharged-by-decomposition
with an otherwise empty hard-stop set, proceed without a further stop into
Step 4 accept -> Step 5 efficiency capture (R307: DEFERRED arm) -> Step 6
Phase 0 -> Step 7 consolidated stop. Any capture conflict, decomposition
ambiguity, unexpected re-ruling result, or new finding = stop and report, as
always. Every stop is a report.

At Step 7, deliver the Phase 0 return packet and the supervisor task packet
for Phases 1-5. Do not begin implementation beyond Phase 0's two permitted
writes; the build dispatch is my next and separate decision.
