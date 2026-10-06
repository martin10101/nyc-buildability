# D-090 source-042 (amendment): owner message 93, 2026-10-06 - update the research assessment only (ground-floor height candidate, apartment-size benchmarks, shared-space measurement), define the areas before proposing the apartment-count formula, and create a permanent zoning-rule review register with a standing instruction and a backfill

Captured 2026-10-06 by the orchestrator (Claude Code session 013RaGmCmULdpmjCy58qBeMY, model claude-opus-5-5) from the saved session transcript `~/.claude/projects/-root-project-nyc-buildability/9b6b7b3f-4902-4b4f-b2e0-971a91de749e.jsonl` (line 825, uuid `b2361151-fb96-44b6-88ae-cc6fcdb07172`, 2026-10-06T13:58:22.191Z, a user line). A script copied the raw text; nothing was retyped. Raw-text SHA-256 `d51fe2a007b4ead49b739238c2a013807a6081e2afb336590a86f572651b6abe`. Lines 1 and 13 of the raw text each end with one space; the block below is otherwise byte-identical. Every owner fragment quoted in a requirement row was checked by the script to be an exact substring of the message.

Context: the message arrived while the race-test repair (task M0-T184) was waiting for the second part of its last independent check. Earlier in the session the orchestrator had put nine open choices to the owner, among them proposed starting values of 14 ft for a ground floor with shops, 700 sq ft per apartment and 15 percent shared space. This message answers none of those choices; it corrects how the research behind three of them is described and asks for a revised proposal.

## Owner message 93 (verbatim)

Transcript timestamp 2026-10-06T13:58:22.191Z.

> You can verify this below with the deep resurch agent 
>
> Update the research assessment, not the program or defaults:
>
> - HPD’s Laying the Groundwork, section 3.1, printed page 37, supports 15 ft floor-to-floor as a retail-ground-floor candidate. Distinguish that from its 14 ft 4 in structural clearance and 12 ft unobstructed clearance. Record its limited applicability; it is not a universal legal requirement. Bring the revised candidate to me for approval.
>
> - The 692/712/737 apartment-size figures remain historical benchmarks from one RentCafe/Yardi dataset, not independently confirmed borough averages. Their net-interior measurement convention is unverified. Don’t count articles repeating the same study as independent sources or substitute averages for newly leased apartments as if they meant newly built apartments.
>
> - Don’t describe 15% shared space as an established NYC average. HCR’s 2025 Design Guidelines, section 3.4.1a and Exhibit A, and the 2026 Project Detail Application’s Exhibit D-2 define a program-specific common-space calculation. It uses residential common area divided by dwelling-unit area plus common area on an interior-gross basis. That differs from HPD’s net-unit area definition. Don’t mix those measurements or subtract walls/shared areas twice.
>
> Before proposing the apartment-count formula, state exactly what each area includes and excludes. Then show me the proposed starting values, evidence, uncertainty and how changing them affects the estimated count. Keep this a simplified feasibility estimate, with legal unit limits separate. This research does not approve any default.
>
> Also 
>
> Create a permanent zoning-rule review register that I can later give to a New York City architect or examiner. It should show each rule, how our program applies it, and whether the reviewer considers that application correct.
>
> Use a separate Markdown file with a simple table. Reuse existing rule IDs and evidence rather than creating duplicate records. Include:
> - Rule ID and official law link, with applicable date
> - Where the rule applies and its exceptions
> - Our interpretation in plain English
> - A concrete example: inputs, expected answer and actual program answer
> - Links to the relevant code and tests
> - Revision and date last changed
> - Architect/examiner verdict: Not reviewed / Correct / Incorrect / Needs re-review
> - Reviewer name, date and comments, when provided
>
> Keep automated test results separate from the human verdict. Claude must never mark a rule professionally reviewed just because tests or another AI passed it. A verdict applies only to the version and conditions actually reviewed.
>
> Maintain a short current table with linked details and an append-only history. When a rule’s interpretation, applicability or implementation changes, preserve the old record and flag affected human reviews for re-review. Don’t create duplicate entries when nothing changed.
>
> Add a short standing instruction to the existing main project instruction file: every session that adds or changes zoning-rule behavior must update this register as part of the same change. Keep the detailed register separate; don’t copy or automatically load the whole history into every session.
>
> Backfill the rules already implemented using verifiable evidence. Mark gaps honestly. This is a review record, not a new mandatory professional-signoff stage.
>
> Use stable IDs and structured fields so we can move it into Supabase later. Don’t build the database integration now. Tell me where the register and standing instruction are saved, and show me two sample rows.

## Reading

