# D-090 source-033 (amendment): owner message 77, 2026-10-06 - a correction to the work order: make it consistent before building; every known gap corrected and tested or shown "not known"; no whole-lot 100% coverage until the geometry supports it; settle the two area figures first; missing inputs stay unanswered; a saved result is not proof

Captured 2026-10-06 by the orchestrator (Claude Code session 013RaGmCmULdpmjCy58qBeMY, model claude-opus-5-5) from the saved session transcript `~/.claude/projects/-root-project-nyc-buildability/50db7f46-a38f-40f0-9883-93949ec062f6.jsonl` (line 898, uuid `39d8ce4c-573e-4553-821b-c1cbb8aa31c3`, 2026-10-06T03:22:39.848Z, a user turn). A script copied the raw text; nothing was retyped; it is complete and byte-identical to the transcript except for the blockquote prefix. Raw-text SHA-256 `6e46b7566945060d45c0d909aff007c6fcfd009f598e30a9e6237ec770349f54`. Every owner fragment quoted in a requirement row was checked by the script to be an exact substring of the message. Message numbers continue from source-032 (message 76).

This record is on the same branch as source-032 and the work order it corrects (PR #445), stacked on the source-031 record (PR #442).

Context: the orchestrator had reported that the work order for the first R6B results connection was ready and audited (PR #445, head `4175a09b841966b47c953d6ca7982aee71a067ea`). The message reads as the owner's reviewer's check of that work order, pasted by the owner: "Send Claude this clarification:" is addressed to the owner, and the paragraph after it is the clarification.

## Owner message 77 (verbatim)

Transcript timestamp 2026-10-06T03:22:39.848Z.

> I checked [the actual work order](https://github.com/martin10101/nyc-buildability/pull/445). It identifies the gaps, but some planned tests still require the old answers. That could put an uncertain result onto the new screen.
>
> Send Claude this clarification:
>
> Before building, make the work order consistent: every known gap must either be corrected and tested, or the affected result must show “not known.” Don’t require 100% coverage for the entire lot until the geometry supports it. Resolve how the two area figures are used before calculating from them. Let missing inputs stay unanswered. Matching an old saved result is not proof that it is correct. Keep this within simplified feasibility.

## Reading

| Words of the message | Requirement |
|---|---|
| "I checked [the actual work order](https://github.com/martin10101/nyc-buildability/pull/445)." "Send Claude this clarification:" | context and a forwarding line (no row) |
| "some planned tests still require the old answers." "That could put an uncertain result onto the new screen." | R235 (obligation) |
| "Before building, make the work order consistent" | R236 (sequencing) |
| "every known gap must either be corrected and tested, or the affected result must show “not known.”" | R237 (obligation) |
| "Don’t require 100% coverage for the entire lot until the geometry supports it." | R238 (prohibition) |
| "Resolve how the two area figures are used before calculating from them." | R239 (sequencing) |
| "Let missing inputs stay unanswered." | R240 (obligation) |
| "Matching an old saved result is not proof that it is correct." | R241 (evidence) |
| "Keep this within simplified feasibility." | R242 (decision) |

- **What was wrong in the work order (the orchestrator's own reading of the finding, not the sender's wording):** (1) planned test T3 required the route's answer to equal the saved journey result, which contains values the same document lists as uncertain (whole-lot corner coverage, a full-lot floor plate, a whole-lot rear-yard waiver); (2) planned tests T4 and T5 and table A row L5 required 100 percent coverage for a whole corner lot; (3) planned test W-5 read values on the screen from that saved result; (4) open point D2 forced the user to answer every input or get no numbers at all; (5) the two lot-area figures were only to be printed side by side, with no rule for which one a calculation uses; (6) findings F1 to F6 were listed with "none is fixed here" and no rule for what the screen shows meanwhile.
- **Orchestrator's readings:** "corrected and tested, or ... not known" leaves no third state such as a number with a caveat. "Until the geometry supports it" means a check of the lot's shape against the corner rule, not an assumption. "Missing inputs stay unanswered" replaces the earlier plan to refuse the whole request.
- **Not claimed by this capture:** none of R235-R242 is done. All 8 rows are pending.
