# D-090 source-039 (amendment): owner message 88, 2026-10-06 - the order of the work in eight steps; research answers the next building decision; build and test instead of rewriting the plan; the temporary security exception is removed after October 7, 10:09 a.m. New York time

Captured 2026-10-06 by the orchestrator (Claude Code session 013RaGmCmULdpmjCy58qBeMY, model claude-opus-5-5) from the saved session transcript `~/.claude/projects/-root-project-nyc-buildability/dcba4eaf-6be8-40f7-9161-b367a7eb57ac.jsonl` (line 1166, uuid `6d3def5f-5a0f-4775-89ab-3790625f5c30`, 2026-10-06T07:12:50.785Z, a user turn). A script copied the raw text; nothing was retyped; it is complete and byte-identical to the transcript except for the blockquote prefix. Raw-text SHA-256 `78acdd2f9b804dfb9be2f9cd290e37803b1f6a03cdab719b4b3ad669543d7fb6`. Every owner fragment quoted in a requirement row was checked by the script to be an exact substring of the message.

Context: the one-time dependency update had merged (D-092, task M0-T182) and three of the ten waiting changes had merged after it. The message reads as the owner's reviewer's advice on the order of the work, addressed to the owner ("Have Claude recommend starting values with reasons for you to approve") and sent on by the owner.

## Owner message 88 (verbatim)

Transcript timestamp 2026-10-06T07:12:50.785Z.

> I’d keep this order:
>
> 1. Finish the waiting merges, one at a time, with fresh tests and independent review. The security update is now merged.
> 2. Settle the report choices. Have Claude recommend starting values with reasons for you to approve. Keep design assumptions separate from facts and legal rules.
> 3. Check the R6B answers. Resolve missing rules and conflicting inputs, and save independently calculated examples to test against.
> 4. Connect one option to the screen. Prove that changing inputs updates every affected result correctly.
> 5. Add floors, simple building shapes and realistic apartment estimates, clearly separated from legal maximums.
> 6. Build the remaining promised development options and their comparison, one at a time.
> 7. Assemble the full report and PDF, including the agreed supporting sections.
> 8. Test the complete journey against the reference examples and inspect the actual PDF. Finish the agreed R6B coverage before moving to the next district.
>
> Research should answer the next building decision. Once the necessary decision is settled, build and test that piece rather than endlessly rewriting the plan.
>
> One cleanup must also stay on the list: remove the temporary security exception after October 7 at 10:09 a.m. New York time.

## Reading

| Words of the message | Requirement |
|---|---|
| "I’d keep this order:" "1. Finish the waiting merges, one at a time, with fresh tests and independent review." "The security update is now merged." | R289 (sequencing) |
| "2. Settle the report choices." "Have Claude recommend starting values with reasons for you to approve." "Keep design assumptions separate from facts and legal rules." | R290 (sequencing) |
| "3. Check the R6B answers." "Resolve missing rules and conflicting inputs, and save independently calculated examples to test against." | R291 (sequencing) |
| "4. Connect one option to the screen." "Prove that changing inputs updates every affected result correctly." | R292 (sequencing) |
| "5. Add floors, simple building shapes and realistic apartment estimates, clearly separated from legal maximums." | R293 (sequencing) |
| "6. Build the remaining promised development options and their comparison, one at a time." | R294 (sequencing) |
| "7. Assemble the full report and PDF, including the agreed supporting sections." | R295 (sequencing) |
| "8. Test the complete journey against the reference examples and inspect the actual PDF." "Finish the agreed R6B coverage before moving to the next district." | R296 (sequencing) |
| "Research should answer the next building decision." | R297 (obligation) |
| "Once the necessary decision is settled, build and test that piece rather than endlessly rewriting the plan." | R298 (prohibition) |
| "One cleanup must also stay on the list: remove the temporary security exception after October 7 at 10:09 a.m. New York time." | R299 (obligation) |

- **Relation to earlier rows:** the steps restate, in one order, what R213 (results, then report, then PDF), R250 (one piece at a time), R256 (visible, editable starting values), R206 and R209 (finish a district before the next) and R284 already require. The new points are: the report choices are settled before the R6B checks (R290); research serves the next building decision (R297); no further plan rewriting once a decision is settled (R298); the clean-up stays listed (R299).
- **Not claimed by this capture:** none of R289-R299 is done. All 11 rows are pending.
