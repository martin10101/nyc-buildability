# D-090 source-043 (amendment): owner message 94, 2026-10-06 - the owner's reviewer's audit of the research update and of the session's statements, and the owner's instruction: resolve the measurement basis before any apartment estimator, correct the HPD area description, keep 700 sq ft and 25 percent unapproved, keep the estimate apart from the legal limit, continue the register with planned, committed and tested told apart, and a register check that enforces recordkeeping only

Captured 2026-10-06 by the orchestrator (Claude Code session 013RaGmCmULdpmjCy58qBeMY, model claude-opus-5-5) from the saved session transcript `~/.claude/projects/-root-project-nyc-buildability/9b6b7b3f-4902-4b4f-b2e0-971a91de749e.jsonl` (line 1264, uuid `4f8ebf48-6fdb-48c6-b319-2764560dda8b`, 2026-10-06T15:15:50.760Z, a user line). A script copied the raw text; nothing was retyped. Raw-text SHA-256 `74413ccb1bf2b0acc90ac4e8f6547c8b5ca32de91102bc941ee0b0248cc87174`. Several lines of the raw text end with one space and its tables use tab characters; the block below is otherwise byte-identical (trailing spaces are not shown). Every fragment quoted in a requirement row was checked by the script to be an exact substring of the message; in the table below a tab inside a quoted fragment is shown as " / ".

The message has two parts. Down to the words "Send Claude this:" it is the report of the owner's reviewer (its first line, "Worked for 6m 29s", is that tool's own header). After those words it is the instruction the owner sends. The owner sent both, so both are recorded; the standing practice is that a forwarded audit is direction, one requirement for each finding.

Context: the message answers the orchestrator's update of the same day, which gave the result of the research helper's check of the documents the owner had named, a proposed formula for the apartment estimate with candidate values (15 ft, 700 sq ft, 25 percent, 10 ft), a table of how the estimate moves, the merge of the race-test repair and the start of the review register.

## Owner message 94 (verbatim)

Transcript timestamp 2026-10-06T15:15:50.760Z.

