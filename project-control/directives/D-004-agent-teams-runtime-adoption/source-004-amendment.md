# D-004 — source-004 (owner amendment 3, verbatim)

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message. Amends `source-001.md`.
Frozen baseline unchanged: `origin/main` = `421265709f81a40e20f3d890609907ed932967dd`.
Requirement IDs added by this amendment start at `D-004-R105`; no existing row is edited.

---

NEW-SESSION BOOTSTRAP + CONDITIONAL STEP-1 GO (D-004).
The project path was renamed to remove a space (hook word-splitting
bug) and the machine-global hooks block was removed owner-side.
Fresh conversation by design: spawn any team fresh; never reference
the prior session's team or task list.

1. VERIFY MACHINE: confirm CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS is
   active and version ≥ 2.1.178. Perform one harmless hook-triggering
   action and SHOW that UserPromptSubmit / PostToolUse / Stop hooks now
   run without the "Is a directory" error. If ANY hook still errors:
   STOP, report, do nothing else.
2. RE-ORIENT: python tools/project_control.py status; confirm local
   main = origin/main = 421265709f81a40e20f3d890609907ed932967dd;
   confirm the uncommitted D-004 capture is intact (source-001.md,
   source-002-amendment.md, source-003-amendment.md,
   requirements.json rows R001-R104, manifest.json version 3,
   verification.json, index.json modification); re-run the registry
   validator and show the result.
3. If 1 and 2 are fully green, this message is my explicit GO for
   STEP 1 with flag-3 option (a): contract M0-T027, commit the D-004
   capture + M0-T027 packet together via the normal protected-main
   workflow, then run the read-only reviewer pilot exactly as D-004
   Step 1 specifies — including the sentinel negative test with your
   independent test -e verification. Present the Step-1 evidence
   package and STOP.
4. EFFORT stays open: apply nothing; re-present the item-3 mechanism
   report alongside the Step-1 evidence, plus the R095 ID-correction
   note, and I will decide then.
Anything ambiguous or not green: stop and report instead of proceeding.
