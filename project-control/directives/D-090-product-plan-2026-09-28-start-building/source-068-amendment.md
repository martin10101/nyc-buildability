# D-090 source-068 (amendment): the owner's second message of the session after handoff seq 152, 2026-10-09 - the first building option compared, step by step, with an independently worked example; the zoning-rule review register kept current for every rule and calculation, with what each detail page shows; legal requirements told apart from design assumptions; a human verdict only from a named human reviewer

Captured 2026-10-09 by the orchestrator (Claude Code session 013RaGmCmULdpmjCy58qBeMY, model claude-opus-5-5). A script copied the raw text from the saved session transcript under `~/.claude/projects/-root-project-nyc-buildability/`; nothing was retyped, and every quoted fragment below was cut out of the message by the script.

| What | Transcript | Line | Entry uuid | Timestamp | Stored as | Raw-text SHA-256 |
|---|---|---|---|---|---|---|
| the message | `f3a4a686-fb58-4cf9-9dc1-56dcc8d8fba7.jsonl` | 688 | none (a queue entry carries no uuid) | 2026-10-09T05:36:08.680Z | queue entry holding the typed text | `fe35842e15896f55258ca229ad8bc8c76969219cbdc592ccc2fd3d6e9f2471b1` |
| the message | `f3a4a686-fb58-4cf9-9dc1-56dcc8d8fba7.jsonl` | 690 | `54276208-50c7-46ba-ba00-b4b8d90ff9f4` | 2026-10-09T05:36:08.797Z | user line holding the message as delivered (the same text) | `fe35842e15896f55258ca229ad8bc8c76969219cbdc592ccc2fd3d6e9f2471b1` |

Context. The message arrived while pull request 480 (task M5-T144, accepted) was at its independent pre-merge check and the two independent readings of step P6 (the hand-worked example of a first building option) had just come in. Pull request 480 was merged afterwards as it stood (`65c60679`): it was complete, reviewed and accepted before the message, and the message says to continue the current work. This capture is the first commit of the next branch; nothing was done on the strength of the message before it. The message carries no number here (see source-067).

## Owner message (verbatim)

Transcript timestamp 2026-10-09T05:36:08.680Z. 1899 characters; the digest is of the raw text.

> Continue the current work, with these requirements included in the relevant tasks.
>
> For the first building option, compare an independently worked example with the actual program output through the complete calculation: property inputs, footprint, each floor’s area and height, total floor area, applicable legal unit limit, and separate preliminary apartment estimate. Reuse completed research and identify any remaining disagreement or missing fact.
>
> Keep "docs/zoning-rule-review/REGISTER.md" and its linked detail pages current whenever a rule or calculation changes. Update the register’s source data and regenerate the table through the existing process.
>
> Every rule, formula, exception and design assumption affecting a reported result must be traceable from that register. Each relevant detail page should show:
>
> - Official source, section and version/date, including applicability and exceptions.
> - The program’s interpretation and what is implemented versus planned.
> - Inputs, units, measurement basis, formula and rounding.
> - A worked example, expected answer, actual program answer and tested revision.
> - Code and test links, unresolved questions and limitations.
>
> Clearly distinguish legal requirements from chosen design assumptions. For example, the apartment-size and efficiency assumptions must remain labelled as preliminary assumptions.
>
> Include calculations that combine several rules, even when they are not separate rule files. Link their existing calculation or measurement records from the relevant review pages. Make any remaining coverage gap explicit.
>
> Only a named human reviewer’s actual decision can establish a human verdict. Preserve previous decisions and separately identify whether they apply after a change.
>
> Make these updates part of the existing implementation and review work. Keep the one-time workflow audit finished and continue toward the building option.

## Reading

