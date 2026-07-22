# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, hard rules, and workflow routes live in
`CLAUDE.md` and the specialist docs it routes to — not here.

**Verified base at `58432cff01c61251eeca944bfb76dd2203cd1c71`** (origin/main when this was written, after
the 2026-07-22 corrective/integration wave; `git fetch` and reconcile). Milestone **M0** active; M1
accepted; M2-T012/T013 accepted. Nothing Published/Verified; every R5 rule stays `needs_review`.
Checkpoint high-water reserved: **CP-0032 is reserved for M0-T019 — do not create one.**

## Merged this session (all owner-authorized; branches preserved, not deleted)
- **M4-T003** rules-engine correctness hardening — PR #78 (reviewed code `7051a7b`).
- **M0-T021** lock-verifier reproducibility fix — PR #80 (reviewed code `bd80e72`). Repaired
  `lock_tools.sh`/`lock_requirements.sh --check` (they compiled into a BLANK mktemp so uv resolved to
  LATEST → any upstream release, e.g. certifi 2026.7.22, deadlocked every PR). Fix seeds the committed
  lock as existing-output preference before the non-`--upgrade` compile. Age gate untouched.
- **M4-T002** rules-engine ↔ property-analysis integration (service layer) — PR #81 (reviewed product
  code `ff33ad2`, blob-verified on main). PR #79 was closed **superseded** by #81.

## AWAITING OWNER MERGE DECISION — M4-T004 (do not merge without authorization)
- **M4-T004** pre-endpoint fail-closed safeguards **FH-1/FH-2/FH-3** — **PR #82 OPEN**, base main,
  MERGEABLE. Reviewed code SHA **`3e45524`** (PR head adds gate-report/ledger markdown only, code
  byte-identical). **CI 12/12 green**; independent **G3/G4/G5 all PASS** at `3e45524`;
  152 rules / 742 full pytest green.
  - FH-1: `_valid_iso_date` true `datetime.date()` validation → impossible dates fail closed.
  - FH-3: `assert_not_verified` guards non-list `evaluations`/non-dict `family_coverage` (fail safe,
    never-Verified intact).
  - FH-2: `registry.detect_rule_conflicts` — strictly fail-closed same-family conflict detection
    (typed, deterministic, load-order-independent; no value; provenance preserved; PRR). **Never
    selects/ranks/merges/supersedes/reinterprets** (owner FH2-SPEC). Not a rule_series redesign.
  - Pre-merge checklist to run before merging (same as prior PRs): head unchanged, MERGEABLE, 12/12
    green, `3e45524..<head>` delta control-only, non-report code byte-identical to `3e45524`.

## Ledger lifecycle note (merged-but-not-accepted)
M4-T002/M4-T003/M0-T021 are merged and clean-gated but remain **pre-acceptance** in the ledger; M4
acceptance is coupled to **M4-T001's outstanding G6** (owner directive: do not manufacture G6 or accept
M4-T001). M4-T004 is `awaiting_gate`/95% with G3/G4/G5 recorded PASS, PR open. Reconcile these states
live; do not accept without owner authorization.

## Next task — rules-evaluation ↔ property-analysis API + existing property screen
Owner priority after M4-T004 merges: connect the M4-T001/T002 rules evaluation to the property-analysis
API and the existing property screen (the first PUBLIC-endpoint exposure of draft results). This task
**must fold in FH-4** (see `project-control/reports/M4-RULES-FUTURE-HARDENING.md`): route `as_of_date`
through `_valid_iso_date` in `detect_rule_conflicts` for belt-and-suspenders parity (already fail-closed
today). FH-1/FH-2/FH-3 are the other recorded pre-endpoint safeguards (delivered by M4-T004). Confirm the
exact task ID from the ledger; if none exists, create the smallest controlled task (never CP-0032).
Preserve: draft/needs_review honesty, provenance-fail-closed, uncertainty preservation, never-Verified;
frozen SHA + CI + G3/G4/G5 (+ human-walkthrough for UI) before merge.

## Frozen concurrent item — scheduled, owner-authorized only
- **M0-T019 / PR #64** OPEN, FROZEN at `39080822a361b6204813d2dcbd1f849b196100ea`, blocked only by its
  7-day dependency-age gate (unlocks **2026-07-22T06:10:00Z** — that instant may now have passed; verify).
  At/after it: rerun ONLY the failed CI jobs at that SHA; if green, run ONLY `ci-evidence-verifier`. Do
  NOT bypass the gate, merge, regenerate the lock, weaken policy, or advance CP-0032. Owner-authorized only.

## Preserved holds (do not violate)
- Nothing Published/Verified; every R5 rule stays `needs_review`; **M4-T001 not accepted** (G6 + B-010
  outstanding — block only publication/verification + final acceptance, not continued `needs_review`
  engineering).
- **CP-0032 / M0-T019** untouched. **Expansion-planning owner-review hold** (counter-notice §2) preserved.
- **Force-push is disabled** in this environment: rebases are published non-destructively to a NEW branch
  + NEW PR (old branch/PR preserved), per owner preference. Do not commit directly to main.

## Unresolved owner decisions
1. **Merge PR #82 (M4-T004)** — clean-gated, 12/12 green, awaiting authorization.
2. M0-T019 / PR #64 merge (after the 2026-07-22T06:10Z gate resolves).
3. Acceptance of merged-but-pre-acceptance M0-T021 / M4-T002 / M4-T003 (M4 coupled to M4-T001 G6).
4. Credentials B-001 Supabase (highest) / B-002 Render / B-004 Geoclient.
5. Survey M2-T014/T015/T016 planning-report dispatch hold; GDS/expansion + 3D holds — preserved.
