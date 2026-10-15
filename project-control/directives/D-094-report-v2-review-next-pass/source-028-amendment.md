# D-094 source-028 (amendment): the owner's resume prompt with the outside audit of 2026-10-15: visible claims that match the drawings and calculations, the scenario sheet, information design, website parity, integrity work, research quality, checks of the real outputs, continuity and the deliverables

Captured 2026-10-15 by the orchestrator (Claude Code session fd88f9b3-8cb7-4d76-83a4-1e93a47e69cf (new session after a /clear; remote control 01TDUgg4Guyvvt3G2i5Bk1fN), model claude-opus-5-5). A script copied the raw text from the saved session transcript under `~/.claude/projects/-root-project-nyc-buildability/`; nothing was retyped, and every quoted fragment below was cut out of the message by the script.

| What | Transcript | Line | Entry uuid | Timestamp | Stored as | Raw-text SHA-256 |
|---|---|---|---|---|---|---|
| the message | `fd88f9b3-8cb7-4d76-83a4-1e93a47e69cf.jsonl` | 10 | none | 2026-10-15T22:59:13.304Z | queue entry holding the typed text | `21f208ea9301c8a71e2d8ddbc42a03cf49d39ee8471ac0ca33a98ae3948dc17d` |
| the message | `fd88f9b3-8cb7-4d76-83a4-1e93a47e69cf.jsonl` | 17 | `d3f0e64a-435e-48c5-b264-0b1380139486` | 2026-10-15T22:59:13.442Z | user line holding the message as delivered | `21f208ea9301c8a71e2d8ddbc42a03cf49d39ee8471ac0ca33a98ae3948dc17d` |

Context. The owner pasted this message at the start of session 2026-10-15c (transcript 2026-10-15T22:59:13Z): the copy-in prompt of handoff seq 172, then an outside audit of 2026-10-15 (sections 1-12) that the owner made a directive. State at the message: main 86a450d4; wave 28 on task/wave28-placement-wiring at e026a391 (pushed, clean, CI 38790045493 read 21/21, ledger 425 accepted), not merged; nothing running. Before this capture, sixteen read-only helpers (batch 1) were dispatched at 23:05 UTC under the rows already captured (handoff section 4, R167-R173); these rows bind at contract time.

## Owner message (verbatim)

Transcript timestamp 2026-10-15T22:59:13.304Z. 25238 characters; the digest is of the raw text.

