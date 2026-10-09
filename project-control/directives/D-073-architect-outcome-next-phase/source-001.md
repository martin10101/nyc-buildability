# D-073 source 001 — owner directive, interactive chat, 2026-09-18 (verbatim)

The owner pasted one long message mid-session. It contains (a) the owner's question about the
external (Codex) review, (b) quoted advisor analysis of the orchestrator's prior status reply,
(c) the owner's request for "a detailed prompt that I should paste him back", and (d) the
operative 10-point directive prompt itself. The ENTIRE message is captured verbatim below; the
operative directive is the final section beginning "Use the original review and your response
to guide the next phase of work." Requirements are decomposed from that operative section; the
earlier material is interpretation context only.

## Owner message (verbatim, complete)

> Did he see the latest work?
> Almost. He saw the newest pushed code — his "newest commit examined" is exactly the small test fix from last night. Two things he could not have seen:
>
> - The street-data build. His one finding that's already out of date is "the live street information connection is still a placeholder." That was true of what was pushed — but loop 1 had just finished that entire build (about 2,200 lines: the live data feed, its safety limits, and the tests) sitting in its workspace, not yet saved into the shared repository. It's the very next thing I review and land. So the first of his two street-width gaps is essentially done; the second (getting the result onto the screen) is real and already on our list as the natural follow-up.
> - The panel's acceptance. He correctly said the panel existed in code but wasn't on the live website. It's now fully accepted; "not live" stays true until you deploy.
>
> How true is the rest? Very — I'd call it accurate and fair on nearly every point.
> What makes me trust it: almost every specific claim matches records we made ourselves before his review existed.
>
> - The four properties where the live analysis stopped — all four match items already on our own discovery list: the split-zoning case (where we verified against city records that refusing to guess was the correct answer), the condo billing-lot connection gap, and boundary-confidence limits. His caution that four properties don't prove a citywide failure rate is also correct.
> - The FAR story (built 2.61 vs reference 3.00 vs "what actually applies to your project") is exactly right — labels fixed, the complete per-property computed answer still the unfinished center.
> - Address search, the six-second deadline, the dependence on the city's service — all true; the deadline concern is on our watch list in nearly the same words.
> - The panel's "shows but doesn't compute" distinction, the missing flood flags, the small polish items — all true and all recorded.
> - The process critique — time lost to review-round limits and fragmented tasks — is fair. Three round-limit stops happened yesterday alone; the one-line setting change remains your call.
>
> One nuance I'd add: some of those "failed" analyses are the product behaving correctly — refusing to invent an answer on a genuinely complicated lot. The fix for those is new capability (split-lot support, the condo connection), never loosening the safety checks — which is also what he concludes.
>
> His bottom line — judge progress by complete, dependable property analyses rather than by task counts, and prove it on real properties with independently pre-established answers — matches the plan we already run almost word-for-word. The next lane does exactly that: land the finished street-data build, then put its result on the screen, so one full limit computes end-to-end from a real address.He is largely agreeing with the review. His main correction is that some additional work had been completed in his workspace but had not yet reached the shared repository when the reviewer checked it.
>
> That means there was more development progress than the reviewer could see. It also means the review accurately described the version that was available to inspect.
>
> The most useful way to understand his response is to separate three things: what has been built, what has been reviewed and accepted, and what actually works on the live website.
>
> Those are different stages, and his update moves two items further along that path.
>
> The first is the street-data connection.
>
> The original review identified two gaps. The program needed to bring real street information into the calculation, and then it needed to send the resulting answer to the screen.
>
> According to this update, the first part has now been built. He describes about twenty-two hundred lines covering the live data connection, protective limits, and tests.
>
> That is a meaningful update. It means the team has reportedly completed the implementation needed to supply the calculation with real street information.
>
> But his wording also tells us where that work stands. He says it is the next thing he will review and land in the shared repository.
>
> So the precise status is: the implementation is reported complete, and it still needs to pass review and become part of the shared version. After that, its behavior in the deployed system needs to be verified.
>
> Calling it "essentially done" makes sense when discussing the coding assignment. For you as the product owner, the feature becomes fully delivered when an architect can enter a real address and receive the supported result.
>
> The amount of code is secondary. Twenty-two hundred lines tells you that this was a substantial assignment. The important question is whether those changes successfully complete the connection for actual properties.
>
> The second street-related gap remains open: getting the calculated result onto the screen.
>
> He explicitly acknowledges that. He says it is already planned as the natural follow-up.
>
> That gives you a clearer picture of the next sequence. First, review and incorporate the street-data work. Then connect its result to the interface. Then demonstrate that the complete process works from a real address.
>
> That would be a meaningful product milestone.
>
> The second update concerns the zoning-information panel.
>
> The reviewer said the panel existed in the code but was not on the live website. He now says the panel has been fully accepted.
>
> That moves it further through the development process. Acceptance means it has cleared the team's required review.
>
> But he also confirms that it remains unavailable on the live website until deployment.
>
> From the architect's perspective, the screen has therefore not received that improvement yet. The work is ready further upstream, and delivery to the live product remains outstanding.
>
> This distinction matters because words like "finished," "accepted," and "live" can sound interchangeable in a progress update. They describe different things. Knowing which stage a feature has reached helps you understand what the architect can actually use today.
>
> On almost everything else, he agrees with the original assessment.
>
> He confirms the FAR distinction: the recorded built FAR of 2.61, the residential reference of 3.00, and the separate question of what actually applies to the proposed development.
>
> He agrees that the labels have improved and that the complete property-specific calculation remains central unfinished work.
>
> He confirms the address-search findings, including dependence on the city's service and the six-second deadline.
>
> He confirms the distinction between showing zoning information and calculating its effects. He also acknowledges the missing flood flags and the remaining presentation issues.
>
> That is significant because he is not disputing the core diagnosis. He is saying that those findings match problems and requirements the team had already recorded.
>
> Having an issue recorded is useful. It means there is a place to track it and carry it forward. The issue still needs a resolution before the user receives the benefit.
>
> His most important qualification concerns the four properties where the analysis stopped.
>
> He is saying that some of those stops were correct behavior under the program's current capabilities.
>
> For example, the team had reportedly checked the split-zoning case against city records and concluded that producing a simple answer would have required an unsupported assumption.
>
> In that situation, stopping protects the user from being given a misleading number.
>
> The development need is to add the capability required to handle that complexity, while preserving the checks that keep the answer supported.
>
> The condominium example requires a different improvement: connecting the billing lot to the underlying land lot needed for the analysis.
>
> These distinctions help you understand what kind of work remains. Some cases need better connections between records. Others need broader calculation capability. A stopped analysis does not automatically mean the existing calculation is broken.
>
> However, correct refusal still leaves the architect with an unanswered question.
>
> The product needs to make that refusal useful. It should explain what condition prevented the answer, which conclusions are affected, and what additional information or review would resolve the problem.
>
> He also accepts the criticism about the development process.
>
> He reports that review-round limits stopped work three times in one day. That suggests the workflow itself may be interrupting otherwise useful progress.
>
> He says changing the setting remains your decision. The message does not specify the current limit, the proposed replacement, or the circumstances behind those stops, so it does not give enough detail to judge that particular change.
>
> The broader issue is clear: the review process needs to preserve quality while allowing work to reach a completed, usable outcome.
>
> Finally, he says the team's plan already measures progress through dependable property analyses, and that the next work will demonstrate one full street-dependent limit from address entry through calculation to the screen.
>
> That is the right kind of milestone to evaluate.
>
> The word "one" matters, though. Completing one limit would establish that this particular path works. Each remaining development limit would still need its own supported implementation and verification.
>
> For that demonstration to answer the original review's concern, it should use a real property whose expected result was established independently. The displayed answer should agree with that expectation, its evidence should be accessible, and any corresponding report should show the same result.
>
> His update therefore gives you a more encouraging picture of the work in progress. The street-data implementation is further along, and the panel has cleared acceptance. He also confirms that the larger assessment was fair.
>
> The next thing to look for is the promised demonstration: a real address producing a supported development limit in the live experience. That will show exactly how much of this additional engineering has become useful to the architect.Can you give me a detailed prompt that I should paste him back to guide him back on track?Use the original review and your response to guide the next phase of work. Your update clarifies that the street-data implementation is further along than the reviewer could see, and that the zoning panel has now been accepted. Build on that progress.
>
> The priority is to turn the existing engineering into complete, dependable property analyses that an architect can actually use.
>
> Continue within our existing scope, architecture, approval rules, and model restrictions. Reuse completed work, preserve the safety checks, and take responsibility for the complete path from address entry to the displayed result and report.
>
> Please follow this direction:
>
> 1. Establish the actual current state, then proceed.
>
> Check the current repository, the workspace containing the street-data implementation, and the versions running on the live frontend and backend.
>
> Distinguish work that is implemented locally, reviewed and accepted, incorporated into the shared repository, deployed, and verified through a real property analysis. Report the relevant commits or other concrete identifiers.
>
> Specifically reconcile the status of the street-data implementation, its connection to the calculation, delivery of the calculated result to the interface, the accepted zoning panel, and the existing report/export path.
>
> Use the existing task records and discovery list. Update them where needed so we have one consistent account of the work.
>
> Keep this initial check brief and move into execution. Routine investigation and implementation already covered by our authorization should continue without another request to approve a plan.
>
> 2. Finish the street-data implementation through the established review process.
>
> Review the implementation you said was completed in the workspace. Confirm that it supplies the information the intended calculation actually needs, preserves its supporting evidence, and handles unavailable, incomplete, contradictory, or otherwise unusable data appropriately.
>
> Resolve material findings and incorporate the accepted changes into the shared repository.
>
> Apply our established street-width interpretation policies. If a genuinely unresolved policy decision affects a calculation, identify that dependency precisely and continue work that does not depend on it. Do not silently turn an unresolved interpretation into a coding assumption.
>
> Use the existing tests and add targeted checks only where they address a concrete remaining risk or required acceptance condition.
>
> Describe completion in terms of working behavior and evidence. The number of lines written is background information; it does not establish whether the feature works.
>
> 3. Complete one street-dependent development limit from beginning to end.
>
> Take the intended limit through the complete user flow: a real address resolves to the correct property; the required street information is obtained; the applicable conditions are established; the calculation runs; and its result and evidence reach the interface.
>
> Remove any remaining delivery gap that keeps an accepted, supported result inside an internal component instead of making it available to the architect.
>
> The displayed result must clearly identify what was calculated, its units, the scenario or conditions under which it applies, and the sources supporting it.
>
> Carry the same result into the existing report or export functionality. Use the same underlying calculation and evidence so the screen and report cannot quietly disagree.
>
> If the report connection is unfinished, identify and complete that connection within the existing design. If there is no usable report capability within the current scope, state that explicitly and distinguish a completed screen demonstration from the broader screen-and-report milestone.
>
> Keep the presentation calm. The architect should see the answer and any material unresolved condition first, with detailed evidence available on demand.
>
> 4. Establish the expected results independently before judging success.
>
> Create a small, fixed collection of real properties for validating this milestone.
>
> Include ordinary properties within the supported scope that should produce calculated results. Include different relevant street conditions where they exercise materially different behavior. Also retain cases that should produce a specific unresolved or unsupported outcome.
>
> Choose the cases and document their expected outcomes before using the application's answers to judge correctness.
>
> Establish those expectations from authoritative source information and applicable rules. The production calculation must not serve as its own independent reference answer. If an expected result cannot be established confidently, classify that case accordingly and select another supported case for the positive demonstration.
>
> Verify the complete flow through the actual interface and existing report, as applicable. Record the deployed versions and date of the check.
>
> A passing internal test, a successful data request, or a calculation that works only with manually supplied inputs is evidence about that component. The complete demonstration must show the ordinary user path working with real property information.
>
> State the scope of what the demonstration proves. Success on a small collection of properties should support claims about the tested capability and covered conditions.
>
> 5. Keep the four previously stopped properties as explicit regression cases.
>
> Maintain a clear record for:
>
> 1279 37th Street, Brooklyn.
>
> 298 Wallabout Street, Brooklyn.
>
> 401 Columbia Street, Brooklyn.
>
> 69-02 Kessel Street, Queens.
>
> For each, identify the precise stopping condition, its evidence, the affected calculations, and the capability or information needed to resolve it.
>
> Distinguish genuine source uncertainty or split zoning from incomplete property-identity connections, unsupported rule coverage, data or geometry problems, and defects in the implementation.
>
> Preserve the finding that a refusal can be correct. A genuinely complicated lot should remain unresolved until the relevant conditions can be supported.
>
> For split zoning, do not collapse a real conflict into one district through an unsupported shortcut. For the condo case, establish the connection to the underlying land lot through authoritative records. For boundary-confidence cases, investigate the underlying data and logic before proposing changes.
>
> Do not relax protective thresholds merely to produce more successful-looking results. Any correction to the checks must have a defensible basis and preserve protection against unsupported conclusions.
>
> These cases do not all have to become positive results in the current street-data milestone. They do need correct, specific outcomes and an explicit place in the remaining work.
>
> Where an issue affects only part of an analysis, determine whether other results can safely remain available. Any displayed value must still have sufficient support, and the interface must make the scope of the unresolved issue understandable.
>
> 6. Preserve the distinction between property records and calculated development allowances.
>
> Keep these concepts separate throughout the interface and report: recorded existing-building information, city reference fields, and allowances calculated for the property under stated conditions.
>
> For 1279 37th Street, preserve the distinction between the recorded built FAR of 2.61 and the residential reference of 3.00. Neither field, by itself, completes the property-specific development analysis.
>
> Show a computed allowance only when the applicable conditions have been established sufficiently. If the computation remains unresolved, explain that without presenting a reference number as though it were the calculated result.
>
> Where ordinary and affordable-housing or other program-dependent scenarios are within the agreed scope, present them separately and state their qualifying conditions. Keep unfinished scenario support visible in the plan.
>
> Also distinguish a calculated floor-area allowance from a complete determination of the building that can physically and legally fit on the lot. Height, yards, setbacks, coverage, and other relevant conditions still need their own supported treatment.
>
> 7. Deliver the accepted panel and completed calculation through the existing release process.
>
> Use the panel's existing acceptance and address any material issues uncovered during integration.
>
> Release completed work through our established deployment process and authorization. Verify what the live frontend and backend are actually serving afterward.
>
> If deployment still requires an owner approval that has not already been given, finish the release preparation first. Present one concrete request identifying the exact version, included changes, verification results, and established recovery path.
>
> Keep deployment status explicit. "Accepted," "merged," and "live and verified" describe different stages.
>
> For the panel, preserve the distinction between displaying a zoning designation and calculating its effect. Track the omitted flood information and remaining presentation work accurately.
>
> For address search, preserve the recovery improvements and investigate the six-second deadline based on observed behavior. Confirm that complete-address search and manual fallback preserve the user's input and give an understandable outcome when the city's service is unavailable or slow.
>
> 8. Keep the remaining work ordered around the architect's needs.
>
> The immediate delivery milestone is the completed street-dependent calculation reaching the user, together with the accepted panel through the established release path.
>
> Use the live-case findings to determine the next implementation priorities, including the condo-to-land-lot connection and the geographic or coverage limitations that prevent useful analyses.
>
> Then continue assembling the supported development limits into one coherent property analysis: FAR, height, yards, setbacks, and coverage, with the conditions that affect each.
>
> Keep conditional development scenarios in that sequence. Maintain an explicit account of supported districts and conditions so the product's claims match its actual coverage.
>
> Permanent evidence storage, document-review capabilities, and the agreed building-code scope should remain visible in the plan. Identify genuine dependencies, and continue zoning work that can proceed independently.
>
> Reuse the existing architecture and completed components. Preserve the default-deny MCP policy and existing SDK admission requirements.
>
> 9. Own the complete result across delegated tasks.
>
> Continue using only the previously mandated Opus 4.8 with xhigh effort for sub-agents. Do not silently substitute a different model. If the required configuration is unavailable, report the specific conflict.
>
> You remain responsible for integration across assignments. A component's acceptance should feed into completion of the user flow, including inputs, calculation, output, interface, and report.
>
> Keep using the shared discovery list. For each material unresolved issue, record what it prevents the architect from doing and the next concrete action needed to resolve it.
>
> Address the review-round interruption separately. Show the current setting, the exact proposed adjustment, the reason for the recent stops, and which review protections would remain. Preserve the existing owner-decision requirement unless that decision has already been made.
>
> Continue unaffected work while a decision is pending. Consolidate related blockers instead of repeatedly stopping for small questions.
>
> 10. Report results in terms I can evaluate as the owner.
>
> At the next completed milestone, give me one consolidated report in plain English, with technical evidence linked underneath the relevant findings.
>
> Tell me what the architect can now do that was unavailable before; which changes are live; which properties were checked; what was independently expected; what the application returned; and whether the screen and report agree.
>
> For unresolved cases, identify the exact missing information or capability, its effect on the analysis, and the next action. Distinguish a correct safety stop from an implementation defect.
>
> Include direct links to the relevant commits, live pages, source evidence, and verification records where available. Avoid unlinked placeholders.
>
> Summarize the required automated checks, but make the real property outcomes central to the report.
>
> Do not assign a completion percentage without a defined basis. State the capabilities demonstrated, the scope they cover, and the remaining limitations.
>
> Proceed with this work under the existing authorization. When a genuine blocker needs my decision, finish the useful independent work first and bring me the specific decision with a recommendation.
>
> The next milestone should demonstrate a real address producing a supported development limit that the architect can inspect and use, with consistent evidence and report output. Use that complete result to guide the subsequent work.

## Interpretation notes (orchestrator)

- "He"/"him" = this orchestrator; the review discussed is the external Codex review of the
  pushed head; the advisor analysis was drafted for the owner and pasted back as the guiding
  prompt. The operative directive is the 10-point section; the preceding analysis is context.
- "The street-data implementation / workspace" = the M5-T035 build in `wt-m5t035` (DB-015 live
  wide-street provider + DCM envelope predicate + DB-013 ceilings).
- "The zoning panel" = M5-T036 (DB-016 context panel + DB-005 ZoLa unification), accepted 218th.
- "Review-round limits" = the supervisor breaker `consecutive_revision_loops` (DB-012; current
  value 4, surfaced option 6; owner-only admin edit).
- "Model restrictions / Opus 4.8 xhigh for sub-agents" = D-064 (main session stays fable-5).
- "Four previously stopped properties" = the live-spatial discovery-list cases named verbatim
  in item 5.
- This directive does not lift any hold (PR #241, expansion §2, Tier D/Section 20 unchanged)
  and does not change gate authority; "existing authorization" = ADR-006 tiers as recorded.
