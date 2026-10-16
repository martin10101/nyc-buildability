# M0-T198 reviews (every return kept unchanged)

- Produced by the orchestrator (governance task; the owner asked the orchestrator itself to build it): d0c22841 on task/wave29-scenario-drawings (3 files, all inside the allowed paths).
- G2 orchestrator self-check at 8e1d5912: frontmatter valid; the rule is always loaded (no paths frontmatter); lane coverage PASS; CI read green at that head.
- G3 code-reviewer PASS, no required findings. Advisory 1: the carry-over takes effect once the branch is merged to main (recorded as the open part of R314).

Every reviewer is an AI agent; none is a human or professional review.

## G3 (code-reviewer)

VERDICT: PASS — G3 on M0-T198 (code-reviewer, independent AI agent; this is not a human or professional review).

Reviewed at frozen head d0c2284147a6d871d66cb7023dfc8f0a7b5e0c53 (worktree /root/project/w-wave29; `git rev-parse HEAD` matched). Scope confirmed: the commit touches exactly the three allowed-path files and nothing forbidden.
  .claude/rules/helper-briefing.md  (+12)
  .claude/skills/dispatch-brief/SKILL.md  (+57)
  project-control/reports/M0-T198-producer-report.md  (+18 -1)

## Checks run (read-only, under heavy-run.lock where applicable)
- `python3 tools/context_budget_check.py` -> PASS, EXIT 0. helper-briefing.md appears in the "Eager (auto-loaded) project instructions" list (963B, 12L, ~241 tok); eager total ~12983 tok, no cap (D-093-R074). This is S5.
- `python3 scripts/lanes/check_lane_paths.py --coverage` -> "LANE COVERAGE PASS: 10930 file(s), each owned by exactly one lane", EXIT 0.

## Evidence for each brief check

(a) Is a no-`paths:` rule really always-loaded (incl. subagents)? — VERIFIED (this runtime), with one bounded UNKNOWN.
 - tools/context_budget_check.py keys "eager" on absence of a real `^paths:` front-matter key (lines 43-52) and lists helper-briefing.md as eager alongside research-and-verification.md, expansion-agent-dispatch-hold.md, living-files.md, CODING_RULES.md, PROGRAM_KNOWLEDGE.md. The tool's own header (lines 4, 14) states "every session (and every subagent) eagerly loaded ... every `.claude/rules/*.md` WITHOUT `paths:` frontmatter."
 - Direct runtime evidence: as a subagent in THIS harness I received the other no-`paths:` rules injected at start as "project instructions, checked into the codebase." That is first-hand confirmation the mechanism reaches subagents here.
 - helper-briefing.md has no front-matter at all (starts with `#`), matching research-and-verification.md's always-loaded form; the path-scoped rules carry a `paths:` block (e.g. code-architecture.md). So the file is correctly shaped to load unconditionally.

(b) Does the skill frontmatter match the repo format so it is listed? — VERIFIED.
 - dispatch-brief/SKILL.md frontmatter carries `name: dispatch-brief` + `description:`, closed with `---`. Several committed skills also carry a `name:` field (loop-ask, loop-codex, loop-*, pr-review, session-handoff); others use `description:` only. Both forms are valid and listed. The name matches the directory. Valid, listable frontmatter. This is S1.

(c) Any clause conflicting with CLAUDE.md / .claude/rules / ORCHESTRATION_POLICY / owner rows? — NONE FOUND.
 - Read-only limits (no write/commit/push/memory, ledger `status` only), builder limits (own worktree reset to named head, allowed paths only, never push, one commit + producer report), ports 3000/3001/8000 forbidden + preview not stopped, heavy-run.lock, roster-type dispatch with NO model parameter, unnamed spawns for writers — all match CLAUDE.md, PROGRAM_KNOWLEDGE and D-085. No clause authorizes a helper to push, write memory, use the preview ports, or override a model.
 - Disconfirming check (brief item): I looked for wording that would let a helper widen its task or show the brief to the owner. The opposite is written: "The brief goes to the helper, never to the owner"; "do not add work the question did not ask for"; "Keep the helper's intent narrow." No widening/owner-facing clause exists. This is the "nothing asks for owner-facing output" half of S1.