> Resume as the NYC Buildability orchestrator. Start INSIDE tmux: `tmux attach -t buildability` (use the Claude there, or close it and run `cd /root/project/nyc-buildability && claude` in the tmux window). Never run two sessions. No MCP servers; `/mcp` must show none before any write.
> This is a planned handoff: no resume checks and no READY TO RESUME round (owner, D-094 R109-R113). Read CLAUDE.md, docs/SESSION_HANDOFF.md (seq 172) in full, then /root/project/lanes-runtime/owner-docs/session-2026-10-15b/NEXT-SESSION-BRIEF.md, /root/project/lanes-runtime/owner-docs/session-2026-10-11c/NEXT-SESSION-BRIEF.md sections 1-4, the plan (session-2026-10-11c/workorder-D094-v2.md, session-2026-10-11d/workorder-D094-v3-delta.md, and project-control/master_plan.json report_programme), the last STATE lines of session-2026-10-15b/SESSION_NOTES.md, and the living-files map .claude/rules/living-files.md with its handoff checklist in .claude/session-handoff-profile.md. The ledger, git and CI win over prose.
> Spin up at least 15 sub agents at once (owner, D-094 R169-R173), each doing a small part: no two touch the same file or hold the same shared set (the benchmark set, the review register, the evidence records); no helper pushes (only you integrate and push); every helper reports to you; you divide the work, review it (dispatch more reviewers when useful) and bring it together; builders may be more than three under these rules; heavy test runs stay one at a time under the shared lock; if helpers collide on files, pushes or the lock, lower the number and note why. Next action: handoff section 4 (the wave-28 PR, pre-merge audit, fail-closed merge; PDF #5 from main with every page diffed against print-main-86a450d4 and real website pictures; then the serial lane from E0 (options 2-3) with each increment split into parallel new-file parts, and parallel lanes on other files). Research and verification (D-093) applies; put its dispatch clause in every brief and name the reference cases. Every helper brief says: all parts in ONE hand-back. Do not repeat completed work.
> Standing restrictions: handoff section 5. Updates to the owner: four short plain bullets with links, no time estimates unless asked; answer questions at once and to the point.
> Continue the NYC Buildability project and finish the architect-facing presentation of the work already underway.
>
> The objective is an accurate, visually clear report and website that help an architect quickly understand the property, compare the options, see the proposed building, and identify what still needs confirmation. The objective is not simply fewer pages, more calculations, or passing tests.
>
> Implement the changes and produce the actual outputs. Do not respond with another plan alone.
>
> 1. Continue the existing work and preserve the operating rules
>
> Use the existing Claude Code session in the "buildability" tmux session. Do not launch a second Claude session. If operating from outside tmux, use "tmux attach -t buildability"; if already inside the existing session, remain there.
>
> Preserve the standing requirement that "/mcp" shows no MCP servers before any repository write.
>
> This is a planned continuation. Do not introduce a “READY TO RESUME” round, repeat completed review cycles, or restart the project. Read the current branch head, relevant CI, task ledger, and applicable handoff instructions to determine what remains.
>
> Read the applicable project instructions and continuity records, including:
>
> - "CLAUDE.md".
> - "docs/SESSION_HANDOFF.md" in full.
> - "/root/project/lanes-runtime/owner-docs/session-2026-10-14b/NEXT-SESSION-BRIEF.md".
> - Sections 1–4 of "/root/project/lanes-runtime/owner-docs/session-2026-10-11c/NEXT-SESSION-BRIEF.md".
> - The D-094 work order in "session-2026-10-11c/workorder-D094-v2.md" and delta in "session-2026-10-11d/workorder-D094-v3-delta.md".
> - "project-control/master_plan.json", especially "report_programme".
> - The last STATE entries in "session-2026-10-14b/SESSION_NOTES.md".
> - The applicable living-files map and handoff profile. The supplied locations were "/root/project/w-wave20/.claude/rules/living-files.md" and "/root/project/w-wave20/.claude/session-handoff-profile.md"; use their current canonical successors if they have since moved or merged.
>
> The owner referred to handoff sequence 168. The GitHub audit found an older sequence 156. Do not overwrite newer local instructions with older repository prose. Resolve actual state through the ledger, git, CI, and current owner decisions.
>
> Use the latest documented owner authorization for helper concurrency and building limits. Do not increase those limits merely because this prompt mentions parallel review. If no later authorization supersedes the supplied restrictions, retain at most five helpers, up to eight only when the additional helpers perform research, and at most three building.
>
> Every helper brief must include the applicable D-093 research-and-verification dispatch clause, name the relevant reference cases, and require all parts in ONE hand-back.
>
> Continue ordinary implementation, review, and integration under the existing authorizations. Preserve deployment holds and professional-verification requirements.
>
> 2. Understand the audit baseline before changing anything
>
> These findings describe a specific audited snapshot, not a claim that the branch has remained unchanged.
>
> Audit date: October 15, 2026.
>
> - Main: "86a450d46ff0d21dccf9292146edea785ee2952e".
> - Working branch: "task/wave28-placement-wiring".
> - Working branch head: "8fbf701b20c0bf43e935e0eb85ab566471557835".
> - PR #491 and PR #492 were merged and had successful automatic checks.
> - The audited working branch also completed its automatic checks successfully.
> - An independent local run passed 361 focused tests.
>
> The independent reviews found in project records were AI reviews. Do not describe those as human architect approval or professional zoning verification.
>
> The audit generated PDFs through the actual report API and repository print script, using recorded official-data fixtures through the engine. These were reproducible development previews, not fresh live-data verification or production exports.
>
> All pages of both generated PDFs were inspected: eight pages from main and ten pages from the working branch.
>
> Preserve the genuine progress already made:
>
> - Street-wall, above-base setback, and side-yard calculations connected to the report.
> - The eleven-option comparison table placed first on its page.
> - Removal of the long repeated “Limitation” paragraphs.
> - Consolidation of calculations, open items, input measurement bases, and provenance.
> - Independently worked reference cases or explicitly identified missing facts.
> - Placement and area-allocation calculations.
> - Handling of nonfinite numbers.
> - Stable report fingerprints.
> - The fix for long commit identifiers causing the report to shrink.
> - Accepted law-library corrections.
>
> Check each finding below against the current code and output. If it is already fixed, retain the fix and record the evidence. Do not rebuild completed work.
>
> 3. Correct the contradiction between available calculations and visible drawings
>
> This is the highest-priority presentation defect.
>
> In the audited ten-page PDF:
>
> - Page 4 still said “No building placed” and did not show a proposed building footprint.
> - Page 5 said the building was “Shown on the site plan.”
> - Page 6 showed a generic three-floor stack and a schedule, with wording saying there was no placement on the lot.
> - Page 10 said the allocation was shown as zones inside the placed footprint, but no such zones appeared anywhere.
>
> The engine had placement and allocation data, but the report did not show the promised drawings.
>
> For the audited benchmark, the engine contained:
>
> - Tax-map-basis rear clearance: 33.34 ft.
> - City-map/GIS-basis rear clearance: 35.31 ft.
> - Three floor plates totaling 20,150 sq ft of the stated zoning-floor-area proxy.
> - A 60/40 illustrative allocation: 12,090 sq ft for apartments and 8,060 sq ft for the remainder.
>
> None of those four clearance/allocation numbers appeared in the audited PDF.
>
> Do not fix this merely by changing captions to sound more complete. Finish the drawing integration, then make the captions describe what is actually visible.
>
> A data field such as "placement.status = placed", available floor plates, or "area_allocation.fitted = true" is not proof that a drawing was rendered. It is also not proof of a permitted, physically resolved building.
>
> Inspect the report readers and conditions that determine these claims. In the audited code, "building_not_placed()" could return false based on available geometry even when the report still did not draw the building.
>
> Make claims about visible content depend on the content actually included in the output. Correct page references, legends, comparison-table statuses, and methodology together.
>
> 4. Finish the existing scenario-sheet work
>
> Follow the current task ledger. At the audit, placement wiring was associated with M5-T172, the scenario sheet with M5-T173, and website parity with M5-T174. Preserve these task identities or their documented successors.
>
> Complete the applicable placement acceptance and then finish its architect-facing presentation.
>
> The scenario should provide:
>
> - A dimensioned illustrative proposed footprint positioned on the lot.
> - A compact section or floor-stack drawing showing the relevant levels and heights.
> - A concise floor schedule that reconciles with the calculations.
> - An illustrative area-allocation diagram using the same underlying quantities.
> - A short statement of the important unresolved conditions.
>
> For the allocation diagram, use two zones: “Apartments” and the approved label for the remainder. If that remainder includes more than core and corridors, make its label accurate. Do not describe all non-apartment area as circulation unless that is what the calculation means.
>
> Size the zones from the actual allocation. Do not use decorative proportions that disagree with the numbers.
>
> Do not invent rooms, apartment partitions, unit layouts, or unit counts. Label the drawing “Illustrative.” Do not make it look like an approved architectural plan.
>
> Keep these distinctions explicit:
>
> - Zoning floor area versus physical gross building area.
> - A zoning-floor-area proxy versus a physically developed floor plate.
> - A legal unit ceiling versus an illustrative apartment-yield estimate.
> - A single 60% allocation example versus the broader 60–75% efficiency range.
> - A feasibility illustration versus verified buildability or remaining development rights.
>
> If the current plate geometry is calculated from zoning floor area divided by storeys, say that accurately. Do not silently assume that walls, exclusions, circulation, or gross-area conversion have been resolved.
>
> Keep the existing apartment-size assumption and rounding method traceable. Do not make the 60% illustration appear to validate the whole yield range.
>
> Use the correct measurement basis for each drawing. The 33.34 ft and 35.31 ft clearances came from different source geometries. Do not mix them into one apparently surveyed plan, average them, or conceal their disagreement.
>
> Draw legally established constraint lines only where supported. An illustrative footprint does not establish a legal setback or yard requirement.
>
> All displayed values must come from the shared result model. Do not hardcode this property’s numbers or recalculate zoning rules independently inside rendering components.
>
> 5. Improve the information design across the whole report
>
> The report still feels busy because of uneven hierarchy, repetition, wrapped tables, process language, and missing useful drawings. Page count alone does not explain the problem.
>
> The audited main PDF contained approximately 2,619 extracted words across eight pages. The working version contained approximately 2,674 across ten pages, including repeated page furniture. The increase to ten pages largely reflected the printing fix, not two new pages of substantive scenario drawings.
>
> Do not set an arbitrary three-page, ten-page, or eighty-eight-page target.
>
> The competitor’s length is not a completeness requirement. More pages are appropriate when they contain useful scenarios, drawings, comparisons, or evidence. Fewer pages are not an improvement if essential information disappears.
>
> Use this reading sequence:
>
> 1. What can the architect reasonably conclude?
> 2. What are the main quantities and constraints?
> 3. What does the building or scenario look like?
> 4. How do the options compare?
> 5. What remains unresolved, and what would resolve it?
> 6. Where are the supporting calculations and sources?
>
> Apply the existing "docs/design/ARCHITECT_PRESENTATION_CONTRACT.md" and shared presentation tokens. Locate and use the canonical "presentation-tokens.json" rather than creating another design system.
>
> Make these page-specific improvements, adjusting page numbers if the layout changes:
>
> - Summary: Keep the useful headline quantities and map. Fix awkward wrapping of values and units, crowded explanatory columns, and weak use of space. Do not solve this by shrinking the entire page.
> - Location/context: Keep the locator useful and legible. Large blank areas do not need filler; use a better composition or meaningful context where the presentation contract allows.
> - Constraints: Explain the architectural consequence of each applicable rule. Reduce repeated “conditional” badges, duplicate headings, and long source labels. Preserve material conditions.
> - Site plan: Show the proposed footprint when supported, with dimensions, source basis, and relevant constraints.
> - Options comparison: Keep all eleven options in scope and comparable. Distinguish evaluated results, allowances only, conditional results, missing inputs, and work not yet implemented. Never turn “not evaluated” into zero or “not buildable.”
> - Scenario sheet: Replace the oversized generic stack with the useful combination of footprint, compact section, allocation, and reconciled schedule.
> - Assumptions/open items: Consolidate repeated statements and shorten wrapped text. State the issue, its effect, and the next useful action. Preserve important uncertainty.
> - Evidence appendix: Keep arithmetic, input bases, citations, review status, and report identity. Improve table breaks, repeated headers, source labels, and long identifiers.
>
> Use consistent typography, spacing, alignment, dimension notation, and visual hierarchy. Keep body text readable at normal viewing size. Avoid collisions, clipped labels, orphan headings, tiny footnotes, and tables that require constant backtracking.
>
> Use short readable citations with working links and retained source identifiers. Full legal titles do not need to be repeated in every cell.
>
> Remove internal development language from architect-facing pages. Examples include “owner-approved order,” “connecting the rule,” and descriptions of checking the program against a worked example. Those belong in project records. Tell the architect what the condition means for the property.
>
> Do not add decorative photography to fill space. Prefer useful maps, site imagery with known provenance, diagrams, and clear tables.
>
> 6. Make the website and PDF agree
>
> The website should use the same quantities, assumptions, source bases, scenario identities, and uncertainty states as the PDF.
>
> At the audited snapshot, an area-allocation web component existed but was not mounted in the relevant user flow. A component file alone does not establish website parity.
>
> Connect the appropriate existing components under the established feature flags. Give the architect a clear overview, visible scenario drawings, a comparable options table, and expandable supporting methods and evidence.
>
> Verify the actual relevant property and scenario in the browser. A generic screenshot of another property is not evidence that this benchmark works.
>
> Check desktop and narrow-screen layouts. Tables, diagrams, labels, units, and controls must remain readable without overlap. Preserve the existing map and navigation behavior.
>
> Do not claim full website parity until the visible website and generated PDF have been compared using the same result data.
>
> 7. Use the existing implementation boundaries
>
> Inspect and modify the relevant existing modules rather than creating another reporting framework.
>
> Likely locations include:
>
> - "services/api/app/scenario/three_answers/placement_wiring.py"
> - "services/api/app/scenario/three_answers/geometry.py"
> - "services/api/app/scenario/three_answers/placement.py"
> - "services/api/app/scenario/three_answers/area_allocation.py"
> - "services/api/app/scenario/three_answers/envelope_constraints.py"
> - "services/api/app/drawings/report/page_option_comparison.py"
> - "services/api/app/drawings/report/page_scenario_sheet.py"
> - "services/api/app/drawings/report/page_evidence.py"
> - "services/api/app/drawings/report/readers.py"
> - "services/api/app/drawings/report/drawings_embed.py"
> - "services/api/app/drawings/report/layout.py"
> - "services/api/app/drawings/kit/area_allocation.py"
> - The applicable context-plan renderer under "services/api/app/drawings/maps/"
> - "apps/web/src/components/architect/answers/AreaAllocation.tsx"
> - "apps/web/src/components/architect/answers/FirstBuildingOptions.tsx"
> - "services/api/app/api/v1/report_read.py"
> - "apps/web/scripts/print-report-pdf.mjs"
>
> Confirm current responsibilities before editing. This is a navigation list, not an instruction to modify every file.
>
> 8. Finish outstanding integrity work and preserve honest status
>
> At the audited pushed branch, M3-T013’s producer report was a placeholder, its proposed test file contained only a docstring, and none of the 37 table-bearing bundled snapshots had "table_digest_sha256".
>
> There may have been unpushed work on the working server. Check that before repeating anything.
>
> If still incomplete, finish the captured-law-table integrity protection. Verify that valid captures pass and a deliberate change to a numeric table cell is detected. Document intentional capture updates through the existing process.
>
> Do not call a placeholder, task claim, or empty test an implemented safeguard.
>
> Preserve the accepted fixes associated with M5-T189, M5-T190, and M3-T014, or their current successors.
>
> Report status precisely. “Built,” “connected,” “rendered,” “tested,” “accepted,” “merged,” “deployed,” and “professionally verified” are different states.
>
> 9. Maintain research quality as the remaining options advance
>
> Follow ".claude/rules/research-and-verification.md" and "docs/RESEARCH_AND_VERIFICATION.md". Use applicable primary official sources, evidence records, rule-review records, and independently worked reference cases.
>
> Relevant R6B cases include:
>
> - "real-lot.json"
> - "overlay-reading.json"
> - "placement-building-b.json"
> - "benchmark-options-2-3-6-7.json"
> - "benchmark-options-5-8-9-10.json"
> - "benchmark-options-4-11.json"
>
> These are under "docs/reference-cases/R6B/cases/".
>
> An engine output is not independent verification of the engine. A reference case is not proof that its corresponding scenario has been implemented and rendered.
>
> Preserve the planned progression into options 2 and 3, then community-facility options 6 and 7 and retail option 5, subject to the current authorized plan.
>
> Do not copy the same unit count across different qualification pathways. In particular, do not automatically give the qualifying senior-housing option the affordable-housing option’s 35-unit figure. Confirm the applicable formula, exemptions, qualifications, and remaining limits separately.
>
> The referenced 24,180 sq ft and 65-foot allowances remain conditional on the applicable pathway and supporting facts.
>
> Where reference cases indicate no additional floor area for options 5, 6, or 7 on this lot, implement and explain that result accurately. Do not assume it means those uses have no other architectural or commercial significance.
>
> Keep the existing owner questions concerning option 8 and options 9–10 open until answered. Do not silently choose their intended meaning.
>
> 10. Verify the actual deliverables
>
> Passing tests did not catch the audited contradictions. Add meaningful integration coverage and inspect the rendered outputs.
>
> Generate the report through the real API and standard print path, using the exact full commit identifier. Do not manually edit the exported PDF.
>
> For reproduction, the audit used:
>
> - "POST /api/v1/properties/4073340070/report".
> - The standard residential scenario for 215-16 Northern Boulevard, Queens.
> - "benchmark_provider(with_zoning_lot=True, street_on=True)".
> - "recorded_pack_provider(benchmark_215_16_northern_window)".
> - The applicable internal results and lane flags.
> - The repository’s "print-report-pdf.mjs".
>
> Use the current canonical equivalent where interfaces have changed. Clearly identify recorded-data previews versus live-data exports.
>
> Read every page and inspect every rendered page image at a useful size. Do not inspect only the first page, text extraction, or a contact sheet.
>
> Check:
>
> - Every placement and allocation claim against a visible drawing.
> - Cross-page consistency of statuses, numbers, legends, captions, and references.
> - Reconciliation of floor schedules and allocation totals.
> - Separate handling of tax-map and GIS measurement bases.
> - Readability, clipping, overlaps, page breaks, repeated table headers, page numbering, links, and bookmarks.
> - Correct handling of full-length commit identifiers without global shrinking.
> - Website/PDF agreement for the same results.
>
> Cover meaningful cases: placement data with a rendered drawing; placement data without a rendered drawing; unavailable geometry; unavailable allocation; nonfinite values; legitimate zero values; conflicting measurement bases; and long metadata.
>
> Ensure missing values remain missing rather than becoming zero, and conditional results remain conditional.
>
> Have an independent reviewer inspect the final output from the exact candidate commit, not merely an earlier screenshot or source diff. The producer must not be the sole verifier.
>
> Run the required existing gates and targeted tests that address the remaining risks. Do not substitute large counts of redundant tests for checking the real output.
>
> 11. Preserve the work across sessions
>
> Update the existing canonical project records as work changes. Do not create a competing status system or a new questionnaire.
>
> Keep the task ledger, "report_programme", session handoff, current pass, subsequent option sequence, and applicable design/research records consistent.
>
> At the audit, the master plan still described later options as "not_planned" despite concrete next-step descriptions. Reconcile that discrepancy with the actual authorized work.
>
> Use the living-files map and handoff checklist to determine every required update.
>
> The next session must be able to determine:
>
> - The current branch and exact commit.
> - What is accepted and merged.
> - What remains unmerged or under review.
> - Which drawings are actually visible.
> - Which scenarios are fully implemented, conditional, or still pending.
> - Which PDF and website evidence correspond to which commit.
> - Which questions remain unanswered.
> - The next concrete task and its acceptance criteria.
>
> Preserve the reasons behind the presentation decisions: architect-first reading order, accurate visual claims, shared calculations, explicit uncertainty, useful drawings, and supporting evidence that does not overwhelm the main reading path.
>
> Do not rely on chat history as the only record.
>
> 12. Ask only necessary questions and deliver concrete proof
>
> Put genuinely blocking product or architectural questions into the existing owner questionnaire, including "/root/project/lanes-runtime/owner-docs/OWNER_QUESTIONS.md" if it remains canonical.
>
> For each question, provide the recommended answer, the alternatives, the practical consequence, and what it blocks. Mention the question plainly to the owner. Do not re-ask answered questions or stop unrelated work while waiting.
>
> Use professional judgment for routine spacing, typography, component wiring, and other reversible implementation choices already covered by the design contract.
>
> Deliver all parts in one hand-back:
>
> - The actual PDF generated from the candidate commit.
> - Website screenshots or accessible preview evidence for the same property and scenario.
> - The exact commit and PR status.
> - A concise account of the visible changes.
> - The verification results and remaining limitations.
> - Confirmation that the canonical continuity records were updated.
> - Any genuinely necessary owner questions.
>
> Keep the owner-facing chat update to four short, plain bullets, with links to the deliverables and detailed project records. Do not provide time estimates unless asked. Answer direct owner questions immediately.
>
> Do not describe the report as finished because it has ten pages, eleven option rows, passing CI, or placement data in JSON.
>
> It is ready for the next acceptance decision when the architect can see the supported building scenario, understand the main quantities and constraints, compare the available options, and identify the unresolved decisions—and when every visible claim agrees with the calculations and drawings.

## Reading

| Words of the message | Requirement |
|---|---|
| "Resume as the NYC Buildability orchestrator." "Start INSIDE tmux: `tmux attach -t buildability` (use the Claude there, or close it and run `cd /root/project/nyc-buildability && claude` in the tmux window)." "Never run two sessions." "Continue the existing work and preserve the operating rules" "Use the existing Claude Code session in the "buildability" tmux session." "Do not launch a second Claude session." "If operating from outside tmux, use "tmux attach -t buildability"; if already inside the existing session, remain there." | R175 (obligation) |
| "No MCP servers; `/mcp` must show none before any write." "Preserve the standing requirement that "/mcp" shows no MCP servers before any repository write." | R176 (prohibition) |
| "This is a planned handoff: no resume checks and no READY TO RESUME round (owner, D-094 R109-R113)." "This is a planned continuation." "Do not introduce a “READY TO RESUME” round, repeat completed review cycles, or restart the project." | R177 (prohibition) |
| "Do not repeat completed work." "Do not introduce a “READY TO RESUME” round, repeat completed review cycles, or restart the project." "Do not rebuild completed work." | R178 (prohibition) |
| "Read CLAUDE.md, docs/SESSION_HANDOFF.md (seq 172) in full, then /root/project/lanes-runtime/owner-docs/session-2026-10-15b/NEXT-SESSION-BRIEF.md, /root/project/lanes-runtime/owner-docs/session-2026-10-11c/NEXT-SESSION-BRIEF.md sections 1-4, the plan (session-2026-10-11c/workorder-D094-v2.md, session-2026-10-11d/workorder-D094-v3-delta.md, and project-control/master_plan.json report_programme), the last STATE lines of session-2026-10-15b/SESSION_NOTES.md, and the living-files map .claude/rules/living-files.md with its handoff checklist in .claude/session-handoff-profile.md." | R179 (sequencing) |
| "Read the applicable project instructions and continuity records, including:" ""CLAUDE.md"." ""docs/SESSION_HANDOFF.md" in full." ""/root/project/lanes-runtime/owner-docs/session-2026-10-14b/NEXT-SESSION-BRIEF.md"." "Sections 1–4 of "/root/project/lanes-runtime/owner-docs/session-2026-10-11c/NEXT-SESSION-BRIEF.md"." "The D-094 work order in "session-2026-10-11c/workorder-D094-v2.md" and delta in "session-2026-10-11d/workorder-D094-v3-delta.md"." ""project-control/master_plan.json", especially "report_programme"." "The last STATE entries in "session-2026-10-14b/SESSION_NOTES.md"." "The applicable living-files map and handoff profile." "The supplied locations were "/root/project/w-wave20/.claude/rules/living-files.md" and "/root/project/w-wave20/.claude/session-handoff-profile.md"; use their current canonical successors if they have since moved or merged." "The owner referred to handoff sequence 168." "The GitHub audit found an older sequence 156." "Do not overwrite newer local instructions with older repository prose." "The ledger, git and CI win over prose." "Read the current branch head, relevant CI, task ledger, and applicable handoff instructions to determine what remains." "Resolve actual state through the ledger, git, CI, and current owner decisions." | R180 (decision) |
| "Spin up at least 15 sub agents at once (owner, D-094 R169-R173), each doing a small part: no two touch the same file or hold the same shared set (the benchmark set, the review register, the evidence records); no helper pushes (only you integrate and push); every helper reports to you; you divide the work, review it (dispatch more reviewers when useful) and bring it together; builders may be more than three under these rules; heavy test runs stay one at a time under the shared lock; if helpers collide on files, pushes or the lock, lower the number and note why." "Use the latest documented owner authorization for helper concurrency and building limits." "Do not increase those limits merely because this prompt mentions parallel review." "If no later authorization supersedes the supplied restrictions, retain at most five helpers, up to eight only when the additional helpers perform research, and at most three building." | R181 (authorization) |
| "Spin up at least 15 sub agents at once (owner, D-094 R169-R173), each doing a small part: no two touch the same file or hold the same shared set (the benchmark set, the review register, the evidence records); no helper pushes (only you integrate and push); every helper reports to you; you divide the work, review it (dispatch more reviewers when useful) and bring it together; builders may be more than three under these rules; heavy test runs stay one at a time under the shared lock; if helpers collide on files, pushes or the lock, lower the number and note why." | R182 (prohibition) |
| "Next action: handoff section 4 (the wave-28 PR, pre-merge audit, fail-closed merge; PDF #5 from main with every page diffed against print-main-86a450d4 and real website pictures; then the serial lane from E0 (options 2-3) with each increment split into parallel new-file parts, and parallel lanes on other files)." | R183 (sequencing) |
| "Next action: handoff section 4 (the wave-28 PR, pre-merge audit, fail-closed merge; PDF #5 from main with every page diffed against print-main-86a450d4 and real website pictures; then the serial lane from E0 (options 2-3) with each increment split into parallel new-file parts, and parallel lanes on other files)." | R184 (sequencing) |
| "Research and verification (D-093) applies; put its dispatch clause in every brief and name the reference cases." "Every helper brief says: all parts in ONE hand-back." "Every helper brief must include the applicable D-093 research-and-verification dispatch clause, name the relevant reference cases, and require all parts in ONE hand-back." | R185 (obligation) |
| "Standing restrictions: handoff section 5." "Continue ordinary implementation, review, and integration under the existing authorizations." | R186 (prohibition) |
| "Preserve deployment holds and professional-verification requirements." | R187 (hold) |
| "Updates to the owner: four short plain bullets with links, no time estimates unless asked; answer questions at once and to the point." "Keep the owner-facing chat update to four short, plain bullets, with links to the deliverables and detailed project records." "Do not provide time estimates unless asked." "Answer direct owner questions immediately." | R188 (obligation) |
| "Continue the NYC Buildability project and finish the architect-facing presentation of the work already underway." "Implement the changes and produce the actual outputs." "Do not respond with another plan alone." | R189 (obligation) |
| "The objective is an accurate, visually clear report and website that help an architect quickly understand the property, compare the options, see the proposed building, and identify what still needs confirmation." "The objective is not simply fewer pages, more calculations, or passing tests." | R190 (obligation) |
| "Understand the audit baseline before changing anything" "These findings describe a specific audited snapshot, not a claim that the branch has remained unchanged." "Check each finding below against the current code and output." "If it is already fixed, retain the fix and record the evidence." | R191 (sequencing) |
| "Audit date:" "October 15, 2026." "Main: "86a450d46ff0d21dccf9292146edea785ee2952e"." "Working branch: "task/wave28-placement-wiring"." "Working branch head: "8fbf701b20c0bf43e935e0eb85ab566471557835"." "PR #491 and PR #492 were merged and had successful automatic checks." "The audited working branch also completed its automatic checks successfully." "An independent local run passed 361 focused tests." "The audit generated PDFs through the actual report API and repository print script, using recorded official-data fixtures through the engine." "These were reproducible development previews, not fresh live-data verification or production exports." "All pages of both generated PDFs were inspected: eight pages from main and ten pages from the working branch." | R192 (external_fact) |
| "The independent reviews found in project records were AI reviews." "Do not describe those as human architect approval or professional zoning verification." | R193 (prohibition) |
| "Preserve the genuine progress already made:" "Street-wall, above-base setback, and side-yard calculations connected to the report." "The eleven-option comparison table placed first on its page." "Removal of the long repeated “Limitation” paragraphs." "Consolidation of calculations, open items, input measurement bases, and provenance." | R194 (obligation) |
| "Preserve the genuine progress already made:" "Independently worked reference cases or explicitly identified missing facts." "Placement and area-allocation calculations." "Handling of nonfinite numbers." "Stable report fingerprints." "The fix for long commit identifiers causing the report to shrink." "Accepted law-library corrections." | R195 (obligation) |
| "Correct the contradiction between available calculations and visible drawings" "This is the highest-priority presentation defect." | R196 (sequencing) |
| "In the audited ten-page PDF:" "Page 4 still said “No building placed” and did not show a proposed building footprint." | R197 (obligation) |
| "In the audited ten-page PDF:" "Page 5 said the building was “Shown on the site plan.”" | R198 (obligation) |
| "In the audited ten-page PDF:" "Page 6 showed a generic three-floor stack and a schedule, with wording saying there was no placement on the lot." | R199 (obligation) |
| "In the audited ten-page PDF:" "Page 10 said the allocation was shown as zones inside the placed footprint, but no such zones appeared anywhere." | R200 (obligation) |
| "For the audited benchmark, the engine contained:" "Tax-map-basis rear clearance: 33.34 ft." "City-map/GIS-basis rear clearance: 35.31 ft." "Three floor plates totaling 20,150 sq ft of the stated zoning-floor-area proxy." "A 60/40 illustrative allocation: 12,090 sq ft for apartments and 8,060 sq ft for the remainder." "None of those four clearance/allocation numbers appeared in the audited PDF." | R201 (obligation) |
| "The engine had placement and allocation data, but the report did not show the promised drawings." "Do not fix this merely by changing captions to sound more complete." "Finish the drawing integration, then make the captions describe what is actually visible." | R202 (prohibition) |
| "A data field such as "placement.status = placed", available floor plates, or "area_allocation.fitted = true" is not proof that a drawing was rendered." "It is also not proof of a permitted, physically resolved building." | R203 (evidence) |
| "Inspect the report readers and conditions that determine these claims." "In the audited code, "building_not_placed()" could return false based on available geometry even when the report still did not draw the building." | R204 (obligation) |
| "Make claims about visible content depend on the content actually included in the output." "Correct page references, legends, comparison-table statuses, and methodology together." | R205 (obligation) |
| "Finish the existing scenario-sheet work" "Follow the current task ledger." "At the audit, placement wiring was associated with M5-T172, the scenario sheet with M5-T173, and website parity with M5-T174." "Preserve these task identities or their documented successors." "Complete the applicable placement acceptance and then finish its architect-facing presentation." | R206 (obligation) |
| "The scenario should provide:" "A dimensioned illustrative proposed footprint positioned on the lot." | R207 (obligation) |
| "The scenario should provide:" "A compact section or floor-stack drawing showing the relevant levels and heights." | R208 (obligation) |
| "The scenario should provide:" "A concise floor schedule that reconciles with the calculations." | R209 (obligation) |
| "The scenario should provide:" "An illustrative area-allocation diagram using the same underlying quantities." | R210 (obligation) |
| "The scenario should provide:" "A short statement of the important unresolved conditions." | R211 (obligation) |
| "For the allocation diagram, use two zones: “Apartments” and the approved label for the remainder." | R212 (obligation) |
| "If that remainder includes more than core and corridors, make its label accurate." "Do not describe all non-apartment area as circulation unless that is what the calculation means." | R213 (obligation) |
| "Size the zones from the actual allocation." "Do not use decorative proportions that disagree with the numbers." | R214 (obligation) |
| "Do not invent rooms, apartment partitions, unit layouts, or unit counts." | R215 (prohibition) |
| "Label the drawing “Illustrative.” Do not make it look like an approved architectural plan." | R216 (obligation) |
| "Keep these distinctions explicit:" "Zoning floor area versus physical gross building area." | R217 (obligation) |
| "Keep these distinctions explicit:" "A zoning-floor-area proxy versus a physically developed floor plate." | R218 (obligation) |
| "Keep these distinctions explicit:" "A legal unit ceiling versus an illustrative apartment-yield estimate." | R219 (obligation) |
| "Keep these distinctions explicit:" "A single 60% allocation example versus the broader 60–75% efficiency range." | R220 (obligation) |
| "Keep these distinctions explicit:" "A feasibility illustration versus verified buildability or remaining development rights." | R221 (obligation) |
| "If the current plate geometry is calculated from zoning floor area divided by storeys, say that accurately." "Do not silently assume that walls, exclusions, circulation, or gross-area conversion have been resolved." | R222 (obligation) |
| "Keep the existing apartment-size assumption and rounding method traceable." | R223 (obligation) |
| "Do not make the 60% illustration appear to validate the whole yield range." | R224 (prohibition) |
| "Use the correct measurement basis for each drawing." "The 33.34 ft and 35.31 ft clearances came from different source geometries." "Do not mix them into one apparently surveyed plan, average them, or conceal their disagreement." | R225 (prohibition) |
| "Draw legally established constraint lines only where supported." "An illustrative footprint does not establish a legal setback or yard requirement." | R226 (prohibition) |
| "All displayed values must come from the shared result model." "Do not hardcode this property’s numbers or recalculate zoning rules independently inside rendering components." | R227 (obligation) |
| "Improve the information design across the whole report" "The report still feels busy because of uneven hierarchy, repetition, wrapped tables, process language, and missing useful drawings." "Page count alone does not explain the problem." "The audited main PDF contained approximately 2,619 extracted words across eight pages." "The working version contained approximately 2,674 across ten pages, including repeated page furniture." "The increase to ten pages largely reflected the printing fix, not two new pages of substantive scenario drawings." | R228 (obligation) |
| "Do not set an arbitrary three-page, ten-page, or eighty-eight-page target." "The competitor’s length is not a completeness requirement." "More pages are appropriate when they contain useful scenarios, drawings, comparisons, or evidence." "Fewer pages are not an improvement if essential information disappears." | R229 (prohibition) |
| "Use this reading sequence:" "What can the architect reasonably conclude?" "What are the main quantities and constraints?" "What does the building or scenario look like?" "How do the options compare?" "What remains unresolved, and what would resolve it?" "Where are the supporting calculations and sources?" | R230 (sequencing) |
| "Apply the existing "docs/design/ARCHITECT_PRESENTATION_CONTRACT.md" and shared presentation tokens." "Locate and use the canonical "presentation-tokens.json" rather than creating another design system." | R231 (obligation) |
| "Make these page-specific improvements, adjusting page numbers if the layout changes:" "Summary:" "Keep the useful headline quantities and map." "Fix awkward wrapping of values and units, crowded explanatory columns, and weak use of space." "Do not solve this by shrinking the entire page." | R232 (obligation) |
| "Make these page-specific improvements, adjusting page numbers if the layout changes:" "Location/context:" "Keep the locator useful and legible." "Large blank areas do not need filler; use a better composition or meaningful context where the presentation contract allows." | R233 (obligation) |
| "Make these page-specific improvements, adjusting page numbers if the layout changes:" "Constraints:" "Explain the architectural consequence of each applicable rule." "Reduce repeated “conditional” badges, duplicate headings, and long source labels." "Preserve material conditions." | R234 (obligation) |
| "Make these page-specific improvements, adjusting page numbers if the layout changes:" "Site plan:" "Show the proposed footprint when supported, with dimensions, source basis, and relevant constraints." | R235 (obligation) |
| "Make these page-specific improvements, adjusting page numbers if the layout changes:" "Options comparison:" "Keep all eleven options in scope and comparable." "Distinguish evaluated results, allowances only, conditional results, missing inputs, and work not yet implemented." | R236 (obligation) |
| "Make these page-specific improvements, adjusting page numbers if the layout changes:" "Options comparison:" "Never turn “not evaluated” into zero or “not buildable.”" | R237 (prohibition) |
| "Make these page-specific improvements, adjusting page numbers if the layout changes:" "Scenario sheet:" "Replace the oversized generic stack with the useful combination of footprint, compact section, allocation, and reconciled schedule." | R238 (obligation) |
| "Make these page-specific improvements, adjusting page numbers if the layout changes:" "Assumptions/open items:" "Consolidate repeated statements and shorten wrapped text." "State the issue, its effect, and the next useful action." "Preserve important uncertainty." | R239 (obligation) |
| "Make these page-specific improvements, adjusting page numbers if the layout changes:" "Evidence appendix:" "Keep arithmetic, input bases, citations, review status, and report identity." "Improve table breaks, repeated headers, source labels, and long identifiers." | R240 (obligation) |
| "Use consistent typography, spacing, alignment, dimension notation, and visual hierarchy." "Keep body text readable at normal viewing size." | R241 (obligation) |
| "Avoid collisions, clipped labels, orphan headings, tiny footnotes, and tables that require constant backtracking." | R242 (prohibition) |
| "Use short readable citations with working links and retained source identifiers." "Full legal titles do not need to be repeated in every cell." | R243 (obligation) |
| "Remove internal development language from architect-facing pages." "Examples include “owner-approved order,” “connecting the rule,” and descriptions of checking the program against a worked example." "Those belong in project records." "Tell the architect what the condition means for the property." | R244 (obligation) |
| "Do not add decorative photography to fill space." "Prefer useful maps, site imagery with known provenance, diagrams, and clear tables." | R245 (prohibition) |
| "Make the website and PDF agree" "The website should use the same quantities, assumptions, source bases, scenario identities, and uncertainty states as the PDF." | R246 (obligation) |
| "At the audited snapshot, an area-allocation web component existed but was not mounted in the relevant user flow." "A component file alone does not establish website parity." "Connect the appropriate existing components under the established feature flags." | R247 (obligation) |
| "Give the architect a clear overview, visible scenario drawings, a comparable options table, and expandable supporting methods and evidence." | R248 (obligation) |
| "Verify the actual relevant property and scenario in the browser." "A generic screenshot of another property is not evidence that this benchmark works." "Check desktop and narrow-screen layouts." "Tables, diagrams, labels, units, and controls must remain readable without overlap." | R249 (harness) |
| "Preserve the existing map and navigation behavior." | R250 (prohibition) |
| "Do not claim full website parity until the visible website and generated PDF have been compared using the same result data." | R251 (prohibition) |
| "Use the existing implementation boundaries" "Inspect and modify the relevant existing modules rather than creating another reporting framework." "Likely locations include:" ""services/api/app/scenario/three_answers/placement_wiring.py"" ""services/api/app/scenario/three_answers/geometry.py"" ""services/api/app/scenario/three_answers/placement.py"" ""services/api/app/scenario/three_answers/area_allocation.py"" ""services/api/app/scenario/three_answers/envelope_constraints.py"" ""services/api/app/drawings/report/page_option_comparison.py"" ""services/api/app/drawings/report/page_scenario_sheet.py"" ""services/api/app/drawings/report/page_evidence.py"" ""services/api/app/drawings/report/readers.py"" ""services/api/app/drawings/report/drawings_embed.py"" ""services/api/app/drawings/report/layout.py"" ""services/api/app/drawings/kit/area_allocation.py"" "The applicable context-plan renderer under "services/api/app/drawings/maps/"" ""apps/web/src/components/architect/answers/AreaAllocation.tsx"" ""apps/web/src/components/architect/answers/FirstBuildingOptions.tsx"" ""services/api/app/api/v1/report_read.py"" ""apps/web/scripts/print-report-pdf.mjs"" "Confirm current responsibilities before editing." "This is a navigation list, not an instruction to modify every file." | R252 (prohibition) |
| "Finish outstanding integrity work and preserve honest status" "At the audited pushed branch, M3-T013’s producer report was a placeholder, its proposed test file contained only a docstring, and none of the 37 table-bearing bundled snapshots had "table_digest_sha256"." "There may have been unpushed work on the working server." "Check that before repeating anything." | R253 (sequencing) |
| "If still incomplete, finish the captured-law-table integrity protection." "Verify that valid captures pass and a deliberate change to a numeric table cell is detected." | R254 (harness) |
| "Document intentional capture updates through the existing process." | R255 (obligation) |
| "Do not call a placeholder, task claim, or empty test an implemented safeguard." "Report status precisely. “Built,” “connected,” “rendered,” “tested,” “accepted,” “merged,” “deployed,” and “professionally verified” are different states." | R256 (prohibition) |
| "Preserve the accepted fixes associated with M5-T189, M5-T190, and M3-T014, or their current successors." | R257 (prohibition) |
| "Maintain research quality as the remaining options advance" "Follow ".claude/rules/research-and-verification.md" and "docs/RESEARCH_AND_VERIFICATION.md"." "Use applicable primary official sources, evidence records, rule-review records, and independently worked reference cases." "Relevant R6B cases include:" ""real-lot.json"" ""overlay-reading.json"" ""placement-building-b.json"" ""benchmark-options-2-3-6-7.json"" ""benchmark-options-5-8-9-10.json"" ""benchmark-options-4-11.json"" "These are under "docs/reference-cases/R6B/cases/"." | R258 (obligation) |
| "An engine output is not independent verification of the engine." "A reference case is not proof that its corresponding scenario has been implemented and rendered." | R259 (evidence) |
| "Preserve the planned progression into options 2 and 3, then community-facility options 6 and 7 and retail option 5, subject to the current authorized plan." | R260 (sequencing) |
| "Do not copy the same unit count across different qualification pathways." "In particular, do not automatically give the qualifying senior-housing option the affordable-housing option’s 35-unit figure." "Confirm the applicable formula, exemptions, qualifications, and remaining limits separately." | R261 (prohibition) |
| "The referenced 24,180 sq ft and 65-foot allowances remain conditional on the applicable pathway and supporting facts." | R262 (obligation) |
| "Where reference cases indicate no additional floor area for options 5, 6, or 7 on this lot, implement and explain that result accurately." "Do not assume it means those uses have no other architectural or commercial significance." | R263 (obligation) |
| "Keep the existing owner questions concerning option 8 and options 9–10 open until answered." "Do not silently choose their intended meaning." | R264 (hold) |
| "Verify the actual deliverables" "Passing tests did not catch the audited contradictions." "Add meaningful integration coverage and inspect the rendered outputs." | R265 (harness) |
| "Generate the report through the real API and standard print path, using the exact full commit identifier." "Do not manually edit the exported PDF." | R266 (harness) |
| "For reproduction, the audit used:" ""POST /api/v1/properties/4073340070/report"." "The standard residential scenario for 215-16 Northern Boulevard, Queens." ""benchmark_provider(with_zoning_lot=True, street_on=True)"." ""recorded_pack_provider(benchmark_215_16_northern_window)"." "The applicable internal results and lane flags." "The repository’s "print-report-pdf.mjs"." "Use the current canonical equivalent where interfaces have changed." | R267 (harness) |
| "Clearly identify recorded-data previews versus live-data exports." | R268 (obligation) |
| "Read every page and inspect every rendered page image at a useful size." "Do not inspect only the first page, text extraction, or a contact sheet." | R269 (harness) |
| "Check:" "Every placement and allocation claim against a visible drawing." | R270 (harness) |
| "Check:" "Cross-page consistency of statuses, numbers, legends, captions, and references." | R271 (harness) |
| "Check:" "Reconciliation of floor schedules and allocation totals." | R272 (harness) |
| "Check:" "Separate handling of tax-map and GIS measurement bases." | R273 (harness) |
| "Check:" "Readability, clipping, overlaps, page breaks, repeated table headers, page numbering, links, and bookmarks." | R274 (harness) |
| "Check:" "Correct handling of full-length commit identifiers without global shrinking." | R275 (harness) |
| "Check:" "Website/PDF agreement for the same results." | R276 (harness) |
| "Cover meaningful cases: placement data with a rendered drawing; placement data without a rendered drawing; unavailable geometry; unavailable allocation; nonfinite values; legitimate zero values; conflicting measurement bases; and long metadata." | R277 (harness) |
| "Cover meaningful cases: placement data with a rendered drawing; placement data without a rendered drawing; unavailable geometry; unavailable allocation; nonfinite values; legitimate zero values; conflicting measurement bases; and long metadata." | R278 (harness) |
| "Cover meaningful cases: placement data with a rendered drawing; placement data without a rendered drawing; unavailable geometry; unavailable allocation; nonfinite values; legitimate zero values; conflicting measurement bases; and long metadata." | R279 (harness) |
| "Cover meaningful cases: placement data with a rendered drawing; placement data without a rendered drawing; unavailable geometry; unavailable allocation; nonfinite values; legitimate zero values; conflicting measurement bases; and long metadata." | R280 (harness) |
| "Cover meaningful cases: placement data with a rendered drawing; placement data without a rendered drawing; unavailable geometry; unavailable allocation; nonfinite values; legitimate zero values; conflicting measurement bases; and long metadata." | R281 (harness) |
| "Cover meaningful cases: placement data with a rendered drawing; placement data without a rendered drawing; unavailable geometry; unavailable allocation; nonfinite values; legitimate zero values; conflicting measurement bases; and long metadata." | R282 (harness) |
| "Cover meaningful cases: placement data with a rendered drawing; placement data without a rendered drawing; unavailable geometry; unavailable allocation; nonfinite values; legitimate zero values; conflicting measurement bases; and long metadata." | R283 (harness) |
| "Cover meaningful cases: placement data with a rendered drawing; placement data without a rendered drawing; unavailable geometry; unavailable allocation; nonfinite values; legitimate zero values; conflicting measurement bases; and long metadata." | R284 (harness) |
| "Ensure missing values remain missing rather than becoming zero, and conditional results remain conditional." | R285 (prohibition) |
| "Have an independent reviewer inspect the final output from the exact candidate commit, not merely an earlier screenshot or source diff." "The producer must not be the sole verifier." | R286 (harness) |
| "Run the required existing gates and targeted tests that address the remaining risks." "Do not substitute large counts of redundant tests for checking the real output." | R287 (harness) |
| "Preserve the work across sessions" "Update the existing canonical project records as work changes." "Do not create a competing status system or a new questionnaire." "Use the living-files map and handoff checklist to determine every required update." | R288 (obligation) |
| "Keep the task ledger, "report_programme", session handoff, current pass, subsequent option sequence, and applicable design/research records consistent." | R289 (obligation) |
| "At the audit, the master plan still described later options as "not_planned" despite concrete next-step descriptions." "Reconcile that discrepancy with the actual authorized work." | R290 (obligation) |
| "The next session must be able to determine:" "The current branch and exact commit." "What is accepted and merged." "What remains unmerged or under review." "The next concrete task and its acceptance criteria." | R291 (obligation) |
| "The next session must be able to determine:" "Which drawings are actually visible." "Which scenarios are fully implemented, conditional, or still pending." "Which PDF and website evidence correspond to which commit." "Which questions remain unanswered." | R292 (obligation) |
| "Preserve the reasons behind the presentation decisions: architect-first reading order, accurate visual claims, shared calculations, explicit uncertainty, useful drawings, and supporting evidence that does not overwhelm the main reading path." | R293 (obligation) |
| "Do not rely on chat history as the only record." | R294 (prohibition) |
| "Ask only necessary questions and deliver concrete proof" "Put genuinely blocking product or architectural questions into the existing owner questionnaire, including "/root/project/lanes-runtime/owner-docs/OWNER_QUESTIONS.md" if it remains canonical." "For each question, provide the recommended answer, the alternatives, the practical consequence, and what it blocks." "Mention the question plainly to the owner." | R295 (obligation) |
| "Do not re-ask answered questions or stop unrelated work while waiting." | R296 (prohibition) |
| "Use professional judgment for routine spacing, typography, component wiring, and other reversible implementation choices already covered by the design contract." | R297 (authorization) |
| "Deliver all parts in one hand-back:" "The actual PDF generated from the candidate commit." | R298 (return) |
| "Deliver all parts in one hand-back:" "Website screenshots or accessible preview evidence for the same property and scenario." | R299 (return) |
| "Deliver all parts in one hand-back:" "The exact commit and PR status." | R300 (return) |
| "Deliver all parts in one hand-back:" "A concise account of the visible changes." | R301 (return) |
| "Deliver all parts in one hand-back:" "The verification results and remaining limitations." | R302 (return) |
| "Deliver all parts in one hand-back:" "Confirmation that the canonical continuity records were updated." | R303 (return) |
| "Deliver all parts in one hand-back:" "Any genuinely necessary owner questions." | R304 (return) |
| "Do not describe the report as finished because it has ten pages, eleven option rows, passing CI, or placement data in JSON." | R305 (prohibition) |
| "It is ready for the next acceptance decision when the architect can see the supported building scenario, understand the main quantities and constraints, compare the available options, and identify the unresolved decisions—and when every visible claim agrees with the calculations and drawings." | R306 (evidence) |

- **Reading of the orchestrator (not the owner's words):** 'the latest documented owner authorization for helper concurrency and building limits' is D-094 R169-R173 (source-026): at least fifteen helpers at once; builders above three when no two touch the same file or hold the same shared set; no helper pushes; fewer helpers on collisions. It supersedes R104 (five; eight when the extra ones research; three building), so the message's fallback does not apply, and its mention of parallel review raises nothing beyond R169-R173.
- **Reading of the orchestrator (not the owner's words):** the audit names handoff seq 168 and the session-2026-10-14b files; the latest are handoff seq 172 (uncommitted in the main checkout, the owner's lighter handoff form) and session-2026-10-15b, which the resume part of the same message names. The committed docs/SESSION_HANDOFF.md on main and on the wave-28 branch is seq 156 (what the GitHub audit saw). The ledger, git and CI win over all of them.
- **Reading of the orchestrator (not the owner's words):** the audit's branch head 8fbf701b (the source-026 capture commit) is 13 commits before e026a391; M5-T172 part B's last round and M3-T013 were accepted after it. Each finding is checked against the current code and a current print before any change; a finding already fixed is kept and its evidence recorded.
- **Reading of the orchestrator (not the owner's words):** 'This is the highest-priority presentation defect' outranks the resume part's 'the serial lane from E0': after the wave-28 merge and PDF #5, the serial order is M5-T173 part B, M5-T180, E0 (options 2-3), M5-T174 B1/B2, E1, E2, M0-T195.
- **Reading of the orchestrator (not the owner's words):** the approved zone labels are R089's 'Apartment area' and 'Other building area: core, circulation, walls and services' (the tokens at e026a391); the message's 'Apartments' names the first zone and is not a new label. Changing either label is an owner decision.
- **Reading of the orchestrator (not the owner's words):** 'Deliver all parts in one hand-back' (section 12) is addressed to this session: the closing owner reply links all seven items inside the four-bullet form of R188.
- **Reading of the orchestrator (not the owner's words):** 'Preserve deployment holds and professional-verification requirements' is read with ADR-007: professional review stays advisory and is never claimed; nothing is labelled Verified until the owner answers C1.
- **Sentences of the message quoted by no row:** '1.'; '2.'; '3.'; '4.'; '5.'; '1.'; '2.'; '3.'; '4.'; '5.'; '6.'; '6.'; '7.'; '8.'; '9.'; '10.'; '11.'; '12.'.
- **Not claimed by this capture:** no row is verified; all 132 are pending. This capture changes no product file, no test and no instruction file.
