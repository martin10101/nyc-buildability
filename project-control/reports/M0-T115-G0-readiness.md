# M0-T115 — G0 readiness (administrative; recorded at the claim seam)

Task: M0-T115 (unit O: broker answer paths resolve their queued_asks rows + recovery-probe
read-time reconciliation; Amendment 12 rows R272/R273/R274). Recorded by: orchestrator
(fable-orchestrator-session), 2026-08-29, campaign seq 28. Supervisor-freeze qualifying
evidence: **D-024-R270** (the correction this unit executes) / **D-024-R272** (owner
execution order).

1. **Authorization:** Amendment 11 R270 mandated the proposal; Amendment 12 R272 (capture
   `b180754`, validator EXIT=0) orders execution in the same certification window as
   M0-T114, as SEPARATE bounded tasks/commits/evidence/reviews, no broadening.
2. **Bootstrap Gate 0:** re-verified — cwd IS the ctl24 root, branch
   `control/D-024-fable-codex-loop`, clean tree, local == origin, no MCP.
3. **Defect provenance (primary evidence, recorded pre-claim):** live first-run journal
   (three `queued_asks` rows `answered_at_utc: ""` with approval records `DENIED`) +
   restart refusal (`UNSAFE_OR_DRIFTED`, failed `['pending_requests']`, 0 provider calls)
   + code reading: `broker.py deny_request`/`approve_once` never call `resolve_ask`
   (M0-T070 fix exists in `revoke_all` only, broker.py:684); `recovery_probes.
   probe_pending_requests` reads raw `open_asks()` without the cli.py (~1493) read-time
   reconciliation. Full account: `M0-T113-activation-evidence.md` addendum §4.
4. **Packet integrity:** resolver ok=true, 3 applicable ids (R272, R273, R274);
   allowed_paths = the two owning modules + their two test packs + the repair record;
   `cli.py` explicitly FORBIDDEN (the status-side reconciliation is already correct —
   smallest fitting change stays in the owning modules, standard §2.1/§2.4).
5. **Method staged (standard §3):** red-before-green — regression tests written and
   observed FAILING against unchanged code first, exact commands+output recorded; fix;
   green observed; revert-proof recorded (fix reverted → tests fail → restored → pass),
   satisfying both §3.4 and the owner's removal-sensitivity order (R274). Path proofs
   cover deny→clear-recovery→restart AND approve-once→restart against BOTH new-shape and
   pre-fix-shape journal records. NO runtime-journal edit at any point (R273) — the live
   journal becomes truthful via the read-time reconciliation only.
6. **Consequence acknowledged:** supervisor-source change → R247 certification invalidated
   → M0-T116 recertification at the ONE frozen final identity before any resume (R275/R276).

Verdict: **PASS** (administrative readiness; independent review at G3/G4/G5 + DCV).
