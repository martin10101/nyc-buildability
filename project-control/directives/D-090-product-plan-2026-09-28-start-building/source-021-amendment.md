# D-090 source-021 (amendment): owner message 50, 2026-10-04 - the owner's reviewer's third check (through integration 7275e463), forwarded

Captured 2026-10-04 by the orchestrator (Claude Code session 0ba6d6a3-f9a0-4ebc-95d9-610739d030b5, model claude-fable-5-1) from the saved session transcript `~/.claude/projects/-root-project-nyc-buildability/0ba6d6a3-f9a0-4ebc-95d9-610739d030b5.jsonl` (line 4914, uuid `d9d2f79d-80e9-4192-a2bd-041d3aafd8c1`, a mid-turn `queued_command` attachment). A script copied the attachment's raw prompt text; nothing was retyped. It is complete and byte-identical to the transcript except for the blockquote prefix ("> " on every line, ">" alone on an empty line); the raw text's SHA-256 is `f3b47a7c804d6e2708737560b7155ed6f5fb0c51467de36042e27de07c4c98a1`. Times are the transcript's UTC timestamps. Message numbers continue from source-020 (message 49). Frozen base at capture: `53ec5343` (the source-020 branch head; this capture stacks on sources 019 and 020).

The owner forwarded their reviewer's third read-only check, run through integration head 7275e463 (PR #397 merge): five items PARTLY DONE, the pending-approval checks DONE. Most findings repeat sources 019/020 and are already bound to R117-R127; the new facts below get their own rows.

## Owner message 50 (verbatim)

Transcript timestamp 2026-10-04T03:54:54.625Z.

> Worked for 24m 15s
>
> Five items are PARTLY DONE; the pending-approval checks are DONE. I checked source, actual diffs, review comments and Actions results read-only through integration 7275e463. PR descriptions were checked against that evidence.
>
> Item	Verdict	Evidence checked	Overstatements / gaps	Open questions for owner
>
> 1. Accurate wording — R106	PARTLY DONE	#386, merge 37a8813c; walkthrough, address harness, _benchmark_inputs, route registrations and panel imports. Synthetic address, hard-coded inputs and absent results route are correctly disclosed.	“City-data pack flows through” the engine overstates the connection: separate fixture inputs bypassed the study adapter. “No prior task wired a real address→BBL step” is false; Geoclient and its route exist. #383’s title/body still say “one complete request.”	None needed to correct these factual statements.
> 2. Height — R107	PARTLY DONE	#388, exact 55a66bf5; finding, pinned §23-431/432/433, building_option.py, envelope serialization and height tests. Four tests pass; removing computed-note logic makes two fail. Draft note uses actual numbers; envelope gives 30/45/55 standard, 30/45/65 qualifying. PR remains OPEN, 46 checks green.	§431/433 HTML hashes reproduce; §432 does not: pinned 06ca2245…, current 4abaa149…, although operative text/R6B row match. Finding says “COMPLIES” and “would misstate the law.” Computed note exists internally but is dropped before the results document.	Qualified reviewer: which §23-431 paragraph governs this lot? Separate yes/no on corrected #388.
> 3. Scope — R108	PARTLY DONE	Merged #387/#389; schema, Python constants, tax-lot-scope.ts, fixture and snapshots. Strings match exactly; lot identity and unconfirmed whole-site/remaining capacity are correct. Open #392 0e3b083c, cards #395 eec67cf0, drawings #398 bf341c40 inspected.	Merged snapshots do not implement scope in drawings. Engine/cards/drawings remain unmerged; current #395/#398 checks are unfinished. Five conditions have basis words, but hard-coded special-district and special-density assumptions are omitted. Latest cards change now shows assumptions openly.	Yes/no on #392 after omissions are corrected; #395/#398 need review and green checks.
> 4. One journey — R109	PARTLY DONE	#386 journey: all seven links contain proven/missing/smallest-task fields. #390 08ed12d6: injected geometry seam, no live binding, production unchanged. #391 71512237: inert existing_building contract slot; no engine file changed.	Geocoder-choice blocker ignores existing Geoclient wiring. “AutoCAD-opening” exceeds tests, which explicitly prove structure only. Claimed exact keep/remove order conflicts with Wave 1 and already-merged scaffolding. Lane A input-field work is incorrectly marked as needing no owner decision.	M1-05/Q1/Q12, E-02, Q4 and B-001 remain decisions. No repeat geocoder choice is justified by this evidence.
> 5. Pending approvals — R110/R111	DONE	#369 6cf97a04, #377 12bbdb8c, #382 ed984b30: all OPEN, exact-head PASS comments and 46/46 successful checks. Diffs respectively change option math, add-on math and pinned legal source text.	PASS reviews are recorded through a shared GitHub account; GitHub alone cannot authenticate separate reviewer identities. Green checks do not establish zoning correctness.	Explicit, individual yes/no for #369, #377 and #382.
> 6. CI proposal — R112	PARTLY DONE	#385, merge 1f73e105; inspection document, workflows and 2026-10-03 Actions inventory. 68 disappearing push runs per workflow, retaining 31 candidate pushes and 66 PR runs, reproduced. Coverage matrix exists; Windows causation is labelled a hypothesis with an unrun experiment. No workflow file changed.	“Single cost” omits loss of raw-head testing on open PRs. Scheduled workflows perform dependency audits, not every CI job. Automatic revalidation after base advancement is false: #369’s PR run remained old while integration advanced. “Every push” policy is narrowed.	Accept or reject the coverage/policy change after accurate disclosure and clarification of how fresh-base testing is enforced.
>
>
> The two scope strings are byte-exact across the checked schema, Python constants and web constants:
>
> Remaining development capacity: Not confirmed
>
> Needs verified zoning-lot boundaries and existing zoning floor area.
>
>
> The narrow height conclusion is a fair draft reading of the captured provisions: the setback trigger concerns walls above maximum base height, and the relevant minimum-wall clauses accommodate shorter buildings. It does not establish this lot’s compliance. 
>
> Repository defaults keep LANE_A_ENABLED through LANE_E_ENABLED and INTERNAL_STUDY_READ_ENABLED false; render.yaml contains no enabling overrides. Deployed environment overrides cannot be established from repository evidence. The blanket “nothing claims a legal determination” statement nevertheless overstates matters because the height finding uses “COMPLIES.”

