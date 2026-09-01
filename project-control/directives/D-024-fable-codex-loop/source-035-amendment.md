# D-024 Amendment 35 — B-020 resolved: proceed now (no cap wait); start the codex loop under Fable unavailability (owner instruction 2026-09-01)

Captured: 2026-09-01 UTC by the orchestrator (Fable 5), verbatim, BEFORE acting.
Base identity at capture: HEAD `b1aec5fe` (campaign seq 65). Amends: `source-001.md`.
Requirement IDs: D-024-R446..D-024-R448.

Reconciliation: this resolves blocker **B-020**. R446 — the owner rejects Option A
(waiting for the Fable 5 seven-day cap reset): proceed NOW. R447 — the goal is to START
the codex loop even though Fable 5 is unavailable (capped) right now; commissioning
proceeds under Fable unavailability using the campaign's established fallback-model path
for any model-dependent work (workers/routing on the non-capped worker model,
`claude-opus-4-8`, per the M0-T074 model-routing set) rather than blocking on Fable.
R448 — mechanically, this selects **B-020 Option B**: the bounded shell-routing
recapture at `e713c5a6` runs on the non-capped worker model, so M0-T132 can complete in
one pass (three owner-named fixtures + shell-routing at the admitted digest + repin +
ONE combined R247 recert at ONE final frozen identity + gates G0/G2/G3/G4 + DCV +
accept), producing a certified startable identity; the certified `--owner-enable-bounded-auto`
start command (R595 already exercised 2026-08-29) is then prepared under the R254/R259
conditions. This amendment does NOT lift any other owner gate: it does not authorize
merging PR #241, does not change the R595 activation terms, does not waive any gate or
the fail-closed dependency-security/identity rules; if the non-capped model is ALSO
unavailable, or any gate/identity check fails, the standard R394 stop-and-report applies.

Forward trace: "no waiting go on" -> R446 (proceed now, reject the cap-wait);
"i need to start the codex loop even if fable is not available now" -> R447 (commission
under Fable unavailability via the fallback path) and R448 (its mechanical consequence:
B-020 Option B recapture + finish M0-T132 + prepare the certified start).
Anchors: #proceed-now (R446), #start-under-fable-unavailable (R447), #option-b-finish (R448).

---VERBATIM-BEGIN---
no watiinf go on i need to start the codex loop even if fable is not available now
---VERBATIM-END---
