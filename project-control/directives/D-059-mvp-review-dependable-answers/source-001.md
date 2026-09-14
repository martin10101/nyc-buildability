# D-059 source-001 — Owner 2026-09-14: MVP progress review (dependable-answers priority)

## Capture context

Delivered mid-session (session_01JjK8w1YXwFBjUS8PRrTfHp) on 2026-09-14, while the orchestrator
was executing the seq-111 handoff NEXT ACTIONS (M5-T025/M5-T026/M4-T020 accepted 205th–207th this
session; M4-T021 contract seam in flight at capture, contract head ccc01012). The owner uploaded
a commissioned read-only MVP review (`cd08f17f-NYC-Buildability-MVP-Review-2026-09-14.md`,
reviewing the branch at 16272c05) and delivered a covering message summarizing it. The review
document states it is "a sequencing recommendation for the existing goal, not permission to
merge, deploy, change owner holds, or alter the repository"; the owner's transmission of it with
the covering message makes its findings and sequence the owner's own work order. Baseline
`origin/main` at capture: d8b3899f. Everything below is verbatim.

## Owner covering message (verbatim) {#owner-message-verbatim}

@"C:\Users\MLFLL\.claude\uploads\77a25c99-1f90-4253-868c-bfe425d5ab0a\cd08f17f-NYC-Buildability-MVP-Review-2026-09-14.md" Worked for 12m 20s

You have real, working software now. But the complete MVP you most recently asked for is still unfinished. Its strongest part today is gathering official property information and producing a preliminary residential floor-area calculation. The work that turns that into “here is the building that can actually fit on this property” still has substantial gaps.

I checked the branch you named through 16272c05, including the actual calculation code, progress records, independent reviews, and automated checks. Your two local commits were not part of that pushed version. main remains untouched. I did not change your repository or open the running website; the live-site observations below come from the recorded walkthrough.

An important detail: you recently made the MVP much bigger. On September 13, you authorized residential, commercial, manufacturing, special-district, and waterfront coverage. That is a much larger target than the earlier residential floor-area demo. I am judging progress against that expanded goal. Your recorded scope decision.

Here is where the product stands in everyday language:

What you want it to answer	Where it stands

“Did I choose the right property?”	Address search, official lot identification, confirmation card, and lot-outline display are built.
“What does the city know about this property?”	Official property facts, zoning information, sources, missing information, and conflicts are built.
“How much residential floor space do the basic rules allow?”	Draft floor-area rules across R1–R12 are built. Special conditions still limit which answers it can give.
“How tall can I build?”	Some height rules are built, but they are not connected to the normal result calculation yet.
“How much more can I add to the existing building?”	A subtraction feature exists, but I found important problems with how it interprets the existing building’s area.
“What building shape actually fits?”	Still incomplete.
“How many apartments can I build?”	Still incomplete.
“Can I save this project and send a finished report?”	The complete saving, account, and report workflow remains unfinished.


The distinction between the third and seventh rows is important. A rule might allow 10,000 square feet across all floors, but an architect still needs to determine whether that much space fits within the height, yard, setback, and other restrictions. Your software does not yet bring all those pieces together. Current calculation path, current scenario limitations.

The latest task, M4-T020, is useful groundwork. The city supplies streets as lines with coordinates. Previously, one part of your program read the street information but discarded those lines. This task preserves and checks them so later calculations can use them.

Think of it as giving the program a measuring tool. The next work must use that tool to identify the correct street beside a property, measure the relevant area, and apply the appropriate rule. Finishing M4-T020 alone does not yet give the architect a new complete answer. Its code is pushed and tested, but its final acceptance was still pending in the version I reviewed.

Your street-width policy decision has also been recorded and implemented. That particular owner decision is no longer waiting for you. Some questions about what the city’s underlying width records mean remain unresolved. Latest task, implemented width policy.

The engineering process is generally following the right guidelines. I found evidence that:

Calculations come from code, with identifiable rules and inputs.

Official sources and uncertainty are preserved.

Separate reviewers check completed work.

Draft legal rules are kept separate from professionally approved rules.

Security and software checks are running.


All 18 jobs in the latest main test workflow passed, including the website build and browser tests. That is meaningful progress. Latest test run.

However, passing software tests means the program does what those tests expect. It does not prove that every expectation matches zoning practice or that an architect agrees with the legal interpretation.

