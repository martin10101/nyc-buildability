# Three-loop launch record — 2026-09-18 (D-072-R001/R002/R003 evidence)

Owner directive D-072 (up to three loops side by side, zero conflict) executed at the
M5-T035 acceptance seam. All three supervisors launched and holding their locks; journals
at START_CLAUDE (preflight_pass) at record time.

| Loop | Checkout (own runtime identity) | Runtime key (sha256 of canonical checkout path) | Packet | Worktree / branch | Fresh run-id |
|---|---|---|---|---|---|
| 1 | C:\SupervisorController | 9aca7075… | M5-T037 (DB-014 screen wiring + DB-020 fix + report parity) | wt-m5t037 / task/M5-T037-screen-wiring | persistent-local-42-m5t037 |
| 2 | C:\SupervisorController2 | cfdedc11… | M5-T038 (DB-006/007/009/019 address/panel cluster) | wt-m5t038 / task/M5-T038-address-panel-polish | persistent2-local-03-m5t038 |
| 3 | C:\SupervisorController3 (NEW byte-copy of instance 2) | 9df5e3ba4671f54db460fed03b322e7fe79bf87c47545770c87fb197873de57e | M5-T039 (DB-010 named-street matcher, module only) | wt-m5t039 / task/M5-T039-named-street-override | persistent3-local-01-m5t039 |

- **No-conflict check (D-072-R003):** pairwise allowed_paths intersection across all three
  packets mechanically verified EMPTY at the contract seam ("PAIRWISE DISJOINT: True");
  recorded in each packet's G0 report. Distinct worktrees, branches, and runtime identities;
  key3 derivation verified by reproducing keys 1 and 2 exactly through
  `durable_state.checkout_key` (normcase-canonical path sha256). Sequential integration at
  seams unchanged (ADR-005).
- **Worker model:** all three share `C:\SupervisorController\model_selection.toml`
  (claude-opus-4-8 worker pin, D-064 / D-073-R009); main session stays fable-5.
- **Pre-launch drill:** both existing runtimes had ZERO pending approvals and ZERO queued
  asks (both stores checked); both audit chains found FORKED (duplicate sequences 123 / 10 —
  stale CLI-race damage from the prior session) and repaired BETWEEN runs by the documented
  evidence-preserving archive (`audit.jsonl` → `audit.jsonl.forked-evidence-20260918-074553`
  in both runtime dirs; loop-1 via tools/controller_update/repair_forked_audit_chain.py,
  loop-2 via the same manual pattern; append capability re-proven with `revoke-all` on both).
  Loop-3 starts a fresh chain at genesis.
- **Watcher:** re-armed as one triple watcher (audit signatures incl. ASK/DEFER_TO_OWNER,
  breaker, refusal, completion; the run-40 two-store fix polling `pending-approvals` per
  checkout; native-tasklist pid liveness with 5 s recheck) over all three runtime keys.
- **Contract head:** c92154e7 (packets, G0 PASS ×3, claims, applicability bindings with
  digest resyncs, placeholders). CI on that head: context-budget + secret-scan success, main
  CI in progress at record time (loops branch from the same head; the orchestrator captures
  the completed run before any producer harvest).
- **Fewer-than-three fallback (D-072-R002):** not needed — three loops launched. Contention
  rule: reduce stepwise 3→2→1 on observed cross-writes or sustained machine/account
  contention (D-072-R003).