> Worked for 6m 29s
>
> Most of the source facts and all 16 calculations check out. But the proposed defaults are still assumptions, and several statements need correction before this becomes a reliable feasibility method.
>
> I checked the official HPD, HCR and zoning sources, recalculated the numbers, and reviewed the available repository evidence.
>
> 1. The biggest issue is the relationship between zoning area and apartment area.
>
> The proposed formula can work as a preliminary estimate:
>
> > Residential zoning floor area × assumed apartment-area ratio ÷ assumed average apartment size.
>
>
>
> But its ratio must specifically mean:
>
> > Total HPD-measured dwelling-unit area ÷ residential zoning floor area.
>
>
>
> That is different from the usual ratio of apartment area to the building’s physical gross area. Zoning floor area already excludes certain physical spaces. Applying a generic allowance for all corridors, mechanical rooms and common spaces can deduct space that zoning has already excluded. 
>
> The formula is not inherently wrong. The proposed 75% ratio has not been established. Neither the cited HPD material nor the HCR ceiling validates that ratio.
>
> There is a second inconsistency: RentCafe does not establish that its apartment sizes use HPD measurements. Consequently, “both use the HPD basis” is only true if 700 sq ft HPD-measured area is explicitly adopted as an assumption, rather than described as a verified research result.
>
> 2. Section 23-23 contains specific allowances that materially affect this estimate.
>
> The report accurately discloses that they are unmodelled. However, the law already supplies the following rules:
>
> Space	Potential exclusion from zoning floor area
>
> Residential amenities, including qualifying laundry facilities	Up to 5% of residential floor area; resident-access and other conditions apply.
> Corridors	50% under the qualifying termination/daylighting/outdoor-access provisions; another 50% where the specified corridor length is no more than 100 ft. These provisions can combine.
> Refuse storage/disposal	Up to 3 sq ft per dwelling unit.
> Qualifying access to elevated ground-floor apartments	Up to 100 sq ft per foot of elevation difference, capped at 500 sq ft per building.
>
>
> These are conditional allowances, not automatic deductions for every building. 
>
> Therefore, “laundry rooms count” needs qualification. The simplified parking, balcony and mechanical-space descriptions also omit conditions. Section 12-10 additionally contains qualifying exterior-wall and energy-related exclusions. Those should be checked when relevant, rather than treating the short inclusion/exclusion list as complete. 
>
> 3. The 29-unit zoning calculation is correct for the stated standard-residential example.
>
> Section 23-52 uses maximum permitted residential floor area, divided by 680 where that factor applies. A fractional remainder of 0.75 or more rounds upward.
>
> \[
> 20,150 \div 680 = 29.632\ldots \quad\Rightarrow\quad 29
> \]
>
> This is a density ceiling, not proof that 29 apartments fit. Qualifying senior housing and specified other cases are exempt from the factor; affordable housing alone does not automatically remove it. 
>
> Also, distinguish the two R6B scenarios:
>
> Conditional scenario on a 10,075 sq ft zoning lot	Residential FAR	Formula-based maximum area	Density calculation if 680 applies
>
> Standard residences	2.00	20,150 sq ft	29 units
> Qualifying affordable housing	2.40	24,180 sq ft	35 units
>
>
> These follow from §23-22 and §23-52, before site-specific limitations. The affordable scenario cannot simply inherit the standard scenario’s 20,150 sq ft and 29-unit ceiling. 
>
> For a mixed-use proposal, the apartment estimate must use the residential area actually allocated to that proposal. A shop floor cannot simply be added to a fully consumed residential allowance without checking the combined FAR rules and shared-space allocation. 
>
> The assumed lot area also remains unverified by this research; these calculations do not establish whole-site or remaining development capacity.
>
> 4. The HPD height numbers are correct, but their scope needs better wording.
>
> I checked printed page 37 of the official Laying the Groundwork PDF. It gives:
>
> - 15 ft floor-to-floor.
> - 14 ft 4 in floor-to-underside-of-slab.
> - 12 ft vertical clearance below horizontal utilities.
>
> These measure different things. Selecting 15 ft floor-to-floor does not by itself demonstrate that the structural system and utilities satisfy the other two clearances.
>
> Two qualifications matter:
>
> - “Guidance, not law” is incomplete. It is not a universal zoning minimum, but HPD identifies critical success factors as requirements for mixed-use proposals on HPD-owned property disposed through its RFP process. 
> - The community-facility recommendation has more support than the update suggests. The document defines “retail” broadly enough to include covered ground-floor childcare, health and cultural uses. That supports applying its general guidance to those uses; it does not establish one universal height for every zoning-defined community facility. 
>
> The 14-versus-15-ft story-count statement is arithmetically correct:
>
> Height allowance	14-ft ground floor + 10-ft upper floors	15-ft ground floor + 10-ft upper floors
>
> 55 ft	5 total floors	5 total floors
> 65 ft	6 total floors	6 total floors
>
>
> R6B’s ordinary height table supports the 55/65-ft distinction, with a 45-ft maximum base height. Actual floors still depend on setbacks, elevations, structure and roof treatment. Ten-foot residential floors remain a design assumption. 
>
> 5. The HPD apartment sizes are correct; “excludes wall thickness” needs precision.
>
> The current 2026 HPD guidelines retain these target net areas:
>
> Unit type	Target area
>
> Studio / 0BR	350–400 sq ft
> 1BR	500–550 sq ft
> 2BR	650–725 sq ft
> 3BR	850–950 sq ft
>
>
> HPD measures at finished perimeter-wall faces. Exterior/demising-wall thickness and mechanical/plumbing chases are excluded; internal partitions are included. Therefore, the model must not subtract all apartment walls. 
>
> Using the midpoints and the proposed mix:
>
> \[
> 25\%(375)+35\%(525)+30\%(687.5)+10\%(900)=573.75
> \]
>
> So “about 575” is correct. It is an illustrative mix, not HPD’s prescribed or observed average.
>
> The 2026 guidelines apply to relevant Design Consultation submissions beginning October 1, 2026. MIH/UAP incentive-only projects without another HPD loan subsidy are not automatically subject to them. The research should record this version and applicability. 
>
> 6. The HCR interpretation is substantially correct.
>
> The 2025 guidelines establish a 25% common-space ceiling for new construction/adaptive reuse, with five additional percentage points for NYC, producing a 30% baseline ceiling. Conditional increases also exist.
>
> The measurement distinction is real: HCR uses shared-wall centerlines and includes unit-serving chases/mechanical space in apartment area. Exterior walls are measured at the interior finish. Shared mechanical rooms—and certain garages—enter common-space calculations. This is not equivalent to HPD net area or zoning floor area. Leaving HCR’s percentage out of the proposed formula is correct. 
>
> I could independently corroborate common ÷ (dwelling-unit area + common) from the official 2026 RFP. I could not retrieve the application spreadsheet itself, so I cannot certify its exact Exhibit D-2 cells or the claim that the division appears “only” there. 
>
> 7. RentCafe supports the historical numbers, with two corrections.
>
> The figures are correctly associated with apartments completed during 2014–2023:
>
> Borough	Reported average
>
> Queens	692 sq ft
> Brooklyn	712 sq ft
> Manhattan	737 sq ft
>
>
> They come from the same underlying study. 
>
> However:
>
> - The linked national study does identify coverage: multifamily properties with 50 or more units. Only the shorter NYC article lacks that explanation. 
> - “Market-rate only” is not established for these size figures. RentCafe’s general methodology applies that restriction expressly to its average-rent data. It should not automatically be transferred to the apartment-size study. 
>
> The measuring convention remains unspecified. Thus 700 is usable as an explicitly chosen historical reference, but not a validated R6B-specific, HPD-measured average. The 50-unit threshold makes the sample poorly matched to this 29-unit example; it does not mean R6B universally prohibits 50-unit buildings.
>
> I did not independently establish the exact claim about six repeating news articles.
>
> 8. All 16 sensitivity-table entries are correct.
>
> I recalculated every cell. At 25% assumed loss and 700 sq ft:
>
> \[
> \left\lfloor20,150\times0.75\div700\right\rfloor=21
> \]
>
> That proves the arithmetic. It does not validate the two assumptions or demonstrate a workable apartment layout.
>
> Likewise, neither “25% is appropriate” nor “15% is probably too low” is established by the cited research. Both remain design judgments.
>
> 9. The Windows repair is supported; the register remains unfinished.
>
> The repository audit checked integration commit 80d51b99.
>
> Project statement	Audit result
>
> Race-test repair merged	Confirmed: PR #449.
> Real Windows lock-removal fault	Supported by the code change and regression logs.
> Failed before, passed after on Windows	Confirmed: two relevant failures before; the repaired run passed.
> Three independent checks passed	Recorded agent reviews passed. These are not human professional reviews.
> All 46 checks green	Confirmed: 46 successful check runs, representing 23 distinct check names across push/PR executions.
> Program contains 23 rules	Confirmed as 23 production rule-definition files—not complete legal coverage.
> Register and build enforcement completed	Not verified: the register was absent from the merged branch.
> Corrected research saved	Still pending; PR #447 retained the earlier proposals when checked.
>
>
> The register proposal needs one additional safeguard: updating or touching its file must not preserve an old approval for changed logic. Keep the human reviewer’s original decision and history, but separately mark whether it applies to the current rule/source/implementation version.
>
> My recommendation is to accept the verified source findings and Windows repair, while keeping 700 sq ft, 25%, and 10-ft residential floors labelled as editable preliminary assumptions. Before presenting the apartment count as an accurate feasibility result, resolve the zoning-area conversion, mixed-use allocation, applicable exclusions and physical layout.Send Claude this:
>
> The source checks and sensitivity-table arithmetic are useful. Before implementing the apartment estimator, resolve the measurement basis. Don’t apply a generic gross-to-net loss percentage directly to zoning floor area. Show how the model accounts for zoning exclusions and arrives at HPD-defined dwelling-unit area without double deductions.
>
> Correct the HPD area description: internal partitions and structural members are not all excluded. Keep 700 sq ft and 25% explicitly unapproved assumptions until their basis and limitations are established. Keep estimated physical yield separate from the applicable legal unit cap and its rounding.
>
> Continue the review register, but distinguish planned, committed and tested behavior. Its update check must enforce recordkeeping, not require a human examiner’s approval before development can continue.

