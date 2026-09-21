# D-083 source 001 — owner message, interactive chat, 2026-09-21 (verbatim)

## Owner message (verbatim)

> Here's everything from tonight, in plain English.
>
> What got built
>
> 1. Better condo explanations (finished)
> When you look up a condo, the screen now explains itself in plain words: which lot the city bills, which piece of land the building actually sits on, and why we analyzed the one we did. Screen-reader announcements now say exactly what's shown on screen — no more mismatch. Small bug fixed too: zoning names with a slash (like a mixed district) now display correctly.
>
> 2. The "building site" record system (finished, switched off for now)
> For condos that sit on several lots, a professional can now record "these parcels together are the real building site" — with a name attached, and the ability to replace or withdraw that record later. This is deliberately switched off in the live product until sign-in and protection are added, because it's a legally meaningful record.
>
> 3. Drawing a building on the map — part 1 (finished)
> In the proposal editor, an architect can sketch a building outline as points over the lot map. The system converts those map positions into the official city measuring system that all the real calculations use. Important honesty rule: the conversion tells you how accurate it is, and if it can't be confident, it refuses rather than guessing. The converted shape lands in the numbers table exactly as if you'd typed it — and typing stays an option.
>
> 4. The "maximum allowed building" calculator (finished, not on screen yet)
> This was your big ask: before the designer draws anything, the system works out the biggest building the rules allow — height, footprint, floor area — and for every number it names the exact rule that sets the limit. Where a rule can't be computed for that lot, it says "couldn't check" honestly instead of guessing. And it proves its own answer: it feeds its computed maximum back through the same checker that judges proposals, and the answer must pass. Pure calculation code — no AI in the math.
>
> 5. Security tightening (finished)
> Reviewers found subtle ways a nosy user could learn about other people's records from tiny differences in error responses. All closed — every wrong guess now looks exactly the same.
>
> 6. Clicking on the map — part 2 (in final review right now)
> The natural version of drawing: click the map to place a corner, click a corner to select it, click again to move it, delete it. It feeds the exact same pipeline as typing. Also fixed from review: if you adopt a smaller shape, wall entries pointing at deleted corners are cleaned up and it tells you which ones were removed.
>
> 7. Extra safety tests (the loops are writing these now)
> More tests proving the maximum-calculator fails safely, and one last wording cleanup.
>
> How you can test it today
>
> Open the product the same way as your earlier walkthrough (with the preview switch in the address). Then:
>
> Condo check: look up a condo address. Read the explanation of billing lot vs. land — it should make sense in plain words now.
>
> Proposal editor: open a property → Architect workspace → Proposal editor. Type a building outline, add floors, run the check — you'll see pass/fail with the rules named. Above the table you'll see the new drawing section.
>
> One honest limitation: the Convert button in the drawing section will say conversion isn't available — that's on purpose. The converter, the building-site records, and the maximum calculator are all built and fully reviewed, but deliberately not switched on for real users until the sign-in/protection step. Switching them on is its own planned task that will come to you for approval.
>
>
> The map-clicking and the on-screen "maximum allowed" answer arrive after their reviews finish and the next deploy. Nothing needs you tonight — it's all saved, and the next session picks up automatically from the handoff.
>
> Is this the right approach? If you were an architect, would you use it like this, or you would say this is not how I want this?Worked for 2m 38s
>
> Yes—the overall direction is right. I would see value in this as a tool for preliminary zoning analysis and testing design options. But I would want the experience organized around getting an answer quickly, and I would be careful about the claim "maximum allowed building."
>
> Based on the update, the team is building useful foundations. The remaining question is whether those foundations produce a smooth, dependable experience for the architect.
>
> 1. I would want to understand the property before drawing anything.
>
> Imagine an architect receives an address from a client asking whether a development is worth pursuing. The first useful experience should be:
>
> 1. Enter the address and confirm the correct site on the map.
>
>
> 2. See the supported development limits: floor area, height, yards, setbacks, and coverage.
>
>
> 3. See the assumptions and any specific unresolved conditions.
>
>
> 4. Choose to test a design.
>
>
> 5. Save or share the analysis.
>
>
>
> The architect should not have to enter a building outline simply to discover the site's basic limits.
>
> That general sequence fits existing feasibility workflows. For example, TestFit describes loading site constraints, developing alternatives, editing them, and exporting the work into design tools. That supports the approach, although it does not establish the accuracy of your implementation. TestFit's workflow
>
> 2. Drawing on the map is useful, provided it feels like a design tool.
>
> Clicking corners is a sensible beginning. I would also want to enter an exact dimension, adjust a wall's distance from a boundary, undo a change, and see measurements while editing. Coordinate tables can remain available as an advanced option.
>
> Coordinate conversion should normally happen automatically. An architect should be thinking about wall positions and dimensions, without needing to understand the city's coordinate system.
>
> Also, a precise conversion does not make a roughly clicked point precise. The software must distinguish a preliminary sketch from geometry supported by a survey or confirmed measurements.
>
> For more developed designs, I would eventually want a practical import route. That could start with one supported CAD format or a scaled PDF that the architect aligns and traces. It does not need to understand every drawing automatically to be useful.
>
> 3. "Maximum allowed building" needs a much tighter definition.
>
> This is the most important qualification in the update.
>
> Maximum height, maximum footprint, and maximum floor area are different limits. They cannot necessarily all be reached simultaneously.
>
> For a purely hypothetical example, suppose a site has a six-storey height allowance, a 2,000-square-foot footprint limit, and a 9,000-square-foot zoning floor-area limit. Six full floors of that footprint would total 12,000 square feet. The separate ceilings do not describe one permitted building.
>
> The program should clearly distinguish:
>
> A regulatory limit: a ceiling established by a rule.
>
> A generated building option: a particular shape that passes the implemented checks.
>
> A demonstrated maximum: an optimum established within a stated set of rules, assumptions, and supported building configurations.
>
>
> Until the third claim is established, I would prefer wording such as "Preliminary development limits" and "Generated building option."
>
> 4. Feeding the generated building back into the checker is good engineering—but it does not prove everything.
>
> It establishes that the generator and checker agree. It does not independently establish that the rules are complete or correctly interpreted. Both could share the same missing exception.
>
> It also does not prove that a larger compliant design is impossible.
>
> I would want independently prepared examples, checked against official sources and reviewed by an architect, to test those claims.
>
> And where a necessary rule cannot be evaluated, the overall result must remain incomplete. The architect can still receive useful supported limits, but should not receive an unrestricted green "pass."
>
> 5. Checking my design must tell me what to change.
>
> A pass/fail result with a rule citation is a useful foundation. The more valuable experience is identifying the affected wall or floor and explaining the actual discrepancy.
>
> For example, an illustrative message could say:
>
> > "This rear wall extends three feet into the required yard. The affected area is highlighted."
>
>
>
> The architect can then adjust the design and see the consequences.
>
> The editor also needs to represent the design being checked: different upper-floor footprints, setbacks, floor heights, and any existing building being retained. A ground-floor outline alone cannot describe those conditions.
>
> 6. The condo and building-site work is necessary, but the terminology matters.
>
> Clear explanations of billing lots and underlying land are useful. Recording who supplied a site definition, with supporting documents and revision history, is also sensible.
>
> However, grouping parcels in your software does not itself establish their legal treatment as one zoning lot. NYC's definition expressly allows zoning lots to differ from tax lots and sets conditions for their establishment. NYC zoning-lot definition
>
> The interface should identify whether the site boundary is an official mapped record, a professional's documented assertion, or a proposed scenario. If that record changes, existing analyses should retain their original basis and clearly indicate when a new calculation is needed.
>
> 7. Keeping protected features disabled is reasonable; the next release needs a complete usable path.
>
> I support protecting professional records before enabling them. But I would ask the engineer to explain why the coordinate converter and preliminary calculator depend on the same sign-in milestone. They may have legitimate shared dependencies; the update does not explain them.
>
> A disabled Convert button is acceptable in an internal preview. For an architect's trial, I would present a working sequence with the necessary protection in place.
>
> Would I use it? Yes, if it gives me supported limits quickly, lets me test an option accurately, and produces a useful report. I would be less interested if I must reconstruct the property manually, navigate unavailable features, and still perform most of the analysis elsewhere.
>
> The next demonstration I would request is one ordinary property taken all the way through that experience, followed by a condo and a project the architect already knows well. Let the architect operate it without coaching. Watch where they hesitate, which results they question, and whether they can produce something they would actually send to a client.
>
> This is how Claude Code surfaces messages the user sends mid-turn — within the running turn, often alongside the next tool result, rather than as a separate conversation turn. Address the message above as you continue this turn.

