# Lane A — Engine: status

Updated by lane A only, after every task (lane prompts, shared rules).

| | |
|---|---|
| **State** | Active (lean lane process D-090; owner GO 2026-10-03, D-090-R087) |
| **Done** | **A-02** R6B draft rule tables (FAR 23-22, heights 23-432, corner coverage 23-362, rear-yard waiver 23-344(a), units 23-52) — merged PRs #262 + #269; all `needs_review`.<br>**A-03** Stop subtracting city-recorded building area; legacy subtraction behind a default-off flag, default answer "Remaining development capacity: Not confirmed" — merged PRs #253 + #282.<br>**A-01** Rule-coverage matrix (every R district × output × add-on + street-width source) — this PR `lane-a/A-01-rule-coverage-matrix` (built; awaiting independent review + owner merge). |
| **Next** | **A-04** Three-answer generator on the benchmark fixture (allowance, permitted envelope, building option). Needs B-01 (Lane B) and the M5-T125 contracts before it can be contracted/claimed. **A-08** (Pilot A candidates) depends on A-01 (now built) + B-01 and is held for owner Q1. |
| **Blocked by** | A-04: B-01 + M5-T125 contracts. A-08: owner Q1. Reviewer-paced: A-10 (wide-street apportionment legal ruling, Q12), A-11 (R6–R10 family completion), A-02 reviewed status (Q12). |
| **Open owner / reviewer questions** | 1. **A-01 add-on taxonomy (reviewer):** for R1–R5 the FAR rules surface the ZR 23-21 "qualifying residential sites" FAR column; whether that is the same add-on as the §6 "qualifying affordable or senior housing (City of Yes)" program needs reviewer confirmation (recorded `implemented_draft` with a note).<br>2. **A-01 R6B choice-of-bulk-rules (reviewer):** whether a "Quality Housing vs height factor" choice applies to the contextual R6B district (recorded `needs_reviewer`, the matrix's one such cell).<br>3. **A-01 wide-street non-applicability (reviewer):** for non-wide-street-conditional districts the matrix records `not_implemented` (never asserting `not_applicable` without a reviewer legal reading); the captured sources documenting no wide-street increase are cited in the cell notes.<br>4. Standing: nothing in A is `reviewed`; `implemented_draft` is the ceiling (D-090-R010). |
