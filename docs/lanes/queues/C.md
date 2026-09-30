# Lane C — Contracts, study and integration: queue

Ordered: take the top unblocked item. Built from `docs/lanes/RECONCILIATION.md` (partial and missing items only) under the derived lane plan `docs/lanes/PARALLEL_BUILD_PLAN.md`. Each item becomes one ledger task `M<x>-T<n>` that cites D-090 and the plan ID; its "Done when" is the plan's text unless marked *derived*. Waves: 1 foundations · 2 Milestone 1 + 2 · 3 breadth and parity (plan §11b: never delays Milestone 1). Owned by Lane C; the lane updates only `docs/lanes/status/C.md`.

Nothing here starts before the owner's GO (D-090-R007).

| # | Plan ID | Task | Done when | Depends on | Blocked by | Wave | Size |
|---|---|---|---|---|---|---|---|
| C-01 | M1-01 | Independent review of RECONCILIATION.md "§10 claims check" (the producer never verifies its own work) | M1-01: Every §10 claim has a file:line reference or is corrected | — | — | 1 | S |
| C-02 | M1-02 | Read-only build-info route: deployed commit and boolean flags (no secrets); record the deployed SHAs and flags | M1-02: Deployed SHAs and flags recorded | — | — | 1 | S |
| C-03 | M1-09 | Wire the Wave-0 contracts: study, site_fact, results, report_model, export_record into typegen and the runtime bundle; server-side validation at the producers | M1-09: Valid and invalid fixtures pass and fail | M5-T125 contracts | — | 1 | M |
| C-04 | M1-06 | M1-06a server side: reject example values in real-property requests (caller-attested lot area / district / street class on proposal-checks and max-envelope); unknown street width reads "Unknown" (or both results), never the narrow row silently | M1-06: No example values in any real-property state, request or report | — | — | 1 | M |
| C-05 | M1-10 | One study store for every surface (web lib/study): the dashboard and any remaining screen read the same study; options independent | M1-10: All surfaces agree; editing one option leaves the others unchanged | C-03 | Q4 decides how many screens it serves (not the store itself) | 1 | L |
| C-06 | M1-11 | Revisions and dependency-based invalidation: site change → every dependent option result out of date; option change → that option only; new rule version → marks users; late responses never overwrite newer | M1-11: §9 invalidation rules pass their tests | C-05 | durable storage B-001 / Q7 for saved revisions | 1→2 | L |
| C-07 | M1-08 | Labeled input channel to the evaluator: entered, assumed and survey values stay distinct from city facts | M1-08: Reviewed contract keeps entered values distinct from facts | C-03, B-02, A-01 | — | 1 | M |
| C-08 | M1-12 | Wire engine → API → dashboard for the pilot: mount a results route behind flags (flip the tests that assert it stays unmounted), send the lot BBL and lines | M1-12: Outputs equal the golden record | A-04, C-07 | golden record M1-05 (Q1, Q12) | 2 | L |
| C-09 | M1-18 | Compare backend: identical rows for any two options of a study | *derived:* Feeds D-10 | C-05, A-04 | — | 2 | M |
| C-10 | M1-26 | CI: run the orphaned suites (validate_contracts tests, residential_validation, gate_runner, authority_policy) and add the validation-suite job | *derived:* The suite runs in CI (Tier B CI change, specialist review) | — | — | 1 | S |
| C-11 | M1-20 | Recorded-fixture CI journey: address → lots → results → export on the pilot fixture (harness mounts the needed routes) | M1-20: Recorded-fixture CI journey from address to export passes | C-08, E-03, E-04 | — | 2 | M |
| C-12 | M2-03 | Two-pilot regression in CI | M2-03: Both pilots pass in CI | C-11, D-14 | — | 2 | S |
| C-13 | — | Docs hygiene: "superseded — see the 2026-09-28 plan" banners on the conflicting docs listed in DOCS_INDEX.md | *derived:* No lane can follow a conflicting instruction by accident | — | — | 1 | S |
| C-14 | — | PRs #243–#246 (merged 2026-09-25/26 outside the ledger): reconciliation record | *derived:* Recorded as the owner decides | — | owner: how #243–#246 were authorized | 1 | S |

## Blocked by owner or reviewer

- **C-05** — Q4 decides how many screens it serves (not the store itself)
- **C-06** — durable storage B-001 / Q7 for saved revisions
- **C-08** — golden record M1-05 (Q1, Q12)
- **C-14** — owner: how #243–#246 were authorized

