# D-086 source-001 — owner directive (verbatim), 2026-09-24, interactive chat

## Context

On 2026-09-23 the owner complained about the UI (captured verbatim below as the grounding
complaint), the orchestrator explained why the UI grew text-heavy and offered to record the
feedback and start a design-cleanup plan, and the owner commissioned a separate
assessment-only session using the orchestrator's prompt. On 2026-09-24 the owner delivered
that session's finished assessment and its summary (verbatim below).

## Grounding complaint verbatim (owner, 2026-09-23)

> Give me a detailed understanding about where things are standing at the moment, what you
> built so far, and also I want to understand why the UI looks so crowded and doesn't look
> clean. It's all about uh, warnings for the client and it's just, when I look at it, I get
> so confused about what things are going on. It looks really confusing. It constantly
> keeps telling uh, where it can find things instead of like being clean, organized, you
> know, structured. Instead, the client needs to scroll and look and this and that. It's
> just very unclean and a lot of talking. It keeps talking, it keeps saying things. And
> instead of like talking, it should be more visually explanatory. Over here, it's like
> you gotta read and read and read and read.

## Owner delivery message verbatim (2026-09-24; the auditor-session summary the owner passed through)

> I turned your complaint into a **detailed redesign brief the orchestrator can use to plan
> the work.**
>
> My main finding: **the code supports your complaint.** Individual components each add
> their own warnings, explanations, and source notes. When assembled, the screen becomes a
> stack of explanations with too little distinction between the main answer and supporting
> detail.
>
> The MD contains five things:
>
> 1. **A screen-by-screen inventory.** I reviewed 97 UI source files, plus supporting code,
>    tests, and project documents. For each text block, warning, label, and disclosure, I
>    recorded where it appears and why it exists.
>
> 2. **A decision about what happens to that text.** Each item is classified as meaning
>    that must remain, something that can become a compact visual state or expandable
>    detail, or redundant wording that can be removed once its meaning is preserved
>    elsewhere. I distinguished actual product requirements from tests that simply lock
>    today's wording.
>
> 3. **Specific redesign directions.** For example:
>
>    | Screen            | Proposed direction                                                  |
>    | ----------------- | ------------------------------------------------------------------- |
>    | Property results  | Map beside a compact table of FAR, height, yards, and coverage      |
>    | Warnings          | Short, specific states attached to the affected result             |
>    | Sources           | Consistent **Source / Why?** controls opening the relevant evidence |
>    | Existing building | Collapsed section with a clear show/hide control                    |
>    | Condo records     | Entered, billing, and base-lot relationships shown in a table       |
>    | Proposal editor   | Clear drawing modes, organized inputs, and compact check results    |
>
> 4. **Problems that need verification before polishing.** Two significant examples:
>    editing a proposal may leave an older check result displayed, and the editor starts
>    with example values that may look property-specific. These are code-based findings
>    awaiting browser reproduction.
>
> 5. **A phased implementation plan.** It specifies the order of work, what each phase
>    should produce, and what reviewers must check—including preservation of disclosures,
>    mobile behavior, accessibility, and printed reports.
>
> The MD contains written layout specifications and assessment findings. **The actual
> interface has not been changed.** Sections **2, 12, 13, and 14** give you the findings,
> design direction, risks, and plan without reading the entire inventory.
> "C:\Users\MLFLL\Downloads\UI_DEEP_DIVE_ASSESSMENT.md"

## The delivered artifact

`docs/UI_DEEP_DIVE_ASSESSMENT.md` — copied byte-exact from the owner's named path in the
same commit as this capture; sha256
`c6d1b25779c2dd3fb4699d6a99ca50d9695d82f7afc05986fe58de5cf8504b84`; 1450 lines, 16
sections. The assessment states its own boundary plainly (§14): "These are assessment
recommendations, not contracted tasks or release authorization" and "Do not launch the old
19-task pack from this plan."