(d) Do the five parts + return contract match what the owner approved (R309, R310) and carry-over (R314)? — VERIFIED.
 - R309 (brief parts) maps 1:1 to the skill's five parts: answer needed / exact scope (files + pinned commit = "files and version") / evidence that could change the answer / what is unknown / depth and stopping point.
 - R310 (helper standard) is present in both files: original source, finding-to-evidence-to-consequence, keep verified facts / reported claims / inferences / assumptions / unknowns apart, say what was not checked, lead with the answer then the support, one hand-back. The owner's "guesses" is rendered as "inferences, assumptions" — a faithful, non-narrowing expansion.
 - R307 (authorization): the artifact is the orchestrator's own helper-briefing method (dispatch-brief), not the private father-facing skill; source-029's reading is honored.
 - R314 (carry over by itself): realized by the always-loaded rule (no `paths:`) naming /dispatch-brief + the helper standard, plus the committed+listed skill; once merged to main a fresh session loads both with no chat-history dependency. This is S3. The producer report states this contingency honestly.

## Acceptance scenarios
 S1 PASS (valid frontmatter; five parts + return contract named; nothing owner-facing).
 S2 PASS (no `paths:` frontmatter; main-session half names /dispatch-brief; helper half states the standard; short — 12 lines, 963B).
 S3 PASS (rule is eager-loaded per the budget tool + my own injected context; skill is listable; no chat-history dependency).
 S4 PASS (demonstrable): the very brief that dispatched me, /root/project/lanes-runtime/owner-docs/session-2026-10-15c/prompt-G3-M0-T198.md, is itself built on the five parts (its headed items 1 "THE ANSWER NEEDED", 2 "SCOPE", 3 "EVIDENCE THAT COULD CHANGE THE ANSWER", 4 "UNKNOWN AND STAYING UNKNOWN", 5 "DEPTH") plus the return contract ("lead with VERDICT ... keep verified facts, inferences and unknowns apart ... END-OF-REPORT"). Each part present; the standard is applied.
 S5 PASS (budget check above).

## Directive binding (advisory to the authoritative DCV pass)
 Packet directive_refs cite D-094 R307, R309, R310, R314. In requirements.json exactly those four carry M0-T198 in `applicability.task_ids`; R308/R311/R312/R313/R315 are bound to D-094-BOOTSTRAP only (chat returns / owner decision / go-ahead — correctly not product requirements on this task). Cited == applicable. The independent directive-compliance-verifier owns the binding verdict in verification.json; I only confirmed the cited/applicable match and that each cited requirement's text is satisfied by the two files as detailed above.

## Modularity
 N/A as a boundary review: both new files are markdown instruction artifacts under .claude/, not handwritten production source. Each is single-responsibility and short (skill 57L; rule 12L). No code module grew. modularity_check not required for this change.

## Findings
 REQUIRED: none.
 ADVISORY 1 (project-control/reports/M0-T198-producer-report.md "How it carries over"): the carry-over property (R314/S3) only takes effect once the branch is merged to main — until then no fresh session loads the rule (and, per PROGRAM_KNOWLEDGE, a mid-session helper whose parent already started inherits the parent's snapshot, not these new files, reaching them only via the brief). The report states this correctly; flagging it so the orchestrator treats merge-to-main as the enabling step, not an optional follow-up. No change to the files needed.

## What I did NOT check / stays UNKNOWN
 - Whether EVERY Claude Code harness/runtime version loads no-`paths:` rules into subagents identically. I established it from this runtime (my injected context) and from the repo tool's documented intent; I did not and cannot prove it for all runtime versions from repository evidence alone. Per the brief this stays UNKNOWN; it does not affect the PASS, because R314 targets fresh later sessions (start-time load from main), which the mechanism and the budget tool support.
 - I did not exercise the skill by dispatching a new helper (read-only); S4 is evidenced by the existing brief that invoked me rather than by a fresh dispatch.
 - I did not run modularity_check (not applicable to markdown instruction files) nor the full CI suite (CI at the accept head is the orchestrator's read per D-090-R639).

END-OF-REPORT
