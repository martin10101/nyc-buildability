# M0-T120 — G2 self-check (orchestrator, producer-side verification before independent review)

Recorded 2026-08-29 at the material identity `7d8195b` (cherry-pick of worktree commit
`4e0d307`; worktree `wt-m0t120` @ base `47f9037`; two recorded scope extensions).

| # | Check | Result |
|---|---|---|
| 1 | Scope | PASS — delta spans exactly 14 files, all inside the twice-extended allowed_paths (extensions recorded in the packet's scope_extension_note with justification); `test_agent_supervisor_loop.py` admitted but legitimately untouched (its failures resolved by the mode scoping); cli.py, broker/policy, and `.claude/**` untouched |
| 2 | The measured routing answer (R292) | PASS — orchestrator read the fixture and evidence report: NATIVE routing at 2.1.251 under the exact controller construction (Grep→Read→Edit, zero shell; mutating Edit brokered+DENIED; 3 provider calls; no writes; digest-keyed `cli_identity`); the original bashFirst stops root-caused to cross-worktree discovery |
| 3 | Tooth gates for real (R295) | PASS — the fold is LIVE in `start_gate.live_revalidation`; tooth-bite proven as a permanent golden test (certified start without evidence → `UNSAFE_OR_DRIFTED`, `routing_evidence_stale`, dispatched False, 0 provider calls, exit 11); fail-closed on absent/unreadable/mismatched evidence; real installed digest still passes the committed fixture |
| 4 | Mode-scoping ruling | RECORDED — gating scoped to `MODE_LIMITED_AUTO` per the orchestrator ruling (R295 protects the CERTIFIED run; shadow forwards nothing; supervised holds every prompt for a human; the tooth reports in every mode). Explicitly flagged for independent reviewer scrutiny — reviewers should judge whether this satisfies R295 |
| 5 | Seeding design honesty | PASS — harness seeding uses the durable journal (`record_routing_evidence`) for each harness's OWN fake identity in setup (M0-T072 bound-manifest precedent); never the shipped fixtures dir; no production special-case for fake digests; the tooth itself unweakened |
| 6 | Tests (independent re-runs) | PASS — orchestrator re-ran: golden+bounded_mode+routing_probe = **168 passed** (golden now 42 incl. the tooth-bite test); earlier three-module run 160 passed; FULL suite in the worktree: **2782 collected = 2726 baseline + 56, 2780 passed, 2 skipped, 0 failed** (matches producer exactly) |
| 7 | Red/green | PASS — probe-level red (tooth stubbed → 3 fails; guidance no-op → 1 fail) and gate-level red (fake identity refused verbatim) captured in M0-T120-routing-evidence.md before the green states |
| 8 | Prohibitions (R293) | PASS — classifier byte-untouched; 13 Windows-shape assertions are tests only; two permissiveness findings RECORDED for the gate wave (both still ASK, never AUTO); no new AUTO class; no owner-gate change; no new dependencies; no DISABLE_UPDATES |
| 9 | Live-probe bounds | PASS — 3 provider calls total (≤3 bound), deny-everything handler, zero writes, temp fixture dir (no repository paths), no retries; no further live calls in the two follow-up rounds |
| 10 | Consequence recorded | The supervisor tree and golden blob MOVE with this unit — certified by the single M0-T119 recertification at the final identity (R296); M0-T119 remains held until this unit is accepted (R297) |

**VERDICT: G2 PASS — ready for the independent G3/G4/G5 wave at this identity.**
