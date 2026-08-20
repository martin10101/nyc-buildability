# D-021 owner report — one bounded product task delivered (M5-T002), PR unmerged

**Date:** 2026-08-20. **Directive:** D-021 (captured verbatim at
`project-control/directives/D-021-resume-product-r5-pilot-next-unit/source-001.md`).

## Plain English: what you can now do that you could not before

Your platform's scenario engine (M5-T001) existed only as invisible internal code. This task makes it
real for a person: with the internal flags on, an analyst looks up a real R5 tax lot on the Property
screen and — below the official facts — sees a **draft scenario**: the calculated draft
zoning-floor-area cap for that lot (e.g. "15,000 sq ft" for a 10,000 sq ft R5 lot), labeled DRAFT
everywhere, with the rule citation (ZR 23-21), the source provenance drill-down, a coverage map that
says exactly what is NOT covered (height, setbacks, yards…), and the professional-review disclaimer.
When the platform cannot honestly produce a value (unsupported district, missing data, split lot /
spatial uncertainty, conflicting rules, malformed data), the analyst sees a plain-language explanation
of WHY there is no number — never a guess. In production nothing changes: both flags are off by
default, and the endpoint is invisible (a generic 404) until you decide otherwise.

## The one unit chosen, and why it was the only clear one

Selected: **M5-T002 — internal flag-gated `GET /api/v1/properties/{bbl}/scenario` + flag-gated
property-screen scenario surface** — the exact "future rule-evaluation→scenario endpoint" slice that
the M5-T001 review records reserved, closing its two assigned security follow-ups (validate-before-emit
FH-M5T001-S1, bounded-depth guard FH-M5T001-S2). Alternatives were all non-ready: yards/coverage rule
families are recorded SUPERSEDED pending M3-T004 + the zoning-lot model; M2-T019 and the M3 corpus
chain are blocked by B-001 (Supabase credential — yours); M0 backlog is control-plane work your
directive excludes; M4-T007/T008 are already accepted. Full analysis:
`project-control/reports/D-021-bootstrap-evidence.md`.

## Verification (independent, evidence-based)

- **Producer:** unnamed backend-engineer agent in an isolated worktree (2 content commits: 8872438,
  31e652a). Producer ≠ reviewers ≠ verifier throughout.
- **Gates at the reviewed identity:** G0 readiness PASS; **G3 code review PASS** (code-reviewer;
  0 blocking findings); **G4 QA PASS** (qa-engineer; AS-1..AS-10 coverage matrix all COVERED;
  0 blocking); **G5 security PASS** (security-reviewer; 0 blocking; posture strengthened vs the
  accepted rule-eval endpoint); **human-journey walkthrough PASS** (honesty/a11y/recovery).
  Reports: `project-control/reports/M5-T002-G3-code-review.md`, `-G4-qa-review.md`,
  `-G5-security-review.md`, `-human-journey-walkthrough.md`.
- **Tests:** 33 new API tests (flag-off matrix, verbatim-cap equality against the canonical trace,
  every no-scenario family, depth-bound/RecursionError, leak canaries, POST/query injection, determinism);
  tests/api 144/144 green (zero existing tests touched — all changes to existing files are additive);
  new web unit/component tests + 2 Playwright journeys.
- **CI:** ALL 20 required contexts green on the PR head, including `web-e2e` (first real execution of
  the web tests + both new Playwright specs) and `web` (lint + typecheck + build).
- **Directive compliance:** all 25 D-021 requirements independently verified PASS by the
  directive-compliance-verifier at HEAD 2fee786 (14 task rows recorded in the D-021 directive
  directory's `verification.json`; the full per-requirement report, including the 11 session-governance
  rows, is preserved verbatim at `project-control/reports/M5-T002-directive-verification.md`).

## Holds — all preserved

D-013-R060 is still PENDING; the controller-update bundle was never run; limited-auto was never
enabled; nothing under tools/agent_supervisor/**, protected controller config, model-selection config,
the context pipeline, or the MCP policy changed (reviewer-verified by diff); no test, review, CI,
security control, or branch protection was weakened; unrelated files preserved (tree was clean); the
autonomy-activation handoff was neither advanced nor dismantled. The MCP roster was verified EMPTY at
session start (fresh process at the worktree root) — no stop condition.

## Merge identity (NOT merged — merging needs your separate authorization)

- **PR:** #241 — https://github.com/martin10101/nyc-buildability/pull/241 (OPEN, mergeable, DO-NOT-MERGE
  banner in the title/body)
- **Branch:** `task/M5-T002-scenario-endpoint` (base `main` @ d8b3899)
- **Reviewed content identity:** commit `31e652aff0b7689cc22c46376d42a12f8c9eab82` (all product code);
  every later commit on the branch is control-plane records only (gates, verification, reports) — the
  reviewed code is byte-identical at the final head.
- **Exact merge identity = the PR head commit at merge time**; the final pushed head SHA is stated in
  the session's closing report and visible on the PR. Merging PR #241 is the single action that ships
  this unit to main.

## Ledger honesty: why the task shows awaiting_gate, not accepted

`accept()` fail-closes unless every dependency is `accepted`. M5-T002 depends on M5-T001 and M4-T005,
which sit at awaiting_gate with all their gates PASS but are barred from acceptance by the **G6
qualified-human legal approval** owed on the M4 draft-rule chain (M4-T001) — an owner-side hard stop
your directive explicitly preserves ("do not weaken reviews"). So M5-T002 ends in the same state as the
whole draft-rule chain: fully implemented, independently reviewed PASS on every gate, all 25 directive
requirements verified, CI fully green, PR open and unmerged — with ledger acceptance mechanically
parked on the same G6 legal approval. No control was weakened to force a different label. The
accept() dry-run refusal reasons are preserved verbatim in
`project-control/reports/M5-T002-accept-dryrun.md`.

## What unblocks next (owner actions, when you choose)

1. **Merge PR #241** (your call; Tier-A-shaped merge but held by D-021-R022 until you authorize it).
2. **G6 qualified-human legal review** of the M4 draft-rule chain — the single hold parking acceptance
   of M4-T001..T006, M5-T001, and M5-T002.
3. **B-001 Supabase credential** — unblocks the M3 corpus chain and M2-T019.
