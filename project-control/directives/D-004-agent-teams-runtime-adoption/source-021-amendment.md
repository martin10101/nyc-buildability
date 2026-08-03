# D-004 — source-021 (owner amendment 20, verbatim) — one-time exact-shape settings-tightening grant

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message (direct prompt to the
orchestrator session, immediately following the amendment-19 merge-authority flag and the
orchestrator's on-the-record answer). Amends `source-001.md`.
Frozen baseline unchanged: `421265709f81a40e20f3d890609907ed932967dd`.

Head at capture time: `control/D-004-amendment-20-settings-grant` branched from
`origin/main` = `b5589d0...` (the merge commit of PR #146).

Requirement IDs added by this amendment start at `D-004-R725`; no existing source file or
requirement row is edited.

## External-fact anchors, verified at capture time

- Both target files are UNTRACKED: `~/.claude/settings.json` is the user-global file outside the
  repository; `.claude/settings.local.json` is gitignored (verified `git check-ignore` positive,
  `git ls-files` empty). The "touch no tracked file" constraint is therefore satisfiable and the
  execution evidence lives in this capture and the Step 7 report, not in tracked diffs.
- "The exact intended shape you recorded" for edit 2 resolves to ADR-005 rule 5's recorded
  intent: `git merge --no-ff task/*` — so `Bash(git merge*)` / `PowerShell(git merge*)` narrow to
  `Bash(git merge --no-ff task/*)` / `PowerShell(git merge --no-ff task/*)`.
- Under D-004-R721 this capture's own PR QUEUES for the owner; the owner's "execute it yourself
  rather than routing it back to me" applies to the settings edits, which proceed once this
  capture is committed, pushed, and its PR is open (repository-reproducible authorization, R664
  principle).

## Redaction

No redaction required: the captured text contains no session identifier, machine username,
absolute user path, or hostname (the `~/` form is the owner's own shorthand, not a machine
path). Verified by scan before commit.

---

## THE OWNER MESSAGE (verbatim, complete)

OWNER GRANT — one-time, exact-shape settings tightening. This is my file and
my explicit instruction; execute it yourself rather than routing it back to
me. Capture this message per the compliance process first, then:

1. ~/.claude/settings.json (user-global): in permissions.allow, REMOVE
   "Bash(gh pr *)" and ADD "Bash(gh pr view *)", "Bash(gh pr checks *)",
   "Bash(gh pr diff *)", "Bash(gh pr list *)", "Bash(gh pr create *)".
   Change nothing else in the file.
2. .claude/settings.local.json (project-local): narrow the two rules you
   flagged as written broader than their intent (Bash(git merge*) and its
   PowerShell variant) to the exact intended shape you recorded.

Constraints: tightening only — the post-state must be a strict subset of the
pre-state plus the five named narrow allows; back up both files before
editing; report before/after of the changed arrays with SHA-256 of each file
pre and post; touch no tracked file. This grant covers exactly these edits,
expires on completion, and sets no precedent: settings files remain otherwise
untouchable to you, and every merge still queues for me under R721 regardless
of what any allowlist says.