The repository records 206 accepted tasks, but 138 belong to the engineering foundation and control system. Those tasks include infrastructure, safeguards, and workflow improvements. They are not 206 finished customer features. I would not turn that count into a percentage showing how close the MVP is to completion.

I found several issues that matter before an architect relies on the results.

1. The “unused floor area” number needs correction.

The program subtracts the city’s recorded building area from the draft zoning allowance.

The problem is that these two areas may be measured differently. The city’s recorded building area is not necessarily the area that zoning law counts. Condominium records add another complication. NYC’s own documentation explains this distinction. Official PLUTO dictionary.

Therefore, the subtraction cannot yet establish how much legal development capacity remains. An experienced architect may notice this immediately. The feature needs compatible area inputs, or wording that clearly presents it as a limited comparison of recorded data. Calculation code.


2. I reproduced a case where missing information becomes a misleading number.

I supplied the actual calculation function with a made-up test property containing:

One existing building.

Building area recorded as zero.

A draft allowance of 10,000 square feet.


It returned 10,000 square feet unused.

But the city’s documentation says a zero building-area value, when buildings exist, means the area is unavailable. The program should recognize that uncertainty instead of treating the property as having no existing building area.

This was a controlled code check, not a claim that your live website produced that result for a real address.


3. Some built features have not reached the normal customer workflow.

The newer R1/R2 and R3/R4 height rules exist in the repository. However, the normal property calculation still selects only the residential floor-area rules.

That means “the height rules were built” and “the architect receives a height answer” are currently different milestones.


4. Updating the website will not fix every confusing result.

The walkthrough records an older deployed backend. Both the website and backend need to be brought to the intended version.

But I also found old “R5” wording inside the newest code, plus a general result label that names the lower-density legal section even though higher-density rules use another section. Those labels need code corrections.

The recorded property failure involving missing map evidence also needs a proper diagnosis. The existing map-data connection has its own setting and failure conditions. Completing the new street-measurement work alone is not a demonstrated fix. Current labels, map-data connection.



These findings are why I would describe the project as carefully built, but not yet sufficiently proven for professional reliance.

An architect would probably see promise and some immediate usefulness. I would not expect him to regard it as a finished feasibility tool yet.

He may appreciate having the property facts, calculation, relevant source, and missing-information warnings together. That can reduce the time spent gathering information before examining a site.

Then he will probably ask:

Does this identify the correct land being analyzed, including any combined lots?

How tall can the building be?

What footprint fits after leaving the required open areas?

How many apartments are possible?

Have special restrictions been checked?

Can I keep the result and send it to my client?


Those are central professional questions. The city’s own zoning-analysis form includes height, stories, units, yards, lot coverage, and parking alongside floor area. NYC zoning-analysis form.

The most convincing demonstration would use a property the architect has already analyzed. Let him compare your answer with his own work, then open the source behind each number. That will reveal usefulness much more clearly than showing him task counts or a polished sample address.

For time savings, I would be cautious about promises. I found no timed benchmark comparing an architect’s work with your app.

After the current problems are corrected and the latest version works reliably on supported properties, these are my planning estimates:

Situation	Potential time saved per property

Experienced architect checking a routine, supported lot	Approximately 15–45 minutes
Straightforward but unfamiliar lot requiring more source research	Approximately 30–90 minutes
Difficult condominium, split-zone lot, special district, or unresolved map data	No dependable saving to promise yet


These are estimates, not measured results.

For a five-unit versus a ten-unit building, the unit count alone does not tell us how long the zoning research takes. A straightforward ten-unit property can be easier to assess than a complicated five-unit property.

Earlier project notes suggested two to four hours saved per lot. I would not repeat that as a demonstrated benefit of the current build. The app does not yet finish the building shape, apartment potential, drawings, or professional report.

The remaining MVP work falls into a clear sequence.

1. Make today’s answers dependable. Fix the building-area problems, old labels, and confusing address changes. Bring the deployed versions and settings into alignment. Reproduce the failed property and identify its actual cause.


2. Finish the street and lot measurements. Complete the current review, then connect street identification, width, distance, and affected portions of the property to the rules.


3. Produce the building limits together. Connect the existing height rules, finish the remaining residential rules, and combine height, setbacks, yards, and coverage into a supported building envelope.


4. Add apartment potential. Build the applicable unit-count rules and the assumptions needed to move from total area toward floors and usable space. Your AMI tool remains downstream of this work.