| Words of the message | Requirement |
|---|---|
| "You can verify this below with the deep resurch agent" | R344 (authorization) |
| "Update the research assessment, not the program or defaults:" | R345 (prohibition) |
| "HPD’s Laying the Groundwork, section 3.1, printed page 37, supports 15 ft floor-to-floor as a retail-ground-floor candidate." | R346 (obligation) |
| "Distinguish that from its 14 ft 4 in structural clearance and 12 ft unobstructed clearance." | R347 (obligation) |
| "Record its limited applicability; it is not a universal legal requirement." | R348 (obligation) |
| "Bring the revised candidate to me for approval." | R349 (return) |
| "The 692/712/737 apartment-size figures remain historical benchmarks from one RentCafe/Yardi dataset, not independently confirmed borough averages." | R350 (obligation) |
| "Their net-interior measurement convention is unverified." | R351 (obligation) |
| "Don’t count articles repeating the same study as independent sources" | R352 (prohibition) |
| "or substitute averages for newly leased apartments as if they meant newly built apartments." | R353 (prohibition) |
| "Don’t describe 15% shared space as an established NYC average." | R354 (prohibition) |
| "HCR’s 2025 Design Guidelines, section 3.4.1a and Exhibit A, and the 2026 Project Detail Application’s Exhibit D-2 define a program-specific common-space calculation." "It uses residential common area divided by dwelling-unit area plus common area on an interior-gross basis." | R355 (obligation) |
| "That differs from HPD’s net-unit area definition." | R356 (obligation) |
| "Don’t mix those measurements or subtract walls/shared areas twice." | R357 (prohibition) |
| "Before proposing the apartment-count formula, state exactly what each area includes and excludes." | R358 (sequencing) |
| "Then show me the proposed starting values, evidence, uncertainty and how changing them affects the estimated count." | R359 (return) |
| "Keep this a simplified feasibility estimate, with legal unit limits separate." | R360 (decision) |
| "This research does not approve any default." | R361 (prohibition) |
| "Create a permanent zoning-rule review register that I can later give to a New York City architect or examiner." "It should show each rule, how our program applies it, and whether the reviewer considers that application correct." | R362 (obligation) |
| "Use a separate Markdown file with a simple table." | R363 (obligation) |
| "Reuse existing rule IDs and evidence rather than creating duplicate records." | R364 (prohibition) |
| "- Rule ID and official law link, with applicable date" | R365 (obligation) |
| "- Where the rule applies and its exceptions" | R366 (obligation) |
| "- Our interpretation in plain English" | R367 (obligation) |
| "- A concrete example: inputs, expected answer and actual program answer" | R368 (obligation) |
| "- Links to the relevant code and tests" | R369 (obligation) |
| "- Revision and date last changed" | R370 (obligation) |
| "- Architect/examiner verdict: Not reviewed / Correct / Incorrect / Needs re-review" | R371 (obligation) |
| "- Reviewer name, date and comments, when provided" | R372 (obligation) |
| "Keep automated test results separate from the human verdict." | R373 (harness) |
| "Claude must never mark a rule professionally reviewed just because tests or another AI passed it." | R374 (prohibition) |
| "A verdict applies only to the version and conditions actually reviewed." | R375 (decision) |
| "Maintain a short current table with linked details and an append-only history." | R376 (obligation) |
| "When a rule’s interpretation, applicability or implementation changes, preserve the old record and flag affected human reviews for re-review." | R377 (obligation) |
| "Don’t create duplicate entries when nothing changed." | R378 (prohibition) |
| "Add a short standing instruction to the existing main project instruction file: every session that adds or changes zoning-rule behavior must update this register as part of the same change." | R379 (obligation) |
| "Keep the detailed register separate; don’t copy or automatically load the whole history into every session." | R380 (prohibition) |
| "Backfill the rules already implemented using verifiable evidence." | R381 (obligation) |
| "Mark gaps honestly." | R382 (obligation) |
| "This is a review record, not a new mandatory professional-signoff stage." | R383 (decision) |
| "Use stable IDs and structured fields so we can move it into Supabase later." | R384 (obligation) |
| "Don’t build the database integration now." | R385 (prohibition) |
| "Tell me where the register and standing instruction are saved, and show me two sample rows." | R386 (return) |

- **The statements about documents are to be checked, not assumed (R344, R346, R355, R356).** The message names HPD's "Laying the Groundwork" (section 3.1, printed page 37), HCR's 2025 Design Guidelines (section 3.4.1a and Exhibit A), the 2026 Project Detail Application (Exhibit D-2) and HPD's net-unit area definition. The research helper reads each at its source. Where a source says something different from the message, the owner is told before the assessment is changed.
- **What "the research assessment" is (R345).** Entries RQ-006, RQ-007 and RQ-008 of `docs/RESEARCH_REQUESTS.md`. Those entries are on a pull request that is not merged yet; the update follows its merge. The program's stated starting height (10 ft, `services/api/app/scenario/three_answers/inputs.py`) and every other value in the program stay as they are.
- **What changes in the orchestrator's earlier proposal (R349, R354, R361).** The 14 ft ground-floor proposal is withdrawn in favour of a revised candidate to be brought for approval. The 15 percent figure is no longer described as anything but a placeholder with a weak basis. No value is approved.
- **Which file is the main instruction file (R379).** `CLAUDE.md` at the repository root, as recorded for R300. A pull request that adds the owner's working guidance to that file is still open; the standing instruction is added after it merges, so the two changes do not collide.
- **Which rule identifiers exist (R364).** The rule files under `services/api/app/rules/rulesets/` carry the identifiers; the captured law text is under `docs/research/zr-snapshots/v1/`. The register points to them.
- **How the register relates to professional review (R374, R383).** The standing rule (ADR-007) is that legal interpretations ship as labelled unreviewed drafts with a link to the law, and professional review is advisory. The register records such a review when one happens. It adds no gate.
- **Points the orchestrator raises with the owner (R329):** none is a conflict. Two limits apply and are kept: the 10,000-token cap on automatically loaded instructions (the standing instruction is one or two lines), and one helper at a time (the research check and the register backfill run one after the other unless the owner allows otherwise).
- **Not claimed by this capture:** none of R344-R386 is done. All 43 rows are pending.