## Reading

| Reviewer words (forwarded by the owner) | Requirement |
|---|---|
| Item 1: "#383's title/body still say 'one complete request.'" | R128 (obligation) |
| Item 3: "Five conditions have basis words, but hard-coded special-district and special-density assumptions are omitted." | R131 (obligation; makes R119's "every assumed input" explicit) |
| Item 4: "Lane A input-field work is incorrectly marked as needing no owner decision." | R129 (obligation) |
| Item 6: "Automatic revalidation after base advancement is false: #369's PR run remained old while integration advanced." / owner question: "clarification of how fresh-base testing is enforced" | R130 (obligation) |
| Item 1 "flows through" / Geoclient; item 2 COMPLIES, §23-432 fingerprint, note dropped; item 3 drawings/cards unmerged at check time; item 4 geocoder blocker, AutoCAD wording, exact order; item 5 shared-account identity; item 6 single cost, scheduled audits, policy narrowing | already bound: R117, R118, R119, R120, R121, R122, R124, R126 (no new rows) |
| Owner-question column (qualified reviewer on §23-431; separate yes/no on corrected #388; yes/no on #392 after omissions; M1-05/Q1/Q12, E-02, Q4, B-001; individual yes/no for #369/#377/#382; accept or reject the CI change after disclosure) | already bound: R123, R125 (no new rows) |
| "The two scope strings are byte-exact ..." / "The narrow height conclusion is a fair draft reading ... It does not establish this lot's compliance." / "Repository defaults keep ... false" | confirmations of R038, R107/R118 and R114 evidence (no rows) |

- **Orchestrator's readings (not owner wording):** (1) R130's "how fresh-base testing is enforced": today it is the manual Option B rule (merge the integration branch into a stale PR branch, prove the merge empty, let the new head's PR run go green before merging); GitHub re-runs pull_request checks only on a push to the PR branch. (2) R128 is applied as a metadata edit of the merged PR (title and body) with a dated correction note, since the merged commit itself is immutable.