| Words of the message | Requirement |
|---|---|
| "Continue the current work, with these requirements included in the relevant tasks." | R685 (authorization) |
| "Continue the current work, with these requirements included in the relevant tasks." | R686 (obligation) |
| "For the first building option, compare an independently worked example with the actual program output through the complete calculation: property inputs, footprint, each floor’s area and height, total floor area, applicable legal unit limit, and separate preliminary apartment estimate." | R687 (obligation) |
| "For the first building option, compare an independently worked example with the actual program output through the complete calculation: property inputs, footprint, each floor’s area and height, total floor area, applicable legal unit limit, and separate preliminary apartment estimate." | R688 (obligation) |
| "Reuse completed research and identify any remaining disagreement or missing fact." | R689 (obligation) |
| "Reuse completed research and identify any remaining disagreement or missing fact." | R690 (obligation) |
| "Keep "docs/zoning-rule-review/REGISTER.md" and its linked detail pages current whenever a rule or calculation changes." | R691 (obligation) |
| "Update the register’s source data and regenerate the table through the existing process." | R692 (obligation) |
| "Every rule, formula, exception and design assumption affecting a reported result must be traceable from that register." | R693 (obligation) |
| "Each relevant detail page should show:" "Official source, section and version/date, including applicability and exceptions." | R694 (obligation) |
| "Each relevant detail page should show:" "The program’s interpretation and what is implemented versus planned." | R695 (obligation) |
| "Each relevant detail page should show:" "Inputs, units, measurement basis, formula and rounding." | R696 (obligation) |
| "Each relevant detail page should show:" "A worked example, expected answer, actual program answer and tested revision." | R697 (obligation) |
| "Each relevant detail page should show:" "Code and test links, unresolved questions and limitations." | R698 (obligation) |
| "Clearly distinguish legal requirements from chosen design assumptions." | R699 (obligation) |
| "For example, the apartment-size and efficiency assumptions must remain labelled as preliminary assumptions." | R700 (prohibition) |
| "Include calculations that combine several rules, even when they are not separate rule files." | R701 (obligation) |
| "Link their existing calculation or measurement records from the relevant review pages." | R702 (obligation) |
| "Make any remaining coverage gap explicit." | R703 (obligation) |
| "Only a named human reviewer’s actual decision can establish a human verdict." | R704 (prohibition) |
| "Preserve previous decisions and separately identify whether they apply after a change." | R705 (obligation) |
| "Preserve previous decisions and separately identify whether they apply after a change." | R706 (obligation) |
| "Make these updates part of the existing implementation and review work." | R707 (obligation) |
| "Keep the one-time workflow audit finished and continue toward the building option." | R708 (prohibition) |
| "Keep the one-time workflow audit finished and continue toward the building option." | R709 (sequencing) |

- **Go on, with these requirements in the tasks they concern (R685, R686, R707).**
- **The first building option (R687 to R690):** an independently worked example beside the program's actual output through the complete calculation, six steps; completed research reused; every disagreement and missing fact named.
- **The register (R691 to R693, R701 to R703):** current whenever a rule or a calculation changes; changed in its source data and regenerated by the existing process; everything behind a reported result traceable from it; combined calculations included; their existing records linked; every remaining gap stated.
- **What each relevant detail page shows (R694 to R698).**
- **Legal requirements apart from design assumptions (R699, R700).**
- **Human verdicts (R704 to R706):** only a named human reviewer's own decision; earlier decisions kept; whether they still apply shown apart.
- **The audit stays finished; on toward the building option (R708, R709).**
- **Sentences of the message quoted by no row:** none.
- **Not claimed by this capture:** no row is verified; all twenty-five are pending. This capture changes no product file, no test, no register file and no instruction file.
- **What the register is today, read before this capture (for the tasks that follow):** 23 entries, one per rule-definition file; its guide lists zoning behaviour in code that has no entry yet, the scenario engine among them. Task M5-T144, merged just before this capture, changed that engine's decision for the rear yard and its geometry block; it moved no register entry because none covers that code. That is a coverage gap in the sense of row R703, to be stated in the register by the first task that takes these rows.