5. Complete the broader coverage you authorized. Commercial and manufacturing rules still need implementation. Special districts and waterfront remain later waves. Completed research is preparation for those features.


6. Finish the legal-source system. The complete stored legal library, change tracking, and checks for linked exceptions are still unfinished. One older street-definition snapshot is already flagged for correction.


7. Finish the professional workflow. Accounts, saved analyses, working fact confirmation, production survey review, and a clear exportable report still need completion. Database access remains a blocker; supplying access unlocks this work but does not automatically build it.


8. Prove the result with an architect. Use roughly 15–20 real properties across the five boroughs. Compare checked answers, record mistakes and unsupported cases, and measure actual time saved. Professional rule approval and the client benchmark remain outstanding.



I would use the next demonstration to gather an architect’s feedback on a few checked properties while the larger campaign continues. Before presenting the headline number as dependable, I would prioritize the area-calculation findings and the complete path from real property data to a supported result.

The detailed review includes the exact evidence and links for your coding session: .

## Attached review document (verbatim) {#review-document-verbatim}

The full uploaded document `cd08f17f-NYC-Buildability-MVP-Review-2026-09-14.md` is appended
verbatim below between the BEGIN/END markers (byte-faithful copy of the upload).

<!-- BEGIN UPLOADED REVIEW (verbatim) -->
<!-- appended by capture script from the upload file -->

NYC Buildability — MVP progress review
Reviewed 14 September 2026

This is a read-only review of candidate/D-024-mrl-option-b at 16272c05bf0e1d8152673122a930aed3904596a4. It covers the current task records, all M1–M6 task files, blocker records, selected implementation and tests, recent independent reviews, and GitHub CI. It is not a professional approval of the zoning rules. I did not access the running Render application or the owner's local computer.

The project has a working early research tool and a substantial software foundation. It does not yet deliver the complete citywide feasibility MVP the owner authorized on 13 September. The biggest remaining work is connecting the rules, measurements, user workflow, and professional validation into a dependable answer for a real property.

**The MVP goal grew on 13 September.**

D-045 records the owner's explicit selection of “Truly everything (incl. A4)”: residential height/setback rules, geometry-dependent rules and their inputs, contextual/Quality Housing and bonus programs, commercial and manufacturing districts, special-purpose districts, and waterfront zoning. Special districts and waterfront come in later waves. This expanded scope is substantially larger than the earlier FAR-based demonstration. A useful limited pilot can happen during that campaign; it does not replace the approved citywide goal.

Source: [D-045 owner scope](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/directives/D-045-citywide-rule-coverage/source-001.md).

**The pushed state matches the owner's message.**

| Item | What I verified |
|---|---|
| Candidate branch | Pushed through 16272c05, M4-T020 submitted for review |
| Latest M4-T020 status | awaiting_gate; implementation exists; acceptance is not in this reviewed snapshot |
| M5-T025 | Accepted: source links, lot-outline visibility/framing fix, zoom controls |
| M5-T026 | Accepted: optional default-on mode for internal web surfaces |
| Accepted tasks | 206: M0 138; M1 9; M2 21; M3 1; M4 13; M5 24 |
| Main branch | d8b3899f, the 20 August merge of PR #240 |
| Candidate versus main | 1,258 commits ahead, zero behind |
| Latest CI | All 18 jobs successful; separate secret-scan and context-budget runs also successful |
| Owner-local commits | 72ee474c and a7b10f8c were not available as part of the branch snapshot I reviewed |

The accepted-task count includes engineering infrastructure, tests, reviews, repairs, and small feature increments. It is not a count of 206 customer features and cannot be converted into an MVP completion percentage.

