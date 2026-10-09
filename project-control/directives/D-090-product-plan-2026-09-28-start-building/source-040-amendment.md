# D-090 source-040 (amendment): owner message 89, 2026-10-06 - working guidance to be recorded in the main instruction file and referenced from the handoff (goal, work efficiently, agents, accuracy, continuity and updates; existing restrictions preserved)

Captured 2026-10-06 by the orchestrator (Claude Code session 013RaGmCmULdpmjCy58qBeMY, model claude-opus-5-5) from the saved session transcript `~/.claude/projects/-root-project-nyc-buildability/dcba4eaf-6be8-40f7-9161-b367a7eb57ac.jsonl` (line 1304, uuid `c07c7f3e-4c1c-42fc-a46d-2c1eff4c210e`, 2026-10-06T07:26:49.469Z). The message arrived while the orchestrator was working, so the transcript stores it as a queued-command attachment, not as a user line. A script copied the raw text; nothing was retyped. The raw text begins with two newline characters; the block below leaves those out and is otherwise byte-identical. Raw-text SHA-256 `ca3a085cd418984faf38b69e21902ae5eacf3f792a3b017537257f7f063d5476`. Every owner fragment quoted in a requirement row was checked by the script to be an exact substring of the message.

The guidance itself, from the line `GOAL` to the end of the message, has SHA-256 `185ed3a4c1baa63c3994942e84608e30fcc92cbdede6aa578d8f461498cf5aeb` (trailing newlines removed). That is the text to appear unchanged in the main instruction file.

Context: five of the ten waiting changes had merged; the research helper had reported on the starting values.

## Owner message 89 (verbatim)

Transcript timestamp 2026-10-06T07:26:49.469Z.

> Record the following working guidance in the existing main instruction file used by future sessions, and reference it from the handoff. Verify the correct file rather than creating a duplicate “main info” file. Follow the normal review process.
>
> GOAL
> Deliver the full feasibility report comparable to my sample, with reliable numbers. Keep all promised sections and options unless I explicitly approve removing one. No detailed apartment layouts or permit-ready plans. Intermediate milestones are progress, not full completion.
>
> WORK EFFICIENTLY
> - Finish one implementation piece at a time and obtain independent review.
> - Reuse shared calculations across scenarios, screens, drawings and PDF.
> - Reach a working address-to-results-to-PDF path early, then expand it into the full report. Don’t abandon the remaining scope.
> - Research the next necessary decision, bring me a recommendation with its basis, then move forward once it is settled.
> - Avoid repeated planning and wording changes unless they resolve a real issue or record a necessary decision.
> - Run heavy test suites one at a time.
>
> AGENTS
> Stay within my existing agent limits. Where permitted, separate building, independent review and preparation of the next research question. Do not add a swarm or increase concurrency without my approval. Parallel work must be independent and must not collide on shared files or tests.
>
> ACCURACY
> Use independently worked, source-backed examples to check interpretation. Matching the program’s own saved output is not proof of correctness. Keep legal limits separate from practical estimates. Make design assumptions visible and editable. Missing facts stay unknown or support clearly conditional scenarios; unfinished promised features remain work owed.
>
> CONTINUITY AND UPDATES
> Keep a concise record of what is built, connected, tested, merged and still missing. Each handoff must identify the exact next step, blockers and pending owner decisions. Report meaningful progress in plain English. Estimate remaining time from observed delivery, not guessed agent speed.
>
> Preserve all existing security, production and merge restrictions. This guidance does not authorize new spending, access changes or additional agents. Point out any conflict before changing those restrictions.

## Reading

| Words of the message | Requirement |
|---|---|
| "Record the following working guidance in the existing main instruction file used by future sessions" | R300 (obligation) |
| "and reference it from the handoff" | R301 (obligation) |
| "Verify the correct file rather than creating a duplicate “main info” file." | R302 (prohibition) |
| "Follow the normal review process." | R303 (obligation) |
| "Deliver the full feasibility report comparable to my sample, with reliable numbers." | R304 (decision) |
| "Keep all promised sections and options unless I explicitly approve removing one." | R305 (prohibition) |
| "No detailed apartment layouts or permit-ready plans." | R306 (prohibition) |
| "Intermediate milestones are progress, not full completion." | R307 (decision) |
| "Finish one implementation piece at a time and obtain independent review." | R308 (obligation) |
| "Reuse shared calculations across scenarios, screens, drawings and PDF." | R309 (obligation) |
| "Reach a working address-to-results-to-PDF path early, then expand it into the full report." "Don’t abandon the remaining scope." | R310 (sequencing) |
| "Research the next necessary decision, bring me a recommendation with its basis, then move forward once it is settled." | R311 (obligation) |
| "Avoid repeated planning and wording changes unless they resolve a real issue or record a necessary decision." | R312 (prohibition) |
| "Run heavy test suites one at a time." | R313 (sequencing) |
| "Stay within my existing agent limits." | R314 (hold) |
| "Where permitted, separate building, independent review and preparation of the next research question." | R315 (obligation) |
| "Do not add a swarm or increase concurrency without my approval." | R316 (prohibition) |
| "Parallel work must be independent and must not collide on shared files or tests." | R317 (prohibition) |
| "Use independently worked, source-backed examples to check interpretation." | R318 (obligation) |
| "Matching the program’s own saved output is not proof of correctness." | R319 (evidence) |
| "Keep legal limits separate from practical estimates." | R320 (obligation) |
| "Make design assumptions visible and editable." | R321 (obligation) |
| "Missing facts stay unknown or support clearly conditional scenarios; unfinished promised features remain work owed." | R322 (obligation) |
| "Keep a concise record of what is built, connected, tested, merged and still missing." | R323 (obligation) |
| "Each handoff must identify the exact next step, blockers and pending owner decisions." | R324 (obligation) |
| "Report meaningful progress in plain English." | R325 (obligation) |
| "Estimate remaining time from observed delivery, not guessed agent speed." | R326 (obligation) |
| "Preserve all existing security, production and merge restrictions." | R327 (hold) |
| "This guidance does not authorize new spending, access changes or additional agents." | R328 (prohibition) |
| "Point out any conflict before changing those restrictions." | R329 (return) |

- **Which file (R300, R302):** `CLAUDE.md` at the repository root is the project's instruction file that every session loads first; `docs/SESSION_HANDOFF.md` is orientation only and `.claude/rules/PROGRAM_KNOWLEDGE.md` holds pointers. No other "main" instruction file exists.
- **A limit that applies to the change:** the files loaded automatically at the start of every session are capped at 10,000 tokens (owner, D-067-R003; the cap is not raised without a new owner authorization). They stand at about 9,896. The guidance is about 515 tokens. Room is made by moving loop-only and Windows-only notes from `.claude/rules/PROGRAM_KNOWLEDGE.md` to the second-tier file `docs/WORKING_KNOWLEDGE.md`, unchanged, as that file's own rule prescribes; nothing is deleted and the cap is not raised.
- **Points the orchestrator raises with the owner (R329):** (1) the eight-step order (R289 to R296) puts the PDF at step 7, and this guidance asks for an early address-to-results-to-PDF path; read together as a first thin PDF soon after step 4 (R310). (2) "Separate building, independent review and preparation of the next research question" is read within the recorded limit of one helper at a time (R315); running them at once would need the owner's approval.
- **Not claimed by this capture:** none of R300-R329 is done. All 30 rows are pending.