## Reading

| Words of the message | Requirement |
|---|---|
| "Before implementing the apartment estimator, resolve the measurement basis." | R387 (sequencing) |
| "Don’t apply a generic gross-to-net loss percentage directly to zoning floor area." | R388 (prohibition) |
| "Show how the model accounts for zoning exclusions and arrives at HPD-defined dwelling-unit area without double deductions." | R389 (return) |
| "Correct the HPD area description: internal partitions and structural members are not all excluded." | R390 (obligation) |
| "Keep 700 sq ft and 25% explicitly unapproved assumptions until their basis and limitations are established." | R391 (hold) |
| "Keep estimated physical yield separate from the applicable legal unit cap and its rounding." | R392 (obligation) |
| "Continue the review register, but distinguish planned, committed and tested behavior." | R393 (obligation) |
| "Its update check must enforce recordkeeping, not require a human examiner’s approval before development can continue." | R394 (prohibition) |
| "Send Claude this:" "The source checks and sensitivity-table arithmetic are useful." "Most of the source facts and all 16 calculations check out." "But the proposed defaults are still assumptions, and several statements need correction before this becomes a reliable feasibility method." | R395 (decision) |
| "But its ratio must specifically mean:" "> Total HPD-measured dwelling-unit area ÷ residential zoning floor area." | R396 (obligation) |
| "Zoning floor area already excludes certain physical spaces." "Applying a generic allowance for all corridors, mechanical rooms and common spaces can deduct space that zoning has already excluded." | R397 (prohibition) |
| "The proposed 75% ratio has not been established." "Neither the cited HPD material nor the HCR ceiling validates that ratio." | R398 (prohibition) |
| "“both use the HPD basis” is only true if 700 sq ft HPD-measured area is explicitly adopted as an assumption, rather than described as a verified research result." | R399 (prohibition) |
| "Section 23-23 contains specific allowances that materially affect this estimate." "Residential amenities, including qualifying laundry facilities / Up to 5% of residential floor area; resident-access and other conditions apply." "Corridors / 50% under the qualifying termination/daylighting/outdoor-access provisions; another 50% where the specified corridor length is no more than 100 ft. These provisions can combine." "Refuse storage/disposal / Up to 3 sq ft per dwelling unit." "Qualifying access to elevated ground-floor apartments / Up to 100 sq ft per foot of elevation difference, capped at 500 sq ft per building." | R400 (external_fact) |
| "These are conditional allowances, not automatic deductions for every building." | R401 (prohibition) |
| "Therefore, “laundry rooms count” needs qualification." "The simplified parking, balcony and mechanical-space descriptions also omit conditions." | R402 (obligation) |
| "Section 12-10 additionally contains qualifying exterior-wall and energy-related exclusions." "Those should be checked when relevant, rather than treating the short inclusion/exclusion list as complete." | R403 (obligation) |
| "This is a density ceiling, not proof that 29 apartments fit." | R404 (decision) |
| "Qualifying senior housing and specified other cases are exempt from the factor; affordable housing alone does not automatically remove it." | R405 (external_fact) |
| "Also, distinguish the two R6B scenarios:" "The affordable scenario cannot simply inherit the standard scenario’s 20,150 sq ft and 29-unit ceiling." | R406 (obligation) |
| "For a mixed-use proposal, the apartment estimate must use the residential area actually allocated to that proposal." "A shop floor cannot simply be added to a fully consumed residential allowance without checking the combined FAR rules and shared-space allocation." | R407 (obligation) |
| "The assumed lot area also remains unverified by this research; these calculations do not establish whole-site or remaining development capacity." | R408 (prohibition) |
| "Selecting 15 ft floor-to-floor does not by itself demonstrate that the structural system and utilities satisfy the other two clearances." | R409 (obligation) |
| "“Guidance, not law” is incomplete." "It is not a universal zoning minimum, but HPD identifies critical success factors as requirements for mixed-use proposals on HPD-owned property disposed through its RFP process." | R410 (obligation) |
| "The community-facility recommendation has more support than the update suggests." "it does not establish one universal height for every zoning-defined community facility." | R411 (obligation) |
| "Actual floors still depend on setbacks, elevations, structure and roof treatment." "Ten-foot residential floors remain a design assumption." | R412 (decision) |
| "HPD measures at finished perimeter-wall faces." "Exterior/demising-wall thickness and mechanical/plumbing chases are excluded; internal partitions are included." "Therefore, the model must not subtract all apartment walls." | R413 (obligation) |
| "It is an illustrative mix, not HPD’s prescribed or observed average." | R414 (obligation) |
| "The 2026 guidelines apply to relevant Design Consultation submissions beginning October 1, 2026." "MIH/UAP incentive-only projects without another HPD loan subsidy are not automatically subject to them." "The research should record this version and applicability." | R415 (obligation) |
| "I could not retrieve the application spreadsheet itself, so I cannot certify its exact Exhibit D-2 cells or the claim that the division appears “only” there." | R416 (external_fact) |
| "The linked national study does identify coverage: multifamily properties with 50 or more units." "Only the shorter NYC article lacks that explanation." | R417 (obligation) |
| "“Market-rate only” is not established for these size figures." "It should not automatically be transferred to the apartment-size study." | R418 (prohibition) |
| "Thus 700 is usable as an explicitly chosen historical reference, but not a validated R6B-specific, HPD-measured average." "it does not mean R6B universally prohibits 50-unit buildings." | R419 (obligation) |
| "I did not independently establish the exact claim about six repeating news articles." | R420 (external_fact) |
| "It does not validate the two assumptions or demonstrate a workable apartment layout." "Likewise, neither “25% is appropriate” nor “15% is probably too low” is established by the cited research." "Both remain design judgments." | R421 (prohibition) |
| "Three independent checks passed / Recorded agent reviews passed. These are not human professional reviews." | R422 (obligation) |
| "Program contains 23 rules / Confirmed as 23 production rule-definition files—not complete legal coverage." | R423 (obligation) |
| "Register and build enforcement completed / Not verified: the register was absent from the merged branch." "Corrected research saved / Still pending; PR #447 retained the earlier proposals when checked." | R424 (obligation) |
| "The register proposal needs one additional safeguard: updating or touching its file must not preserve an old approval for changed logic." | R425 (obligation) |
| "Keep the human reviewer’s original decision and history, but separately mark whether it applies to the current rule/source/implementation version." | R426 (obligation) |
| "My recommendation is to accept the verified source findings and Windows repair, while keeping 700 sq ft, 25%, and 10-ft residential floors labelled as editable preliminary assumptions." | R427 (hold) |
| "Before presenting the apartment count as an accurate feasibility result, resolve the zoning-area conversion, mixed-use allocation, applicable exclusions and physical layout." | R428 (sequencing) |
| "Leaving HCR’s percentage out of the proposed formula is correct." | R429 (decision) |