Sources: [state](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/state.json), [M4-T020](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/tasks/M4-T020.json), [CI run](https://github.com/martin10101/nyc-buildability/actions/runs/34817436542).

**What an architect could get from the latest branch, when correctly deployed and supplied with usable official data.**

| Architect's question | Current position |
|---|---|
| Which property did I select? | Address resolution, official lot identification, address-confirm card, ZoLa link, and lot-outline display are implemented. |
| What does the city record about the lot and building? | Official-data profile, zoning records, source information, conflicts, and missing facts are implemented. |
| What is the residential floor-area allowance? | Draft residential FAR families across R1–R12 are implemented. Coverage of these tables is not complete coverage of all rules in those districts. |
| Can I get the higher allowance near a wide street? | Conditional rule structure exists, but the street/frontage/100-foot geometry is not connected to the normal result path. |
| How tall can the building be? | Draft height-rule modules exist for R1/R2, R3/R4, and the earlier R5 pilot. The normal property/scenario path currently evaluates residential FAR only. |
| How much additional area can I build? | A cap-minus-recorded-building-area calculation is implemented, but its input meanings and zero handling need correction before reliance. |
| What building shape actually fits? | No complete usable building envelope. Height, yards, setbacks, coverage, and related constraints are not yet combined into that result. |
| How many apartments fit? | No complete dwelling-unit calculation and layout/floor-plate workflow. Existing recorded units do not answer future potential. |
| Can I compare alternatives? | A result/Compare screen exists. Ranking, sensitivity, comparison, and threshold tools also exist on the backend, using explicit supplied assumptions. This is not a finished browser tool that generates several feasible buildings automatically. |
| Can I save a project and send a finished report? | The production persistence/authentication workflow, saved analyses, and professional report/share workflow remain incomplete. |
| Can I upload and review a survey? | Survey extraction/review components exist, but the production HTTP/store connection is still a backlog item. |
| Has a qualified person approved the rules? | No published/verified zoning-rule release was established. G6 professional approval remains required. |

Sources: [rule integration](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/app/rules/integration.py), [scenario endpoint](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/app/api/v1/scenario.py), [scenario constants](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/app/scenario/constants.py), [survey production integration backlog](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/tasks/M2-T019.json), [MVP scope and product expectations](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/docs/MVP_ARCHITECT_REVIEW_QA.md).

**M4-T020 builds a measuring tool that later work can use.**

The city supplies street segments with coordinates. The earlier connector read the street attributes but discarded the line geometry. M4-T020 preserves and validates those lines, including their coordinate system and units. Its implementation has 39 recorded tests and is included in the successful CI snapshot.

It does not yet match the correct street frontage to the lot, construct the legally relevant 100-foot area, calculate which portion of the lot qualifies, or change the customer's FAR result. The next geometry and rule-integration tasks must do that. Street centerlines alone do not establish the correct legal measurement boundary.

The owner-approved D-052 width-classification policy is now implemented in M4-T019. Therefore the old OQ-3 choice is no longer an undecided owner question. The remaining RQ-005 questions about the publisher's field conventions are still unresolved; owner approval of a draft policy does not turn those assumptions into a city guarantee.

Sources: [M4-T020 task](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/tasks/M4-T020.json), [geometry implementation](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/app/connectors/dcm_street_centerline_geometry.py), [M4-T019 task](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/tasks/M4-T019.json), [D-052](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/directives/D-052-street-width-draft-classification/source-001.md).

**The guidelines are mostly being followed, but passing gates has not caught every product problem.**

Positive evidence: official-source connectors; source citations; deterministic legal-rule calculations; explicit uncertainty and draft labels; independent producer/reviewer records; dependency/security checks; separate candidate branch; and no premature published zoning status. The latest CI also builds the web application and runs browser tests against recorded official fixtures.

Limits: fixture tests demonstrate the behavior encoded in the software. They do not demonstrate that a qualified architect agrees with every legal reading, that every important city-data meaning was handled, or that the owner's current live deployment has all settings enabled. The client benchmark remains open as B-010.

Sources: [operating guidelines](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/CLAUDE.md), [M5-T025 independent verification](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/reports/M5-T025-dcv-verification.md), [M5-T026 independent verification](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/reports/M5-T026-dcv-verification.md), [client benchmark blocker](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/blockers/B-010-r5-benchmark-sheet.json).

**Findings that should be addressed before a reliance-oriented architect demonstration.**

1. **The “unused zoning floor area” number combines different area definitions.** The code subtracts PLUTO bldgarea from a draft residential zoning-floor-area cap. PLUTO bldgarea is generally recorded gross building area, with different condominium semantics; it is not a verified existing zoning-floor-area calculation. The connector's own comment already recognizes this distinction. Consequently a positive difference does not establish legal unused development rights, and a negative difference does not by itself establish zoning noncompliance. The current draft and geometry disclaimers help, but the wording still calls this a zoning-floor-area difference. Separate a clearly identified data comparison from an actual rights calculation; require a compatible, supported existing zoning-area input and confirmed zoning-lot extent before making the latter claim.

   Evidence: [unused-floor-area implementation](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/app/scenario/unused_floor_area.py), [labels and assumptions](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/app/scenario/constants.py), [PLUTO connector](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/app/connectors/pluto_soda.py). NYC's [official PLUTO dictionary](https://www.nyc.gov/assets/planning/download/pdf/data-maps/open-data/pluto_datadictionary.pdf), the 22v1 document currently served at this URL, explicitly distinguishes the recorded area from ZR 12-10 area. The repository connector cites the same distinction in its 26v1 source notes.

2. **Zero building area is treated as a real zero without checking whether a building exists.** I executed the actual pure calculation function with a synthetic profile containing one building, recorded bldgarea 0, conditional coverage, and a 10,000 sq ft draft cap. It returned computed = 10,000 sq ft unused, no not-computable reason, and no section-level professional-review flag. This is a unit-level reproduction, not an observed live property. The connector only specially normalizes the year-built zero here; it does not apply the bldgarea-with-buildings missing-value rule. Official PLUTO documentation says a zero area with a positive building count means the area is unavailable. The original zero must remain traceable, but this case should not be consumed as a vacant lot.

   Evidence: [calculation](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/app/scenario/unused_floor_area.py), [connector normalization](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/app/connectors/pluto_soda.py), [existing zero-area test](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/tests/scenario/test_unused_floor_area.py). The test named as a vacant-lot case supplies zero area without establishing vacancy.

3. **Old R5 and ZR 23-21 labels survive in the latest branch.** scenario/constants.py hardcodes “draft max residential zoning floor area (R5)” and a universal cap label naming ZR 23-21. The R6–R12 rules cite ZR 23-22. builder.py emits these constants, so a redeploy cannot fix this mismatch. Generate the coverage description and displayed section references from the actual evaluation. This finding concerns displayed coverage/source wording; it does not, by itself, prove the rule's numeric output is wrong.

   Evidence: [constants](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/app/scenario/constants.py), [builder](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/app/scenario/builder.py), [R6–R12 rule](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/app/rules/rulesets/r6_r12_residential_far.rule.json).

4. **The recorded live missing-spatial-result failure has not been traced to one root cause.** The walkthrough records spatial_intersection_absent for BBL 3022647515. The current default provider needs LIVE_SPATIAL_PROVIDER_ENABLED and can return no result on a missing assignment, connector failure, or partial district response. The deployment checklist does not name that setting or INTERNAL_SCENARIO_ENABLED. The live provider does not use the new street-centerline module. Therefore it is not justified to say that completing M4-T020/B4 alone will fix the already-observed missing-lot/district evidence. Check the deployed commit, settings, and typed logs, then reproduce the same parcel.

   Evidence: [walkthrough notes](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/docs/WORKING_KNOWLEDGE.md), [live provider](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/services/api/app/spatial/live_provider.py), [checklist](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md).
   Live deployment configuration was not accessible in this review, so a specific runtime cause is unconfirmed.

5. **New rule files are ahead of the normal result workflow.** evaluate_property targets residential_far and supplies district plus lot area. It does not evaluate the height families there. The scenario output explicitly keeps the envelope constraints missing. Connect the supported constraints and required inputs before calling their existence in the repository a finished customer feature. R6–R12 height/bulk families remain additional work.

6. **The source library and automatic currency checks are incomplete.** M3-T001 is accepted; M3-T002 through M3-T005 remain backlog. Current snapshot fingerprints and individual source captures are useful, but do not equal a complete, continually refreshed legal corpus with checked cross-references. M4-T018 also documents an incomplete older wide-street snapshot and specifies a corrective task; writing the research report did not update the snapshot.

   Evidence: [M3-T002](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/tasks/M3-T002.json), [M3-T004](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/tasks/M3-T004.json), [snapshot reconciliation](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/reports/M4-T018-zr1210-wide-street-reconciliation.md).

7. **Customer workflow remains unfinished.** The “Confirm facts” button is disabled. Saved confirmations require the production analysis/persistence/authentication path. Survey HTTP/store work remains backlog. An unlisted URL and internal feature flags are not user authentication. The old frontend security blocker is resolved; it should not be reported as the current reason the product is unfinished.

   Evidence: [Confirm screen](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/apps/web/src/components/confirm/ConfirmScreen.tsx), [B-001](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/blockers/B-001-supabase-access-token.json), [M6-T001](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/tasks/M6-T001.json), [resolved B-022](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/blockers/B-022-whole-tree-advisories-block-maplibre-admission.json).

8. **Status prose needs reconciliation.** master_plan.json still describes M2 survey work as held and M3 as 0/5 accepted, although the task files and state record acceptance. The handoff says 204 accepted, while the reviewed state has 206. Some differences are ordinary handoff age; the long-standing milestone summaries are misleading. Treat task records, actual code, and CI as the basis of this review.

   Evidence: [master plan](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/master_plan.json), [state](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/project-control/state.json), [handoff](https://github.com/martin10101/nyc-buildability/blob/16272c05bf0e1d8152673122a930aed3904596a4/docs/SESSION_HANDOFF.md).

**What an architect is likely to think — my assessment, not interview results.**

The useful part is bringing property facts, a supported calculation, source text, and missing-information warnings together. A professional may be interested in using that to prepare for the first conversation about a site.

The likely next questions are: Does it recognize the correct zoning lot? Is the existing area measured on the same basis? What height and footprint fit? How many units? Are special restrictions accounted for? Can I keep and send the result? Until those questions are answered, the tool saves research steps but leaves much of the feasibility study with the architect.

The current presentation also has confusing details recorded in the walkthrough: the address may switch from the searched entrance to PLUTO's representative lot address without explanation; years get comma formatting; and the confirmation view lacks the aggregate missing-input list. Correct source information can still look wrong if the interface does not explain it.

A sensible early demonstration uses the architect's own previously analyzed property, shows the answer, opens the governing source, and compares against their known result. Another example should deliberately contain missing or unsupported information so the refusal behavior is visible. NYC's [zoning-analysis form](https://www.nyc.gov/assets/bsa/downloads/pdf/forms_instructions/bsa_zoning_analysis.pdf) illustrates why FAR alone leaves professional questions outstanding: it also records uses, units, heights, stories, yards, coverage, and parking.

**Time saved is unmeasured.**

I found no timed architect-versus-app benchmark in the evidence reviewed. Earlier working notes suggesting two to four hours saved per simple lot are estimates, not demonstrated outcomes.

For planning only, after the current workflow works reliably on supported lots, my cautious estimate is:

| Situation | Potential net saving per lot |
|---|---|
| Experienced architect; routine supported lot | Roughly 15–45 minutes |
| Unfamiliar but straightforward supported lot needing source lookup | Roughly 30–90 minutes |
| Split lot, difficult condo, special district, unresolved geometry | No dependable saving can be promised; some data gathering may still help |
| Full building design, drawings, permit submission | No basis to claim this work is completed by the current MVP |

These are judgment ranges, not measured results or commitments. Five units versus ten units does not determine the lookup difficulty. Lot conditions, zoning complexity, data gaps, and the architect's familiarity matter more.

Measure this with about 15–20 real parcels across all five boroughs. Record the architect's checked answer, both elapsed times, unanswered questions, corrections, and whether the app result was actually useful. Include condo/billing lots, mixed-address parcels, split zoning, special districts, and wide-street boundary cases. Do not count incorrect quick answers as time saved.

**What remains, in a useful delivery order.**

1. Reconcile the live and source versions, complete the internal deployment checklist, reproduce the failed parcel, and repair the area semantics/zero handling and stale labels. Retest the lot-outline fixes on the owner's device.
2. Complete M4-T020's independent acceptance cycle, then build the frontage/distance/portion geometry and connect the width policy to the applicable rules. Correct the flagged source snapshot and preserve unresolved cases.
3. Connect the existing height constraints to the analysis workflow; build the remaining residential height, setbacks, yards, coverage, and eligibility/bonus rules. Combine constraints into a supported envelope.
4. Deliver dwelling-unit potential and explain the assumptions behind floor count, usable area, and any layout-dependent result. The owner's AMI tool remains downstream.
5. Continue the authorized commercial/manufacturing campaign and later special-purpose/waterfront waves. Research completion is preparation; executable rules, integration, tests, and professional review are still required.
6. Finish the source corpus, immutable history, evidence verification, and cross-reference/currency checks required for reliable rule releases.
7. Complete production storage/authentication and analysis state, user confirmations, survey integration, saved projects, a concise report/export/share flow, and required public-launch protection.
8. Obtain professional rule review and a checked parcel benchmark; measure net time saved. Release only the scope whose complete path has been demonstrated.

This is a sequencing recommendation for the existing goal, not permission to merge, deploy, change owner holds, or alter the repository. No repository changes or external messages were made during this review.
<!-- END UPLOADED REVIEW (verbatim) -->
