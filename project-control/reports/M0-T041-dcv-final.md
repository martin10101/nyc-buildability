# M0-T041 directive-compliance verification — FINAL, verdict preserved verbatim

**Verifier:** directive-compliance-verifier (independent, read-only). **Recorded by:** orchestrator.
**Verified at:** content identity `78ed0cc1bedd2c6c15de251fd01e1c905d6624b7a79cd751d8b9eee1ccb50a4f` (reproduced BYTE-EXACT
at reviewed_sha `8a6dd546479b1e0f5fae7f00aec9bafefb9cc209`; invariant through the parallel gate-record commits — tools/ diff
empty to HEAD). **Overall: PASS — all 24 applicable requirements SATISFIED; no VIOLATED/UNVERIFIABLE/BLOCKED.**

---

## Frozen identity and lineage (independently reproduced)
- Identity `78ed0cc1…` recomputed via frozen_git_identity over allowed_paths at `8a6dd54` (raw-blob manifest incl. new resource_sampling.py blob `44f480c6` + 4 control-plane material entries). Base `f65d716`; producer code commit `cdab33d`.
- HEAD moved to `85798a8` during review (orchestrator gate recording); `git diff 8a6dd54..85798a8 -- tools/` EMPTY; every substantive gate (G2/G3/G4/G5) bound to the same identity `78ed0cc1`.
- Deliverable scope confined: exactly 7 files, all tied to the four cited closures.

## Applicable-set and amendment integrity
- evaluate_task_refs → ok=True, 24 applicable, 0 missing/invalid — matches submit record and refs.
- v4 amendment (`a2a8cda`) confirmed applicability-metadata-only: version 3→4, updated_at, and two task_ids edits (R078 dropped M0-T041; R089 M0-T041→M0-T045); no id/text change; count stays 112. R078/R089/R027 correctly excluded from T041.
- Validator --check exit 0; full run "directive registry OK: 9 directive(s), 9 active…".
- Evidence map covers exactly the 24 (0 missing, 0 extra); every referenced file exists.
- Full 23-module suite reproduced: Ran 1189 — OK (skipped=2) = 1189/1187/0/0/2; the 3 new modules 24/24.
- SHADOW-ONLY / R595 untouched: no activation flag; QUOTA_EXHAUSTION_SIGNAL_VERIFIED derives False; production fail-closed PAUSE.

## Per-requirement verdicts (all 24)
- **R025 — DEEP, SATISFIED.** classify_quota_exhaustion returns the reason ONLY on a verified_live match; unknown/absent/malformed/documented-but-unverified → "" (fail-closed, AD-025), never raises; VERIFIED flag derived False. Sampler reports structurally-unmeasurable as unknown (never fabricated OK); outage → conservative; _check_resources fail-closed both directions. 20 new unit/loop tests reproduced green.
- **R093 — DEEP, SATISFIED.** Each closure's citation verified against primary sources (ACTIVATION-CHECKLIST lines 27/30/33-34; V1.2.3 G5 LOW finding matched verbatim to loop.py:591-596); commit stamped "checklist-cited"; B-1..B-4 honestly reported already-fixed, no fabricated reproduction; no uncited feature; consistent with supervisor-freeze rule.
- **R031 — SPOT, SATISFIED.** UnsafeMomentTests::test_every_unsafe_condition_refuses (rotation refuses on command_running/tool_call_pending/approval_pending/…); unchanged; green.
- **R023 — SPOT, SATISFIED.** inspect_stream computes peak current-context off the machine-readable stream, not lifetime cumulative; ModelIdentityAndUsageTests cover including unknown-usage; unchanged; green.
- **R036 — SPOT, SATISFIED.** CodexRateLimitTests (checkpoint held, no unreviewed continue, fresh-process review restart, queued review) + RealProcessSwitchTests/ChainExhaustionTests; AS-1 wiring keeps production fail-closed; green.
- **R019, R020, R021, R022, R024, R026, R028, R029, R030, R032, R033, R034, R035, R037, R038, R039, R040, R075, R076 (19 rows) — PASS (capability continuity, NOT fresh re-derivation).** Basis: (a) supervisor diff confined to the four cited closures; (b) full suite green at the reviewed source; (c) M0-T036 acceptance lineage (585-req verification) + the M0-T039 freeze baseline (1165/1163/0/2, tree `e8eeb4fa…`). Stated explicitly as unchanged-frozen-capability verification.

## Cross-cutting confirmations
Producer ≠ verifier; gate reviewers distinct; deliverables unchanged since reviewed_sha; identity stable and reproduced; validator exit 0; G0/G2/G3/G4/G5 all PASS on file bound to `78ed0cc1`; no prohibited action; SHADOW-ONLY intact; R595 not lifted.

**OVERALL VERDICT: PASS.** All 24 applicable D-010 requirement IDs (R019-R026, R028-R040, R075, R076, R093) SATISFIED on reproduced primary evidence at content identity `78ed0cc1…50a4f` (reviewed_sha `8a6dd54`).