- **Statements of law and of document content in the audit are checked before they are recorded as fact (R395, R400, R405, R410, R415).** The audit states the allowances of Section 23-23, the exemptions of Section 23-52, a requirement HPD attaches to its guideline for HPD-owned property, and the version and applicability of HPD's 2026 design guidelines. Section 23-23 and the floor-area definition of Section 12-10 are not captured in the repository; Section 23-52 is. Each is read at the official source; where the source differs from the audit, the owner is told.
- **What is withdrawn from the orchestrator's update (R398, R399, R418, R419, R421):** "both use the HPD basis" as a research result; 25 percent as supported by anything; "15 percent is probably too low" as a finding; "market-rate" as a description of the size study's coverage; "not what R6B typically allows" as a statement about R6B.
- **What is corrected in the orchestrator's update (R390, R402, R410, R411, R417):** HPD's apartment area includes the apartment's own partitions and free-standing structural members; laundry rooms, parking, balconies and mechanical space carry conditions; the guideline's standing; the support for community uses; where the study states its coverage.
- **What is owed and not done (R387, R389, R428):** the measurement basis, shown step by step with its law text and a worked example. No estimator is built before it.
- **The register (R393, R394, R423 to R426):** these rows change the register's design before it is reviewed and merged: the original human decision is kept and a separate field says whether it applies to the current version; the check enforces recordkeeping only; planned, committed and tested behaviour are told apart; the 23 are rule files, not complete coverage of the law. They are bound to the register's task in the commit that follows this capture.
- **Not claimed by this capture:** none of R387-R429 is done. All 43 rows are pending.
