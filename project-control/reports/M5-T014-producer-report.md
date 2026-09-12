# M5-T014 producer report — compare-screen empty-from assertion repair

Producer: qa-engineer/orchestrator. ENGINEERING_RELIABILITY_STANDARD §1 (diagnosis below),
§2 (one test function, one file), §3 (red externally recorded; green is the CI web-e2e job).

## Diagnosis (from primary evidence, no local execution possible)

The CI vitest DOM diff (run 34669078475, and identically on every web-e2e run since the
M5-T004 acceptance) shows the blanked rule rendering:

    rule id not stated (version not stated) - no effective dates are recorded for this rule

while the assertion expects the per-slot label "from not stated". Mechanism, verified in
source: the committed fixture (packages/contracts/fixtures/valid/scenario/
no_scenario_conflict.json) gives BOTH competing rules `effective_from: "2024-12-05"` and
`effective_to: null`. The test blanks `rules[0].effective_from` to "", so BOTH dates land in
the absent class (`isAbsent` treats null and "" alike) and NoScenarioBlock's DELIBERATE
both-absent collapse renders - a design the ADJACENT PASSING test ("reports recorded dates and
NEVER characterises a draft rule as in effect") explicitly asserts, with the component comment
recording why ("no effective dates are recorded" instead of "from not stated, to not stated"
twice over). The test constructed a both-absent state but asserted the mixed-case phrasing:
a TEST defect in accepted M5-T004 work; the component is correct and untouched.

## The repair (intent-preserving, one test function)

`rules[0].effective_to = rules[1].effective_from as string;` - a real end date DERIVED from
the sibling rule's own fixture value (never an invented literal), inserted after the blanking
so rule[0] becomes (from="", to="2024-12-05") and renders through the per-slot branch:
"recorded effective dates: from not stated, to 2024-12-05". The assertion "from not stated" is
now both correct and meaningful: it fails again if the component ever stops labeling an
empty-string date. All three original expectations remain; nothing deleted or relaxed; a
comment records the mechanism.

## Red/green record (§3.1)

RED: externally recorded on EVERY CI web-e2e run since the M5-T004 acceptance (1 failed /
389 passed; latest 34669078475 with the full expected/received DOM diff quoted above). No
local red run exists or can exist: the thin client has no node_modules by policy
(docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md).

GREEN: the CI web-e2e job on the pushed head is the sole executable authority - expected
vitest 390/390 (389 + this one), Playwright unchanged, making web-e2e green for the first time
since the M5-T004 acceptance and leaving only the two owner-gated CI reds (npm audit RCE
authorization; control-plane digest normalization decision).

## Scope

Exactly one test function in one file + this report. No component, lib, e2e, fixture, or
sibling test change (the both-absent collapse stays accepted M5-T004 behavior; reopening
accepted work is forbidden - this is the post-acceptance-discovery follow-up).
