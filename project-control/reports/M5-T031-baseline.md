# M5-T031 baseline and failure-surface inventory

Base: `780dccf1e95a6ede2051b334ed99e0340ebce914`; main remains `d8b3899f61efa6620e18a26541ced96020f5bef9`. Fresh cloud checkout, no existing product work in flight in this checkout. Legacy controller tasks and B-001/B-010/B-011/B-024 remain untouched. Session handoff is older than ledger: M5-T029 and M5-T030 are accepted.

## Observed user journey (read-only live browser, 2026-09-15)

1. Opened the live frontend, selected Open workspace, typed `1279 37th Street Brooklyn`, selected exact suggestion `1279 37 STREET Brooklyn · 11218`.
2. Address resolved to BBL `3052960043`, BIN `3340270`; continued with this lot. Heading retained the searched address and identified PLUTO representative address `3622 13 AVENUE`.
3. Overview returned `No supported cap`; lot area 2400, building floor area 6271, number of floors 3. Expanded result scope: `rule_evaluation fail_safe_reason: spatial_intersection_absent`.
4. Property facts → Building displayed `Built FAR 2.61`. This value was correctly labelled; no swapped-residfar defect was reproduced.
5. Evidence → Maximum residential FAR displayed original field `residfar`, original value `3.00000000000`, normalized value `3`, PLUTO 26v2, captured `2026-09-15T22:40:50Z`.
6. Scenarios returned no supported cap and no supported estimate of the recorded-data difference. The existing frontend heading `Unused draft zoning floor area` overstates the backend's recorded-data-comparison semantics.

## Causal clusters and boundaries

| Cluster | Cause supported by observation/code | Owning boundary | Treatment |
|---|---|---|---|
| Development information hard to find | Overview emphasizes existing building area/floors; residential reference FAR is only in Evidence; Zoning omits a development summary | Frontend composition | M5-T031 makes development limits first, existing information collapsible, source detail one action away |
| Reference/built/evaluated values easy to confuse | Separate source facts are correct but scattered; overly strong reference label and recorded-data-comparison heading | Frontend labels and shared summary | M5-T031 preserves values and gives each meaning an explicit place |
| No calculated result on real parcel | Live evidence lacks spatial_intersection; engine refuses to infer a district | Backend/deployment and rule coverage | Report as existing gap; do not bypass checks or label the frontend fix as numerical coverage |
| Routine validation depends on client | Owner asks internal testing across residential district contexts | Validation workflow | M4-T022 independent official-source matrix and real-parcel sample; formal G6 stays distinct |

Hypothesis for the frontend cluster: a shared development summary sourced from canonical profile/evaluation/scenario fields can make the relevant distinctions visible without changing any number or rule. Falsifier: a valid source/evaluation field cannot be recovered unambiguously, or the presentation loses a conflict/missing state. Such cases must remain explicit instead of selecting a convenient value.

Known source mapping was present in the accepted baseline; no recent arithmetic change was implicated in the observed FAR concern. Variant sweep includes Overview, Zoning, Scenarios, Report and comparison headings. Existing source links, address continuity, identity checks, flags and complete evidence must remain available.

No timing or universal correctness claim is made. Numeric source correctness, UI visibility and completed buildability calculation are separate outcomes.
