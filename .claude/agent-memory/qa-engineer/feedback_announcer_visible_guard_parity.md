---
name: announcer-visible-guard-parity
description: When a packet adds a screen-reader announcer branch mirroring a visible guard, verify the announcer replicates every correspondence check the visible guard applies with the same inputs available
metadata:
  type: feedback
---

When a web packet adds an aria-live announcer branch that is meant to MIRROR a visible
component's guard (e.g. rule-evaluation.ts `announcementForRuleEvaluation` substitution
branch mirroring `AnalysisIdentityNotice` `stampLegitimate`), the announcer must replicate
EVERY correspondence check the visible guard applies **using the inputs it actually has**.

**Why:** M5-T063 (G4, 2026-09-20). The visible `stampLegitimate` requires
`substitution.entered_bbl === evaluated_input.bbl` (and === requestedBbl); the new announcer
branch only required both BBLs present + `analyzed_bbl !== entered_bbl`. The announcer has
`document.evaluated_input.bbl` available but did NOT check `entered_bbl === evaluated_input.bbl`.
Result: a shape-valid doc where evaluated_input.bbl === opened BBL but the stamp names a
different entered_bbl makes the announcer narrate "the condo billing lot {entered} you entered"
(a lot never entered, shown nowhere) while the visible surface renders nothing — a screen-reader
vs visible divergence AND a false "you entered" claim. This directly violated the packet's own
HJ-3 goal (announced text must not diverge from visible). The visible component had an explicit
test for exactly this doc shape (analysis-identity-substitution.test.tsx:142) but the announcer
had no analog — so the divergence was unimplemented AND untested.

**How to apply:** For any announcer/visible pair, enumerate the visible guard's clauses, then
check each is reproducible from the announcer's inputs; a missing reproducible clause is a
required correction. Demand a negative test: a NON-corresponding stamp must announce generically.
Contract validators here are positive-shape-only ("no legal/substitution meaning judged") — they
do NOT enforce entered_bbl===evaluated_input.bbl, so the divergent doc IS reachable as
kind:"evaluation". Related: [[probe-separator-deleting-normalizations]].
