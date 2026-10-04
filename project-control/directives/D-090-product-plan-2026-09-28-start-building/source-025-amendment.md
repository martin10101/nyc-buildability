# D-090 source-025 (amendment): owner message 57, 2026-10-04 - the #388 hold question, the reviewer's five error groups in the sample PDF, the competitor-error guard-check task, and two forwarded reviewer assessments with corrections

Captured 2026-10-04 by the orchestrator (Claude Code session 4d3637bc-346a-4b44-a0e7-b9688bc4f91a, model claude-fable-5-1) from the saved session transcript `~/.claude/projects/-root-project-nyc-buildability/4d3637bc-346a-4b44-a0e7-b9688bc4f91a.jsonl` (user turn, line 1335, uuid `989f07a9-93a8-4745-81df-9e16783f33c0`, timestamp 2026-10-04T08:21:26.465Z). A script copied the raw text; nothing was retyped. It is complete and byte-identical to the transcript except for the blockquote prefix ("> " on every line, ">" alone on an empty line); raw-text SHA-256 `cce5370ed2917de819889f5eb4600997a0a75b3b1e70a087f065281ed35c0285` (10222 characters). Message numbers continue from source-024 (messages 55-56). Frozen base at capture: integration head `1e73d97c` (origin/candidate/D-024-mrl-option-b).

The message has four parts: (1) the #388 hold question; (2) the owner's (and their AI's) five groups of errors found in the competitor sample PDF and how our program is meant to prevent each; (3) a prompt for a "competitor-error guard check" task (E1-E20); (4) two forwarded assessments by the owner's reviewer ("Worked for 8m 5s" and "Worked for 12m 41s") with corrections to the gap plan (#424) and a reproducible defect in #417.

## Owner message 57 (verbatim)

