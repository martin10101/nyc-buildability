# Live-case regression properties (D-073-R005)

Standing record for the four real properties where the deployed analysis stopped during the
external (Codex) product review, kept as explicit regression cases. Rule (D-073-R005): each
case needs the precise stopping condition, its evidence, the affected calculations, and the
capability or information that resolves it; cause classes are distinguished (source
uncertainty / split zoning vs property-identity connection vs unsupported rule coverage vs
data-geometry problems vs implementation defects). A refusal can be CORRECT — protective
checks are never relaxed to produce more successful-looking results; fixes are new
capability, with a defensible basis, preserving protection against unsupported conclusions.

Status vocabulary matches the discovery backlog (D-069). This file records; the ledger and
backlog queue the work.

| # | Property | Known cause class (evidence) | Affected calculations | Resolving capability | Status |
|---|---|---|---|---|---|
| 1 | 1279 37th Street, Brooklyn | Cause class NOT yet pinned from repository records — the recorded facts are the built-FAR 2.61 vs residential-reference 3.00 distinction (labels corrected in an accepted packet); the review reports its live analysis stopped | Complete per-property computed allowance (FAR chain) | Pin the exact stopping condition from a live re-run + server logs, then classify | OPEN — investigation owed in the validation packet |
| 2 | 298 Wallabout Street, Brooklyn (BBL 3022647515) | Property-identity connection: condo BILLING lot (condono 1313, 75xx billing lot) absent from ZTLDB by design; the app honestly reports no data (DB-002; M5-T033 owner-confirmation; docs/WORKING_KNOWLEDGE.md walkthrough notes) | Zoning-lot lookup and everything downstream | Condo billing-lot → base land-lot resolution through authoritative records (ACRIS/DOF), BEFORE zoning-lot lookup; a D-059-R007 benchmark hard class | OPEN — capability packet (DB-002), priority set by D-073-R008 |
| 3 | 401 Columbia Street, Brooklyn | Cause class NOT yet pinned from repository records (candidate classes per the review: split zoning or boundary confidence) | Per-property computed allowances | Same investigation as #1; if split-zoning: refusing to guess is CORRECT (precedent DB-001, 350 Fifth Ave verified against city records); resolution = split-lot apportionment capability (ZR 77-series), legal research first | OPEN — investigation owed in the validation packet |
| 4 | 69-02 Kessel Street, Queens | Cause class NOT yet pinned from repository records (candidate: boundary-confidence limit) | Per-property computed allowances | Same investigation; boundary-confidence cases get data/logic investigation BEFORE any threshold change proposal | OPEN — investigation owed in the validation packet |

Standing findings that bind any resolution work:

1. A stopped analysis is not automatically a defect: the split-zoning refusal was verified
   correct against city records (DB-001). The correct-refusal outcome must stay a supported,
   explained product state: the interface owes the user WHAT condition stopped the answer,
   WHICH conclusions are affected, and WHAT would resolve it.
2. Prohibition (owner, D-073 item 5): protective thresholds are never relaxed merely to
   produce more successful-looking results.
3. These four cases join the fixed validation collection (D-073-R004) as
   expected-refusal / expected-specific-outcome rows where their cause class is confirmed;
   none is required to become a positive result in the street-data milestone.

Next action: the validation-collection packet (contracted after M5-T035 acceptance) runs the
four live re-runs, pins each stopping condition with server-log evidence, fills the cause
class column, and registers each case in the validation collection with its expected outcome.
