# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff - seq 100: 185 accepted; M5-T016 ACCEPTED end-to-end; D-040 scoped-unblock queue next (R003 -> R002 -> R001)

Generated 2026-09-12 ~04:10 ET by the resumed orchestrator session (seq-99 continuation). Root
`C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch `candidate/D-024-mrl-option-b`, HEAD
`c7170914` **pushed**. `main` untouched at `d8b3899f`. PR #241 OPEN - NEVER merge.

## STATE (verify live; ledger wins)

1. **Accepted = 185.** M5-T016 (address Packet 2: Confirm card + ZoLa /bbl deep-link + handoff)
   ACCEPTED end-to-end this session: CI evidence at first-execution-green 49bd086b -> submit
   069c3d40/ed110e6a -> four-gate wave (G1/G3/G5 PASS; G4 PASS w/ required correction C1) ->
   C1 one-bounded test-only correction b1129f34 (S5 asserts bounded retrieved-at clause +
   in-disclosure GRC line) -> delta attestations from the SAME four reviewers (all PASS; C1
   DISCHARGED) -> gate records fd8832d9 (identity f85bc9e8) -> resubmit restamp 6ec7b631 ->
   independent DCV PASS/ROW-SUFFICES + a5694aea restamp -> accepted c7170914. All reports,
   attestations, and the DCV live under `project-control/reports/M5-T016-*`.
2. **D-040 captured (owner scoped unblocks, commit a5694aea by the prior session; validator
   EXIT 0; all six requirements bind sentinel D-040-BOOTSTRAP).** Owner verbatim: "Ok lets
   unblock all beside the next js and superbase that needs me." Governs the queue NOW:
   - **R003** directive-digest normalization (kills the standing control-plane CI red;
     source-*.md IMMUTABLE - append-only mechanisms only).
   - **R002** feature-flag unification (INTERNAL_RULE_EVAL_UI vs INTERNAL_RULE_EVAL_ENABLED,
     the M5-T015 G5 F-1 note; deploy-affecting - packet must name the Render env-var change
     as an owner return item).
   - **R001** SCOPED expansion-hold release: address-flow lot-outline increment ONLY
     (design-spec Packet 3: MapPLUTO parcel-geometry connector + lot outline on the confirm
     card, MapLibre GL JS; official-source research FIRST). Hold rule §2.1. Everything else
     under the expansion hold stays SUSPENDED.
   - Still owner-gated (R004/R005): Next.js upgrade/deploy; Supabase/credentials (owner said
     credentials tomorrow). R006: G6 unchanged. Suggested order R003 -> R002 -> R001.
3. **CI churn note:** the owner pushed docs commits (MVP_ARCHITECT_REVIEW_QA.md parts 1-4,
   incl. the Part 4 gap list awaiting owner triage) from a parallel session during the arc;
   cancel-in-progress preempted supervisor-bridge twice (documented in
   M5-T016-ci-evidence.txt - NOT a failure; web+web-e2e completed green first). The two
   standing owner-gated reds remain: web-dependency-security (Next.js RCE - D-040 R004 keeps
   it owner-gated) and control-plane (digest normalization - now UNBLOCKED as D-040 R003).
4. Prior session (ctl24-8e) went dormant on repo work after the D-040 capture; this session
   owns the ledger. Campaign-continuity tool still fails closed - use the ledger.
5. Sub-agents: the four M5-T016 reviewers + the DCV verifier completed; returns preserved
   verbatim under `project-control/reports/`. Spawn FRESH agents for new work.

## NEXT ACTION (in order)

1. Contract D-040-R003 (digest normalization) via /start-controlled-task citing
   `D-040:D-040-R003`: reproduce the control-plane CI red locally-in-CI-terms first, fix via
   append-only mechanism (source-*.md immutable), CI green = the red retired.
2. Then R002 (flag unification; small; Render env-var rename = owner return item).
3. Then R001 (Packet 3 lot outline): official-source-researcher on MapPLUTO FIRST (house
   connector law), then packet(s) for connector + confirm-card outline under normal gates.
4. Owner priority beyond the trio: NOT yet given - candidate backlog is
   docs/MVP_ARCHITECT_REVIEW_QA.md Part 4 (owner has it for triage). Do not self-assign
   beyond D-040 scope.

## STANDING RESTRICTIONS (unchanged)

NEVER merge PR #241. Supervisor frozen/SHADOW-ONLY (changes need cited D-024-R###). Expansion
hold except the §2.1 lot-outline release. No bare `git stash`. No new packages without
/dependency-security admission (MapLibre for R001 WILL need G5 provenance review + age gate).
No hosted web deploy before the Next.js RCE fix (owner-gated). API URL private; Geoclient key
ONLY in owner env + Render dashboard. Thin client. G6 on M4-T001 = owner-only. Stop-and-ask
only for credentials/payments/legal (D-008). Bootstrap Gate 0 before any write.

## AUTHORITATIVE FILES (smallest set)

`project-control/state.json` + `directives/D-040-scoped-unblocks/` (the new queue) ·
`tasks/M5-T016.json` + `reports/M5-T016-*` (the completed-arc pattern incl. DCV restamp) ·
`docs/design/address-entry-confirm-design-spec.md` (Packet 3 sections for R001) ·
`.claude/rules/expansion-agent-dispatch-hold.md` §2.1 · `CLAUDE.md` · this file.

## COPY INTO THE NEW SESSION

resume from handoff seq 100: work from durable repository evidence. Verify root/branch/HEAD
(expect C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 on candidate/D-024-mrl-option-b), Bootstrap
Gate 0, read CLAUDE.md + docs/SESSION_HANDOFF.md, run `python tools/project_control.py status`,
reconcile vs live git/CI (origin may have advanced; ledger and CI win). 185 accepted; M5-T016
done. Execute the D-040 queue from NEXT-ACTION item 1 (R003 digest normalization -> R002 flag
unification -> R001 lot-outline Packet 3 with MapPLUTO research first), each via
/start-controlled-task citing its D-040 requirement, normal gates. Report READY TO RESUME or
BLOCKED before changing anything. Stop only for owner-only items (credentials/payments/legal,
PR #241, Next.js upgrade/deploy, Supabase, G6).