> Got it on R6B. Drop the "#388 stays on hold until my architect answers R6B" line from the reply I gave you. If R6B was the only reason #388 was held, you can lift that hold.
>
> **What we found wrong in their PDF, in 5 groups:**
>
> 1. **Wrong rules.**
>    - Heights of 50/60 ft, where the law says 45/55, or 65 with affordable housing. Their own page 10 says 45/55.
>    - A "wide-street bonus" that R6B doesn't have.
>    - Old law section numbers and 2024 city data.
> 2. **Didn't use the full allowance.** Their "best" building is 23,136 sq ft when 24,180 is allowed. The excuse doesn't add up: they call the gap 705 sq ft when it's really 1,044, and blame a height limit the building is nowhere near. Other options repeat this.
> 3. **Ignored real-world facts.**
>    - The existing building, which is bigger than any option they show.
>    - That the lot shares one zoning lot with lot 1.
>    - The rules for the inner half in their lot-split idea.
> 4. **Drawings don't match the numbers.**
>    - Plans are wider than the lot.
>    - The same floor plan is reused for every option.
>    - Apartments drawn don't match apartments claimed (only 1 of 10 options matches).
>    - "No elevator," but one is drawn.
>    - Shops are drawn in senior housing.
>    - The 3D pictures have fixed labels: 116 ft wide, a 20 ft rear yard, 8,032 sq ft per floor.
> 5. **Contradictions.**
>    - Zero parking in most options, 16 spaces in one.
>    - Flooding: "no need to elevate" on one page, "must add 2 ft" on another.
>    - Copy-paste options with different heights.
>    - Two "different" options that are the same building.
>
> **How our program prevents each group:**
> 1. **One checked rule table** with current law sections, and data dates shown with an "Out of date" warning.
> 2. **Allowance kept separate from the building that fits.** Any "can't fit" reason must be calculated, never stock text.
> 3. **Real-world facts flagged, never guessed.** The existing building's floor area must be confirmed (it now shows "Not known — please confirm"). The zoning-lot warning shows, and lot splits are checked one piece at a time.
> 4. **Every drawing and label comes from the same numbers as the tables,** and the app never draws template floor plans.
> 5. **An automatic sweep catches any number that differs between pages,** and the same rule (like parking) applies everywhere.
>
> Some of these protections are built; others are still planned. Here's a prompt so the builder agent checks each mistake and proves it with tests:
>
> ```
> TASK: Competitor-error guard check (assessment + tests only).
> Source: docs/COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md and the list below.
> The sample PDF is a reference only — never commit it. Do not change any zoning
> numbers or rule tables; anything about numbers goes to the reviewer.
>
> For each mistake below, find where OUR app could make the same mistake and report:
> our guard (file + test), status [PREVENTED+TESTED / PREVENTED, NO TEST /
> NOT BUILT YET (task ID) / NOT APPLICABLE IN PHASE 1], and evidence (test name, CI run).
> Use the recorded 215-16 Northern data.
>
> E1 Heights: one source; R6B 30/45/55, 45/65 with affordable (C-1)
> E2 No wide-street FAR bonus shown for R6B
> E3 Every law citation exists in the current Zoning Resolution (C-7)
> E4 Data versions shown; "Out of date" when newer (C-7)
> E5 Allowance 24,180 / 20,150 kept separate from the fitting building (C-2)
> E6 Any shortfall reason is computed and true, never template text (C-11)
> E7 Existing building: zoning floor area confirmed or "Not known"; flag when it
>    exceeds today's allowance (C-3)
> E8 Zoning lot ≠ tax lot; DOB shows lot 70 + lot 1 as one zoning lot (C-9)
> E9 Lot splits: each piece checked with its own lot type; subdivision stated (C-10)
> E10 Footprint never larger than the lot (C-4)
> E11 Drawings generated per option, never reused templates (C-4)
> E12 Units: one formula, same number everywhere (C-12)
> E13 Elevator/core statements match the drawings (C-5)
> E14 Ground-floor use in drawings matches the option's use (C-4)
> E15 Every label inside a picture (width, depth, yards, floor areas) comes from results (C-4)
> E16 Parking/transit rule applied the same in every option (C-8)
> E17 Flood statements consistent across all pages (C-5)
> E18 No copy-paste options with mismatched heights/floors (C-5, C-6)
> E19 Identical buildings merged or explained (C-6)
> E20 One footprint value per option on every page (C-5)
>
> Then:
> 1. Write the missing tests in the owning lane. Tests for features not built yet are
>    marked pending with the task ID that will make them pass, so CI stays green.
> 2. Save the table as docs/plans/COMPETITOR_ERROR_GUARDS_2026-10-04.md.
> 3. One PR, independent review, CI green.
> 4. Report to me in plain, simple English:
>    - how many are protected and tested;
>    - which ones still need building;
>    - anything you found where our own app makes the same mistake.
> ```Worked for 8m 5s
>
> He has made real progress, but you still don’t have the finished PDF report. I checked the merged plan, relevant code and the new journey test.
>
> In plain words:
>
> The pieces now connect in a test: saved property records feed the calculations, which feed the drawings and CAD export. The screen cards are tested separately against that same saved result.
>
> It still uses assumptions. This isn’t yet someone entering Northern’s address and receiving a finished report through the website.
>
> The full report still needs assembling and PDF export. Important property facts and zoning interpretations also need verification.
>
> The first target is smaller than your sample: one property and one building option. Multiple programs, detailed apartment layouts and financial analysis come later.
>
>
> I found a few corrections CC should make:
>
> 1. A basic floor-by-floor table already exists. Reuse it; detailed apartment layouts and building-core calculations are what remain missing.
>
>
> 2. Two criticisms of your sample are unfair. Page 8 already shows the apartment calculation. Page 16 distinguishes the floor area allowed from what its proposed design actually uses—different figures aren’t automatically contradictory. :codex-file-citation{path="sandbox:/workspace/scratch/abdbcb170f9a/upload/sample-report.pdf" purpose="source"}
>
>
> 3. The plan calls steps “unblocked” that require your approval. That wording needs fixing.
>
>
> 4. Sources and passing tests don’t guarantee accuracy. They make mistakes easier to trace; professional review remains necessary.
>
>
>
> My recommendation: correct those statements, reuse what already exists, and concentrate on producing one complete, clearly labelled draft report. Keep your approval requirements and the production switches unchanged.
> Worked for 12m 41s
>
> The merge and CI claims check out. But #417 has a reproducible defect, and the gap plan needs corrections. The app still cannot produce this report.
>
> Checked read-only at integration 7fdff1d3, against the attached :codex-file-citation{path="sandbox:/workspace/scratch/b4b1e3e0f15a/upload/sample-report.pdf" purpose="source"}.
>
> Claim	Verdict	Evidence and limits
>
> Six listed PRs merged after review and green CI	DONE	#416, #419, #420, #422, #423 and #424 are merged. Each had 46 successful checks before merging and an exact-head PASS record.
> Draft height note shown — #416	DONE — component only	414ecca1: card reads the note from results, labels it pending qualified review and hides it with withheld draft heights. Engine emitter in #388 remains unmerged and held.
> Recorded maps — #419	DONE — recorded fixture	8f09b3bd: real builder, recorded geometry, SVG snapshots and byte-drift test. Maps remain disconnected from the results/report path.
> DXF tests and scope/notes compatibility — #420, #422	DONE	#420 changes tests only. #422 fixes the conflicting version constraints; scope plus notes validates at 1.2.0. This establishes contract compatibility, not a completed combined engine integration.
> Continuous journey and automatic scope — #417, #421	PARTLY DONE	bac48702 / 0cd8a23b: genuine recorded study→bridge→engine→SVG/DXF chain; cards consume its checked output fixture. Both remain OPEN and green. Northern address lookup and web results route are excluded as stated. Scope defect below needs fixing.
> Accurate-report gap plan — #424	PARTLY DONE	Merge 7fdff1d3: 12 rows separate all four states; professionally verified is “N” throughout. Missing report builder, multi-page PDF exporter, Excel exporter and report routes are confirmed. The 14-step order contains errors below.
>
>
> Three corrections matter:
>
> 1. #417 can emit false disclosure text. I reproduced schema-valid results where an overlay or special district is true, but the statement says none applies. A false within-100-feet input gets a statement saying the lot is within 100 feet. engine_disclosures.py ignores these actual values when composing the statements. The Northern fixture uses matching defaults, so its passing test misses this defect.
>
>
> 2. The plan misstates existing work and dependencies. building_option.py already produces a basic floor-by-floor table; detailed core, deduction and unit schedules remain missing. Steps 1–7 are called “unblocked,” although step 4 needs approval for #405 and step 6 depends on lifting #388’s hold.
>
>
> 3. Two accuracy claims overreach. The sample’s 2.40 allowable FAR versus 2.30 realized FAR is not, by itself, an internal contradiction—it explicitly distinguishes allowance from achievement. Also, deterministic computation and provenance make results traceable; they do not eliminate every way an inaccurate number can reach a report.
>
>
>
> I reproduced 39 passing focused tests for maps, contract compatibility and the prepared height emitter. CI also confirms #421’s four cards tests passed. Review records use the shared GitHub account; separate reviewer identities cannot be authenticated from GitHub alone.
>
> #369, #377, #382 and #405 remain OPEN; #388 remains held. Workflow files and production-switch configuration are unchanged, with lane/study defaults off. The recording server’s actual Geoclient-key configuration is unverified.
>
> The first usable PDF still needs the connected results route, report builder, PDF renderer and storage. Calling it accurate rather than draft additionally needs qualified review of the applicable rules and assumptions.