## Context (orchestrator interpretation notes; the owner text above is the authority)

Delivered 2026-09-21 ~06:15 UTC, mid-session (seq 125), while the M5-T066 review wave (fresh
HJ + SEC + DCV at frozen 84132df5) was in flight and the T068 harvest pending. The message has
three segments, all relayed in ONE owner message:

1. The predecessor session's plain-English nightly summary to the owner ("Here's everything
   from tonight…" through "…picks up automatically from the handoff.").
2. The owner's question ("Is this the right approach? If you were an architect, would you use
   it like this…").
3. An architect-lens assessment the owner obtained in reply ("Worked for 2m 38s / Yes—the
   overall direction is right…" through "…actually send to a client."). The trailing
   "This is how Claude Code surfaces messages…" line is harness framing captured for
   completeness, not owner product direction.

Reading in-channel: by relaying the assessment into the working session without qualification,
the owner adopts it as product direction for FUTURE increments. It validates the current
direction ("the overall direction is right") and adds requirements on presentation honesty
(the "maximum allowed building" claim classes, no unrestricted green pass under unevaluated
rules), flow (answer-first property understanding), editor ergonomics, input-precision
provenance, site-boundary provenance labels, evidence standards for maximum claims
(independent examples beyond the generator-checker proof), one owner-facing return item (why
the converter and calculator share the sign-in gate), and a requested demonstration path.
Nothing here releases phase C/D, lifts any hold, or changes accepted work; the import-route
paragraph is captured as a pending decision, not an authorization (the D-082-R001 boundary —
phase C assisted import NOT released — stands).
