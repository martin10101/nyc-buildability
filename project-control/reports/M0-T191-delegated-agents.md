# M0-T191 - a delegated agent inherits its parent session's start-time instructions (D-093 correction)

Recorded 2026-10-11 by the orchestrator (session 01TpXJN7, transcript `33a4b56e-2b0e-47dd-9b18-d09cf4097f56`, started 01:25 UTC, before the research rule existed). Evidence is read from Claude Code 2.1.288 transcripts, which record each loaded instruction set as an `instructions` entry. Transcripts live under `~/.claude/projects/-root-project-nyc-buildability/` on the build server (private).

## What was observed

The D-093 files reached the main checkout at 02:58:28 UTC (fast-forward to main `9e107bf3`; `CLAUDE.md` 14,562 characters (14,609 bytes) with principle 21 [ORCH-CORRECTED per G3 advisory 2026-10-11 03:12]; the new rule `.claude/rules/research-and-verification.md`).

| Session | Started | Loaded instruction files (characters as the transcript records them) |
|---|---|---|
| fresh print-mode session `2f0aa039-456c-46e5-8c13-ac7d0eb57a10` from `/root/project/nyc-buildability` | 02:58:37 | `CLAUDE.md` (14561), expansion hold (4027), `CODING_RULES.md` (4537), **`research-and-verification.md` (2452)**, `PROGRAM_KNOWLEDGE.md` (17019), memory index (8289) |
| subagent `agent-a1200433925ba8efc` (code-reviewer) of the orchestrator session | 02:58:48 | `CLAUDE.md` (14177), expansion hold (4027), `CODING_RULES.md` (4537), `PROGRAM_KNOWLEDGE.md` (17012), memory index (8289) - no research rule |
| subagent `agent-a7180378d084bf28b` (backend-engineer, M5-T157 builder) of the orchestrator session | 03:05:24 | the same pre-merge set as the row above - no research rule |

Asked from its loaded instructions only, the 02:58:48 subagent answered that no rule titled "Research and verification - required project workflow" was in its instructions. The sizes 14177 and 17012 are the pre-merge `CLAUDE.md` and `PROGRAM_KNOWLEDGE.md`; the files on disk were already the merged ones.

## Reading

A subagent inherits the instruction set its parent session loaded when that session started; it does not re-read the instruction files from disk. A session started after a rule change loads the new rule, and its subagents inherit that. In a session started before a rule change, the rule reaches delegated agents only through the brief. (Not tested: whether a compaction of the parent session refreshes the set its later subagents inherit.)

## Correction

`project-control/reports/M0-T190-verification-sessions.md` (accepted with M0-T190; not edited) says in its section 4: "So once the main checkout holds the D-093 files, every delegated agent loads the rule." That holds only for delegated agents of sessions started after the files exist. The procedure now says so (`docs/RESEARCH_AND_VERIFICATION.md` sections 6 and 9), and `.claude/rules/PROGRAM_KNOWLEDGE.md` carries a pointer. The M5-T157 builder brief carried the D-093 dispatch clause for this reason.