## Reading

| Owner / reviewer words | Requirement |
|---|---|
| "Got it on R6B. Drop the '#388 stays on hold until my architect answers R6B' line from the reply I gave you. If R6B was the only reason #388 was held, you can lift that hold." | R145 (authorization, conditional) |
| "What we found wrong in their PDF, in 5 groups" (wrong rules; didn't use the full allowance; ignored real-world facts; drawings don't match the numbers; contradictions) and "How our program prevents each group" (five protections, "some built; others still planned") | R146 (external_fact) |
| The prompt: "TASK: Competitor-error guard check (assessment + tests only) ... For each mistake below, find where OUR app could make the same mistake and report: our guard (file + test), status [...], and evidence [...]. Use the recorded 215-16 Northern data. E1 ... E20" | R147 (obligation) |
| "The sample PDF is a reference only — never commit it. Do not change any zoning numbers or rule tables; anything about numbers goes to the reviewer." | R148 (prohibition) |
| "1. Write the missing tests in the owning lane. Tests for features not built yet are marked pending with the task ID that will make them pass, so CI stays green." | R149 (obligation) |
| "2. Save the table as docs/plans/COMPETITOR_ERROR_GUARDS_2026-10-04.md. 3. One PR, independent review, CI green." | R150 (evidence) |
| "4. Report to me in plain, simple English: how many are protected and tested; which ones still need building; anything you found where our own app makes the same mistake." | R151 (return) |
| Reviewer 1 correction 1: "A basic floor-by-floor table already exists. Reuse it; detailed apartment layouts and building-core calculations are what remain missing." Reviewer 2 correction 2: "building_option.py already produces a basic floor-by-floor table; detailed core, deduction and unit schedules remain missing." | R152 (obligation) |
| Reviewer 1 correction 2: "Two criticisms of your sample are unfair. Page 8 already shows the apartment calculation. Page 16 distinguishes the floor area allowed from what its proposed design actually uses—different figures aren't automatically contradictory." Reviewer 2 correction 3 (first half): "The sample's 2.40 allowable FAR versus 2.30 realized FAR is not, by itself, an internal contradiction" | R153 (obligation) |
| Reviewer 1 correction 3: "The plan calls steps 'unblocked' that require your approval. That wording needs fixing." Reviewer 2: "Steps 1-7 are called 'unblocked,' although step 4 needs approval for #405 and step 6 depends on lifting #388's hold." | R154 (obligation) |
| Reviewer 1 correction 4: "Sources and passing tests don't guarantee accuracy. They make mistakes easier to trace; professional review remains necessary." Reviewer 2: "deterministic computation and provenance make results traceable; they do not eliminate every way an inaccurate number can reach a report." | R155 (obligation) |
| Reviewer 2 correction 1: "#417 can emit false disclosure text. I reproduced schema-valid results where an overlay or special district is true, but the statement says none applies. A false within-100-feet input gets a statement saying the lot is within 100 feet. engine_disclosures.py ignores these actual values when composing the statements. The Northern fixture uses matching defaults, so its passing test misses this defect." | R156 (obligation) |
| Reviewer 2: "Review records use the shared GitHub account; separate reviewer identities cannot be authenticated from GitHub alone." | R157 (external_fact) |
| Reviewer 1: "My recommendation: correct those statements, reuse what already exists, and concentrate on producing one complete, clearly labelled draft report." | R158 (sequencing) |
| Reviewer 1: "Keep your approval requirements and the production switches unchanged." Reviewer 2: "#369, #377, #382 and #405 remain OPEN; #388 remains held. Workflow files and production-switch configuration are unchanged, with lane/study defaults off." | R159 (hold) |
| Reviewer 2's claim table (six listed PRs merged DONE; #416/#419/#420/#422 DONE with limits; #417/#421 PARTLY DONE; #424 PARTLY DONE) and "The first usable PDF still needs the connected results route, report builder, PDF renderer and storage. Calling it accurate rather than draft additionally needs qualified review" | acknowledgement; R142 in force (no new row) |
| Reviewer 2: "The recording server's actual Geoclient-key configuration is unverified." | R140 in force (no new row) |

