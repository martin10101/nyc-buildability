# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff - seq 98: 184 accepted; address-entry Packet 1 (M5-T015) ACCEPTED end-to-end; Packet 2 next

Generated 2026-09-12 ~02:45 ET by session `5967607e-525a-430f-b258-e908e6db62e6` (context refresh
checkpoint after the M5-T015 acceptance). Root `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch
`candidate/D-024-mrl-option-b`, HEAD `c9c4ce16` **pushed** (origin same). Dirty: only untracked
`.claude/agent-memory/qa-engineer/*` and `scratchpad/` (left per policy). `main` untouched at
`d8b3899f`. PR #241 remains OPEN and MUST NOT be merged (owner hold).

## STATE (verify live; ledger wins)

1. **Accepted = 184.** This session (resumed from seq 97) landed SEVEN acceptances: M2-T021 (178,
   geoclient connector rework), M4-T010 (179, citation digest schema+loader), M4-T009 (180, R1-R12
   FAR rules + AS-5), M4-T011 (181, cross-suite consumer repairs), M2-T022 (182, address-resolution
   API endpoint), M5-T014 (183, compare-screen test repair — web-e2e green for the first time since
   M5-T004), **M5-T015 (184, address-entry UI Packet 1)**. The M4-T010/M4-T009 dependency edge to
   G6-parked M4-T001 was removed by owner decision D-039 ("Correct both", T007/T008 precedent);
   the G6 hold itself is UNTOUCHED.
2. **M5-T015 arc (the current house pattern for a UI packet, reusable):** contract `428989b1` →
   producer material `352aa9de` (address-api.ts pair-matrix client with rawStreetName verbatim
   re-query member; AddressResolutionScreen PropertyLookup-clone machine + every spec-§2 card with
   an honest Packet-2 stub; AddressForm connector-is-authority; SuggestionChooser caller_selects
   literally; additive announce.ts; flag-gated PropertyLookup mount, flag-off byte-identical) →
   one CI cycle fixed two test-mechanics defects `6787445e` → submit `9f679ff7` → four-reviewer
   wave (G1/G4/G5 PASS; G3 PASS with REQUIRED F1 heading-order correction) → bounded correction
   `9edfbc73` (F1 h1/h2 swap flag-conditional, F2 pick-focus, F3 invalid_input edit affordance,
   G1-D2 754-char raw≠bounded discriminating fixture, report §8 corrections) → all four DELTA
   attestations PASS → gates recorded `de3195d5` → awaiting_gate→rework→resubmit identity restamp
   `e989db84` → DCV ROW-SUFFICES → ACCEPTED `c9c4ce16`. CI evidence: run 34677835271, web+web-e2e
   SUCCESS, 32/32 address tests, 27/27 files. All reports incl. delta attestations preserved
   verbatim under `project-control/reports/M5-T015-*`.
3. **CI posture:** the ONLY red jobs are the two standing owner-gated ones — web-dependency-security
   (npm audit / Next.js RCE fix awaiting owner authorization) and control-plane (directive-registry
   CRLF digest normalization decision). Everything else green, including web-e2e.
4. **Deferred-with-concurrence items for Packet 2** (recorded in M5-T015 producer report §8):
   extract outcome cards from AddressResolutionScreen (it is 754 raw lines, modularity WARN-only);
   G5 F-1 frontend `INTERNAL_RULE_EVAL_UI` vs backend `INTERNAL_RULE_EVAL_ENABLED` flag-name
   divergence (surface to owner); hostile-resolved-card fixture + per-state body-copy assertions;
   dual-primary-button hierarchy resolves when resolved routes to Confirm.

## NEXT ACTION (in order)

1. **Contract M5-T016 = address Packet 2**: AddressConfirmCard (canonical address large, BBL, ZoLa
   deep-link, lot-outline placeholder), "Continue with this lot" handoff to
   `/property/confirm?bbl=<canonical>`, "Not my property" back to entry. BEFORE contracting:
   confirm the exact ZoLa URL path shape (spec flagged assumption (a)); ZoLa href built ONLY from
   client-re-validated `validateBblInput` canonical BBL — adversarial fixture required; provenance
   disclosure (source_facts/provenance render sites) belongs here; human-journey walkthrough (G3)
   belongs here. Design spec: `docs/design/address-entry-confirm-design-spec.md` §2/§4/§6-Packet-2.
2. Then the seq-97 leftover queue continues per the ledger (nothing else is mid-flight).

## STANDING RESTRICTIONS (unchanged)

NEVER merge PR #241. Supervisor frozen (changes need cited D-024-R###). Expansion hold
(`.claude/rules/expansion-agent-dispatch-hold.md`) — Packet 3 lot outline / MapLibre must NOT be
planned or started. No bare `git stash`. No new packages outside the dependency policy. No hosted
web deploy before the Next.js RCE fix (owner-gated). API URL stays private. Geoclient key exists
ONLY in owner env + Render dashboard. Thin client (no local node_modules/DBs/bulk data). G6 on
M4-T001 = owner-only Section 20/Tier D hard stop. Stop-and-ask only for credentials/payments/legal
sign-offs (D-008).
