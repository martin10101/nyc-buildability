# G3 Gate Report - M0-T004 (recorded by orchestrator from code-reviewer return, ADR-005)

Reviewer: code-reviewer | Producer: backend-engineer | Head reviewed: 429c575 | Date: 2026-07-14

Verdict: PASS. Scenarios S1-S5 all PASS on independently reproduced evidence
(gh run view for all 5 CI runs; artifact-dir probe; repo-wide secret grep;
byte-level revert verification; disk 5.19 GB >= 4 GB floor).

Defects: D1 MEDIUM provenance schema under-enforces PRD s9 mandatory fields
(dataset_version, confidence, user_confirmed_or_overridden, conflict_status;
provenance_ref optional) - draft-labeled, MUST fix in M0-T009, would be HIGH if
final. D2 LOW invented enums (borough spellings, conflict resolution/status)
and permissive BBL pattern - validate against real connector outputs at
M0-T009. D3 LOW contracts CI job validates parse+keys only, not meta-schema -
upgrade at M0-T009. D4 LOW disclaimer apostrophe glyph differs from PRD s29.
D5 LOW root README stale (says three jobs / npm install; actual four jobs /
npm ci); contracts README key list stale.

Observations: bot lockfile commit did not itself trigger CI (validated by next
run); no web unit tests (disclosed, agreed scope); Node 20 deprecation
annotations are upstream.

Follow-ups: (1) M0-T009 must fix D1/D2/D3; (2) trivial doc fixes D4/D5;
(3) orchestrator records this gate.

Full reviewer return preserved in the orchestrator conversation of 2026-07-14;
scenario evidence table reproduced from it above.