- **Orchestrator's readings (not owner wording):** (1) R145 is conditional. The recorded reasons for holding #388 are D-090-R125 (hold until the audit corrections R118 and R122 have landed and been independently verified) and D-090-R136 (this message approves nothing; the held Lane A merges stay unmerged until corrected, reviewable work is prepared), and every Lane A merge needs the owner's explicit yes per PR. The R6B-coverage question (source-003) is a standing note on every result, not the recorded hold reason. So the condition "if R6B was the only reason" is NOT met, the orchestrator does not lift the hold on this message, and #388 still needs the owner's explicit yes. The line "#388 stays on hold until my architect answers R6B" was never written by the orchestrator and appears in no repository text (`git grep` at capture: no match), so dropping it requires no change. (2) R146 is the owner's and their AI's list of the sample's errors; it is captured as the owner's finding and as the input list for R147, not as a repository determination about the competitor. (3) R147-R151 are executed as one assessment-and-tests packet on a `task/` branch, by a builder-type producer, with an independent read-only reviewer; statuses use exactly the four words the owner gave. (4) R152-R155 are corrections to the merged gap plan (#424) and are applied first, as tagged `[ORCH-CORRECTED per source-025]` edits, before any completion claim. (5) R156 is a defect in the open #417 (stacked on #405): the fix lands on #417's branch as a Lane C correction with tests for non-default flags, re-reviewed; nothing about it merges before #405 gets the owner's yes. It extends DB-126 (which recorded only the overlay value/basis split). (6) R157 is recorded as a fact about the evidence trail; the review records remain the agents' returns saved verbatim by the orchestrator under the shared account; no process change is made on this message. (7) R158/R159: the priority stays one complete, clearly labelled DRAFT report for one lot and one option; nothing here lifts a hold, changes a production switch, approves a Lane A merge or changes the master plan.
