# M0-T193 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `72fe33cfbf2cb4a02428fa874fac690bdc1ad107` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-090, D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R639, R009, R010, R012, R014, R018, R019, R020, R021, R025, R026, R027, R028, R029, R041, R042, R047, R048, R049, R050, R051, R052, R053, R054, R065, R066, R071, R072, R074, R076, R077, R078, R081, R083, R087, R088, R089, R090, R091, R092, R093, R094, R095, R096, R097, R109, R110, R111, R112, R113.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No VIOLATED or UNVERIFIABLE row. Advisories only, non-blocking: (a) R639 — the orchestrator must read CI green at the exact accept/merge head (the 72fe33cf push CI was peer-cancelled); (b) R021 — the fixed label is "schematic, not to scale" (comma), a deliberate documented canonicalisation of the owner's "schematic / not to scale"; (c) R026/R049 details are carried forward to build tasks M5-T164/page tasks for enforcement.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-11 20:35 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M0-T193 (directives D-090 and D-094, 50 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an automated evidence reproduction, not a human or professional review. Each row below is judged for THIS task's share only: the owner's rule RECORDED in the design contract and instruction files at the frozen head, not as a built report/website page. I reproduced every cited artifact from git plumbing in /root/project/w-wave20 at the frozen head.

(1) HEAD VERIFIED
 - git rev-parse HEAD in /root/project/w-wave20 = 72fe33cfbf2cb4a02428fa874fac690bdc1ad107 on task/wave24-report-v3; working tree clean (git status --short empty).
 - Base is main b47041611 (PR #488 merged). Task material commits ea689ea0 (contract+instructions), a3690424 (producer report), 1dac23f2 (G3 [ORCH-CORRECTED]) all touch only the seven allowed-path files.
 - Contract from the BEGIN ADOPTED BRIEF marker down: sha256 = 3faa7d1f9e1ea50d27421001b6dd4fb3c19a0c55f4b2955270333fbfb81949f1 at aac892fc AND at 72fe33cf — byte-identical (S7 holds; one marker each).
 - Material allowed-path files are byte-stable across 1dac23f2..72fe33cf and 4e92b20c..72fe33cf (git diff empty), so the reviewed content equals the frozen head.

(2) ROWS

ROW D-090-R639 — PASS
 - Recorded in .claude/rules/PROGRAM_KNOWLEDGE.md (diff): new pointer "Read CI green at the EXACT head before every gate, accept, merge and handoff (D-090 R639)".
 - This task's own gates were recorded after CI read green at the submit head 4e92b20c: gh run 38171255530 headSha=4e92b20c conclusion=success.
 - The 72fe33cf push CI run (38171847167) is CANCELLED because a disjoint peer push (M5-T168) superseded it; that is the orchestrator's accept-time concern, not a material regression (files byte-stable 4e92b20c..72fe33cf).
 - Open: the orchestrator must re-read CI green at the exact accept/merge head before recording acceptance.

ROW D-094-R009 — PASS
 - docs/design/ARCHITECT_PRESENTATION_CONTRACT.md change 2026-10-11: principle 1 plus the wording ban on "feasible"/"buildable"/"achievable"/"can be built" and page-3 "demonstrated site fit: Not demonstrated, no bar until a placement exists".
 - A polished drawing is kept from reading as feasibility: page-4 "schematic, not to scale" and the "Illustrative area allocation" caption; competitor structure borrowed, its conclusions not.
 - Open: page build (M5-T165/T166) must apply these labels per page.

ROW D-094-R010 — PASS
 - Page 1 leads with results in large type (headline 28-32 pt) and a small supporting set; page 4 is the predictable scenario sheet (section, reconciled schedule, not-checked list).
 - Faithful to the owner's "dominant headline number + small metrics; predictable scenario sections; drawings that occupy space; short labels".
 - Open: the built pages realise the layout.

ROW D-094-R012 — PASS
 - Page 1 "Named furniture" ends "The coverage inventory leaves the report (R012)"; page-1 table "What it never carries" adds "the coverage inventory"; the appendix opens with the compact scope note of material exclusions.
 - Internal progress/missing-work moves to the owner update per principle 4.
 - Open: build task must actually relocate the inventory.

ROW D-094-R014 — PASS
 - Page 2 = one neighbourhood locator then one large dimensioned constraints close-up; the Supersession paragraph names R014/R074 and retires the second co-equal map and "among its surroundings".
 - The no-photograph rule (owner E1) is kept explicitly; licensed imagery not substituted by generated photos.
 - Open: drawing build (M5-T166) renders the close-up.

ROW D-094-R018 — PASS
 - Page 3: "The comparable-results table comes first ... all eleven options in the owner-approved order ... none reads as evaluated"; table row 3 preserved.
 - All eleven options stay accounted for (principle 2; R007/R084 cited).
 - Open: comparison page build.

ROW D-094-R019 — PASS
 - Page 3 "What it never carries" lists "the missing-work inventory"; principle 4 sends the inventory to the owner update.
 - Matches "Place the detailed missing-work inventory in the owner update".
 - Open: build relocation.

ROW D-094-R020 — PASS
 - Page 3: three distinct measures — allowance, scheduled floor area, demonstrated site fit ("Not demonstrated", with no bar, until a placement exists).
 - Encodes "replace the equal bars with an explicit allowance/scheduled/site-fit distinction; do not imply the scheduled area has been achieved".
 - Open: comparison page build.

ROW D-094-R021 — PASS
 - Page 4: floor stack only as a compact drawing labelled "schematic, not to scale" until a placement exists; main area goes to section and placed footprint.
 - The label is canonicalised to "schematic, not to scale" (comma) and flagged [ORCH-CORRECTED per M0-T193 G3 design A2] as the fixed label for the owner's "schematic / not to scale"; meaning identical, deliberate and recorded (not a weakening).
 - Open: scenario-sheet build applies the label token.

ROW D-094-R025 — PASS
 - Appendix paragraph: issue records with five fields (issue, consequence, next action, responsible role, evidence reference); missing site documents kept apart from program work; limitations as short references on the affected result.
 - Matches the owner's "one concise issue record" structure.
 - Open: appendix page build.

ROW D-094-R026 — PASS
 - Appendix paragraph (ORCH-CORRECTED A1): "the inputs with their basis in plain words and their actual source identifiers and dates (never just \"City records\"; R026)".
 - Carries the owner's "actual source identifiers and dates" and "include real worked calculations or rename the section"; also re-bound to build task M5-T164.
 - Open: appendix build; also bound to M5-T164/M0-T194 for the built page.

ROW D-094-R027 — PASS
 - Appendix table row 6: "the rule sections with links to the law, each result naming its review-register entry and state".
 - Exact-section links were delivered by M5-T159 (already) and the contract preserves them.
 - Open: link-destination checks happen in H2/M5-T159 build, not here.

ROW D-094-R028 — PASS
 - Appendix: "the run identity (fingerprint, code commit, computed date) ... the status key, printed once. No repeated headings"; page-9 provenance moves to the Appendix.
 - Matches "keep them in a clearly named appendix ... avoid repeated headings".
 - Open: appendix build.

ROW D-094-R029 — PASS
 - Fixed wording quoted once: "<allowance> is a conditional tax-lot-only arithmetic allowance, not established remaining development rights." placed beside the headline when the zoning lot is unconfirmed.
 - Page-1 property-specific zoning-lot sentence names the register INDEX entry, never the instrument; faithful to NB-01 (ACRIS ZONE 2022020201551002 recorded 2022-02-08 vs lots 1&70; lot-70 area 10075); no overstatement.
 - Open: page-1 build (also bound M5-T158, accepted).

ROW D-094-R041 — PASS
 - One shared structure for website and PDF via the rewritten page-type table rows 1-6 (decision summary → site/constraints → comparison → scenario sheet → appendix) and principle 5 (one result revision per figure).
 - Keeps the full product scope (principle 2).
 - Open: the shared structure is realised in the web + PDF builds.

ROW D-094-R042 — PASS
 - Principle 4: architects see results, caveats, comparisons, drawings and next actions; feature-completion/missing-implementation/test status go to the owner update.
 - Matches "separate audience needs".
 - Open: build enforces the split.

ROW D-094-R047 — PASS
 - "Print type scale": title 22-23 pt; headline 28-32 pt; section headings 14 pt; body 10.5 pt; table ≥9.5 pt; drawing labels ≥8.5 pt; footer 8.5-9 pt. Every value sits inside the owner's starting ranges and brief §5.
 - The 2026-10-10 "Type" paragraph is marked superseded with its old values bracketed.
 - Open: the scale is applied in the PDF/CSS build.

ROW D-094-R048 — PASS
 - Same paragraph: "margins 14 mm on A4 while question D1 (paper size) is open. Fonts are never shrunk to fit a page count: the larger scale may add a page."
 - Matches "consistent margins ~14-18 mm ... do not reduce fonts to force a page count".
 - Open: build applies margins/grid.

ROW D-094-R049 — PASS
 - The adopted brief §5 (unchanged, line 143) already carries "Put units in the header or beside the value consistently" and right-aligned tabular numerals; the change's checks H2 explicitly cover "section 5 ... tables".
 - The "don't duplicate a section title as its table caption" phrasing is not restated verbatim but is a build-time table detail covered by H2.
 - Open: the "no duplicated caption/title" check is enforced at page build.

ROW D-094-R050 — PASS
 - The six status labels (Verified, Provisional, Illustrative, Conditional, Pending verification, Unresolved) stay (contract line 102); "A shared limitation is stated once"; principle 3 keeps uncertainty beside the result.
 - "Do not remove uncertainty to imitate the competitor" is honoured by principle 3 and the kept labels.
 - Open: build keeps status beside each output.

ROW D-094-R051 — PASS
 - Principle 1: result first, material qualification next, derivation in linked detail; page-1 estimate links to its full calculation and uncertainties link to #issue-<n>.
 - "On the website detail can expand; the PDF contains or precisely references the same evidence" is carried by principle 5 and frontend-web.md.
 - Open: build realises the linked-detail behaviour.

ROW D-094-R052 — PASS
 - Page 2 "What it never carries" adds "a second map doing the same job"; each map has a distinct job (locator vs dimensioned close-up); page 4 keeps the section/footprint as the main drawing, not the stack.
 - Matches "every map a distinct job; a diagram repeating 'three floors' must not displace a useful site drawing".
 - Open: build removes redundant maps.

ROW D-094-R053 — PASS
 - Page 2 close-up: dimension lines anchored to the edges they measure, each naming its basis in plain words (example "103.88 ft, city map outline, not surveyed"), street names with mapped widths, north arrow, scale bar; illustrative geometry marked.
 - The "103.88 ft, city map outline" example is source-exact to NB-04 (gis 103.87921, display-only, not surveyed); no overstatement.
 - Open: drawing build renders the anchored dimensions.

ROW D-094-R054 — PASS
 - Principles 3 and 4 keep missing data visible as short references; the Checks count repeated sentences and drive them to zero ("no repeated 'not yet' prose").
 - Matches "keep missing data honest without repeated 'not yet' prose".
 - Open: text-budget/repeat checks run per page build.

ROW D-094-R065 — PASS
 - The single canonical contract is edited; CLAUDE.md routing row, .claude/rules/drawings-report-presentation.md and .claude/rules/frontend-web.md each add a short pointer to "the change of 2026-10-11, D-094"; no competing design document created.
 - Prior owner decisions preserved (R939 not-placed sentence, E1 no-photo, one-outline check kept).
 - Nothing stays open for this row.

ROW D-094-R066 — PASS
 - "Six principles (R066)" block lists exactly the owner's six: architect-facing results first; full scope retained; uncertainty beside the result; internal progress to the owner update; source/geometry consistency; every-page visual inspection.
 - Each principle cites its supporting rows; all six present and faithful.
 - Open: the principles are enforced by the page tasks.

ROW D-094-R071 — PASS
 - Page-1 item 3: "The ceiling is never labelled Provisional or presented as settled; the estimate is never presented as a count of apartments to build"; the fixed distinction line ends "neither is a demonstrated layout."
 - Encodes "this does not establish that 29 units can actually be built".
 - Open: page-1 build renders the distinction.

ROW D-094-R072 — PASS
 - Checks: "The report never goes above [2,993]; the target is about 10 % fewer (2,713). PDF page 1: at most 220 words." i.e. less text, not more.
 - Addresses "the report actually contains ~10% more text"; before set is the report at main b4704161; also bound to M0-T194 (before set).
 - Open: the text-budget test runs per changed page.

ROW D-094-R074 — PASS
 - Page 2 dimensioned constraints close-up with anchored dimensions; the Supersession paragraph names R014/R074 and retires the superseded 2026-10-10 parts.
 - Matches "the constraints page needs a close-up drawing with dimensions attached to the relevant boundaries".
 - Open: close-up drawing build (M5-T166).

ROW D-094-R076 — PASS
 - Page 4: a section with zoning lines plus the dimensioned placed footprint once placed; table row 4 "never carries" rooms, unit walls, apartment counts, stair or elevator positions; the two-zone illustration.
 - Matches "three stacked rectangles provide no footprint/placement/arrangement" — the sheet now provides footprint/section when placed.
 - Open: scenario build realises the footprint/section.

ROW D-094-R077 — PASS
 - Appendix "no explanation printed twice"; Checks count sentences of ≥8 words printed twice (before set: 3 sentences, 7 printings) and drive to zero.
 - Matches "supporting info useful but explanations repeat; much belongs in an organised appendix".
 - Open: repeats check runs per build; also bound M0-T194.

ROW D-094-R078 — PASS
 - Page-1 item 3: the legal ceiling beside the apartment estimate, side by side and distinct, with the fixed distinction line quoted once in Fixed wordings.
 - Encodes "an architect needs those together, with a short distinction: conditional zoning ceiling vs an unvalidated apartment-yield estimate".
 - Open: page-1 build places them together.

ROW D-094-R081 — PASS
 - Page 1 defines "Four kinds of content and nothing else": results with assumption lines + allowance phrase; one site graphic; ceiling beside estimate with the distinction line; at most three uncertainties linked to #issue-<n>; plus a bounded "Named furniture" list.
 - Matches the reviewer's "rebuild the first page: prominent results, assumptions beside them, one useful site graphic, the few uncertainties".
 - Open: page-1 build (M5-T165).

ROW D-094-R083 — PASS
 - Checks H0-H3: before/after of every changed PDF page (colour and grey) and each changed website view at six widths, checked against the contract rows and section-12 UX ids, inside the task's G3; final export gets the one-minute reader check.
 - Matches "require visual proof: before-and-after screenshots of every changed PDF page and website view".
 - Open: the H0-H3 captures are produced by M0-T194 (before set) and each page task.

ROW D-094-R087 — PASS
 - Two-zone illustration: "The remaining share is never called 'core and corridors'"; the second zone is "Other building area: core, circulation, walls and services".
 - Faithful to the owner's decision that 25-40% must not read as a calculated layout.
 - Open: build renders the zone names.

ROW D-094-R088 — PASS
 - "The two-zone area illustration ... replaces the earlier state 'nothing drawn inside the footprint' (R088)" under R089-R098.
 - Records the authorization to add the illustration.
 - Open: build adds the illustration.

ROW D-094-R089 — PASS
 - Fixed wordings quote the two labels exactly: "Apartment area" and "Other building area: core, circulation, walls and services"; the owner's closing full stop is excluded; no inner double-quote or backslash (token-generator constraint met).
 - Faithful to the owner's words.
 - Open: build uses the label tokens from presentation-tokens.json.

ROW D-094-R090 — PASS
 - Fixed wordings quote the caption exactly: "Illustrative area allocation—not a floor plan" with the em dash; closing full stop excluded; no inner double-quote/backslash.
 - Faithful to the owner's caption.
 - Open: build uses the caption token.

ROW D-094-R091 — PASS
 - "One stated percentage ... 60 % apartment area"; basis stated as the low end of the owner's 60-75 % share (D-090 R540; preliminary_apartment_estimate.py share_low = 0.60) — I confirmed share_low: float = 0.60 at line 94 of that file; "the drawing's proportions equal the calculation".
 - Declared an assumption, not a measurement, owner-editable.
 - Open: build draws proportions = the stated 60 %.

ROW D-094-R092 — PASS
 - "Compatible area measures": the share applies to the estimate's measure (residential floor area); the statement "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked" travels with every appearance; physical plate listed as not checked; "Zoning floor area is never treated as the physical floor-plate area".
 - Matches "check compatible area measurements; do not automatically treat zoning floor area as the physical floorplate area".
 - Open: build carries the plate statement; also bound M5-T164.

ROW D-094-R093 — PASS
 - "No rooms, unit walls, apartment counts, or invented stair or elevator positions (R093)"; page-4 table "never carries" the same list.
 - Faithful to the owner's prohibition.
 - Open: build honours the prohibition.

ROW D-094-R094 — PASS
 - "Zones are drawn inside the footprint only when the footprint has been fitted to the site; until then, a simple proportional bar sits beside the building diagram."
 - Faithful to the owner's sequencing; also bound M5-T164.
 - Open: build switches bar→zones on fit.

ROW D-094-R095 — PASS
 - "The caption ... is the only explanation beside the drawing" and "The method goes in the appendix"; appendix lists the area-illustration method.
 - Matches "keep the explanation to one short caption; put methodology in the appendix".
 - Open: build keeps one caption, method in appendix.

ROW D-094-R096 — PASS
 - "The website and the PDF show the same illustration"; .claude/rules/frontend-web.md adds "website and PDF show the same figures and the same area illustration".
 - Faithful to "apply this consistently to the website and PDF".
 - Open: web + PDF builds (M5-T164/web tasks) render the same illustration.

ROW D-094-R097 — PASS
 - Recorded in the design instructions (this contract, two-zone section, "entered 2026-10-11 16:57 UTC") AND in the owner questionnaire: OWNER_QUESTIONS.md "Answered and kept here" → "H1 ... answered 16:57 UTC" with the labels and caption.
 - Both halves of "record in design instructions and questionnaire" are present.
 - Nothing stays open for the recording share.

ROW D-094-R109 — PASS
 - CLAUDE.md start-of-session: "After a planned handoff ... read docs/SESSION_HANDOFF.md and every file it names, then start its exact next action: no reconcile checks, tests or READY TO RESUME round (owner, D-094 R109-R113)"; SKILL.md section F matches.
 - Realises "make it quicker and less token sends from where I left off" with the information transfer kept.
 - Nothing stays open (recorded rule; applies to future sessions).

ROW D-094-R110 — PASS
 - CLAUDE.md splits the routine: planned-handoff branch (no checks) vs "After a crash or forced stop:" keeping the original five numbered steps; SKILL.md section F mirrors it; PROGRAM_KNOWLEDGE.md D-070 line changed "only verifies+launches" → "only launches (no resume checks, D-094 R109-R113; same full handoff and prompt)".
 - R110's text was re-read in f0540a03 BEFORE the contract (requirements_reread audit entry at 19:14:51; content digest resynced) to match source-008; the owner's verbatim message in source-007 is unchanged (single capture commit f7914cc3a).
 - Nothing stays open.

ROW D-094-R111 — PASS
 - The owner's question ("how do we make it quicker/cheaper") is answered and logged at docs/back-and-forth-developer/2026-10-11-questions-and-answers.md section 17 ("How do we make the start of the next session quicker and cheaper?").
 - This task records the resulting routine in the instruction files; the return-to-owner artifact itself (chat + Q&A log) was written in f0540a03, outside this task's allowed paths.
 - Nothing stays open for the recording share.

ROW D-094-R112 — PASS
 - SKILL.md section F: "the prompt carries NO resume checks and no READY TO RESUME round ... the prompt and handoff otherwise keep all their information"; CLAUDE.md keeps "read the handoff and every file it names".
 - Faithful to the owner's correction: same prompt, full saved handoff kept; R109/R110 resynced to match.
 - Nothing stays open.

ROW D-094-R113 — PASS
 - CLAUDE.md: "no reconcile checks, tests or READY TO RESUME round (owner, D-094 R109-R113); do not begin untracked work" on the planned-handoff path; the checks remain only "After a crash or forced stop:"; SKILL.md section F scopes verify/reconcile/READY-TO-RESUME to the crash/forced-stop branch.
 - Faithful to "the checks, just you don't have to do, since we literally go from session to session"; the "do not begin untracked work" guard was added by [ORCH-CORRECTED per G3 code A1].
 - Nothing stays open.

(3) BINDING B1–B5
 - B1 PASS. All 49 D-094 rows and D-090-R639 carry M0-T193 in applicability.task_ids (verified by reading requirements.json at head). The M0-T193 binding was appended in the contract seam commit fc96fd9c (audit_log applicability_bound entry 2026-10-11T19:45:06 with the full row list; requirements.json changed in that commit). No row text was changed by this task — its three material commits (ea689ea0/a3690424/1dac23f2) touch only the seven allowed-path files, never a directive requirements.json. R109/R110 were re-read earlier in f0540a03 (requirements_reread audit entry; content digest resynced) and the owner's verbatim source-007 words are unchanged.
 - B2 PASS. directive_registry.sha256_text_artifact(D-094 requirements.json) = bae4d0cd78c523f20b3ab4f39a20ec4f169d0e105bae2884e0bdb9bb02c0e3a9 = manifest.requirements_content_digest_sha256.
 - B3 PASS. D-094 verification.json has one M0-T193 row (verifier="", 49 requirement ids, all state=pending); D-090 verification.json has one M0-T193 row (verifier="", id D-090-R639, pending).
 - B4 PASS. DirectiveRegistry.evaluate_task_refs(packet) → ok=True, applicable_ids == cited_ids (exactly the 50 ids), missing_ids=[], invalid_refs=[], unresolved=[].
 - B5 PASS. No other active-directive requirement is applicable-and-uncited for M0-T193 (missing_ids empty). Gates: G0 PASS (orchestrator, fc96fd9c), G2 PASS (orchestrator self-check, 4e92b20c), G3 PASS (product-design-director, 4e92b20c); both G3 reviewers (product-design-director design share, code-reviewer instruction-files share) returned PASS with delta attestations to 1dac23f2 in M0-T193-reviews.md. G2 and G3 share one content identity (reviewed_sha 4e92b20c; material files byte-stable to head). validate_directive_compliance.py --check exits 0 (direct exit code).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while the blob-level predicate holds: the seven allowed-path files keep their blob ids as at 72fe33cf (docs/design/ARCHITECT_PRESENTATION_CONTRACT.md, CLAUDE.md, .claude/rules/drawings-report-presentation.md, .claude/rules/frontend-web.md, .claude/rules/PROGRAM_KNOWLEDGE.md, .claude/skills/session-handoff/SKILL.md, project-control/reports/M0-T193-producer-report.md), the 50 bound rows' text is unchanged, and their M0-T193 applicability binding is unchanged.
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch ANY other file — other wave tasks under services/, apps/, packages/, docs/, .claude/ (files other than the seven above), their packets, gates, reports, and the directive bindings/verification rows of OTHER tasks; this task's own acceptance records (its gate/verification/evidence updates); and a merge of the main line that changes none of the predicate files. Such commits do not void this verdict.

(5) REQUIRED CORRECTIONS
 - None. No VIOLATED or UNVERIFIABLE row. Advisories only, non-blocking: (a) R639 — the orchestrator must read CI green at the exact accept/merge head (the 72fe33cf push CI was peer-cancelled); (b) R021 — the fixed label is "schematic, not to scale" (comma), a deliberate documented canonicalisation of the owner's "schematic / not to scale"; (c) R026/R049 details are carried forward to build tasks M5-T164/page tasks for enforcement.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not verify any BUILT report or website page: every D-094 row is judged only as a RECORDED RULE in the contract/instruction files; the page/website/PDF implementations are re-verified at their own tasks (M5-T165/T166/T171, M5-T164, M0-T194).
 - I did not run tools/test_directive_compliance.py or the full api suite (forbidden, time cost); I relied on validate_directive_compliance.py --check (exit 0), the clean working tree, and git-plumbing reads, with CI confirmation deferred to the orchestrator at the accept head.
 - I confirmed CI success only at submit head 4e92b20c (run 38171255530); the exact accept-head CI is the orchestrator's read.
 - The owner questionnaire lives outside git (lanes-runtime/owner-docs/OWNER_QUESTIONS.md); I read it read-only to confirm the H1-answered entry but it is not a committed repository artifact.

R008 RULING
 - D-094 R008 orders: (1) reconcile the research with the generated results before polishing conclusions; (2) redesign the summary and scenario template; (3) complete one spatial example; (4) apply the structure across the remaining scenarios and website. Source-002 R081 makes "rebuild the first page" the reviewer's concrete first next-pass step, and R039 says "continue unrelated presentation work while documents are unavailable". I am an AI agent; this is a sequencing ruling, not a human approval.
 - M5-T165 (page 1 rebuild): ALLOWED. It is exactly R081. The accepted evidence corrections R029-R035 (M5-T157/M5-T158) are already reflected, and the contract's rear-yard paragraph requires page 1 to read the 1.4.0 state as an OPEN CHECK naming 23-344(b) and (c)(3) with no conclusion — so polishing page 1 does not pre-empt the open rear-yard evidence (R037/R079 preserved). Condition: page 1 must present the rear yard only as the contract's open check (no conclusion) while M5-T163/M5-T176/M5-T167 remain open.
 - M5-T166 (dimensioned close-up): ALLOWED. The constraints close-up (R014/R074/R053) draws lot, neighbours, anchored dimensions with their basis, streets, north arrow and scale — none of which depends on the rear-yard conclusion. Condition: per R017, it must NOT render a rear-yard/setback AREA whose geometry/basis depends on the unresolved 23-344(b)/(c)(3) analysis (draw it only when established).
 - M5-T171 (website page-1 parity): ALLOWED. R096 requires the website and PDF to show the same figures and illustration; parity mirrors the redesigned page 1 (step 2/4) with the identical open-check wording. Condition: same as M5-T165 — the website must carry the rear-yard open check with no conclusion and must not state figures beyond the accepted result revision.
 - Overall: all three ALLOWED because they are presentation/redesign of already-reconciled or honestly-unresolved content; they do not "polish a conclusion" about the still-open rear-yard research, which the contract forces to display as unresolved.

END-OF-REPORT
```
