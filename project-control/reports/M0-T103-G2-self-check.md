# M0-T103 G2 self-check (producer: orchestrator)

Recorded 2026-08-26 UTC before submission.

1. **Outputs vs packet:** upgrade record `M0-T103-version-upgrade.md` (pre/post identity with
   sha256 pair, canary results, rollback plan) ✓; masked dual-version fixtures ✓ (pre =
   `capability_probe_live_2026-08-25.json` + `capability_probe_live_2026-08-26.json`, both
   2.1.220, retained; post = `capability_probe_live_2026-08-26_m0t103_post_update.json`,
   2.1.246, task-id-stamped filename per G3 ADV-1); regression record ✓ (drift tooth RED →
   re-baselined in section 5; no Claude Code regression found, rollback not needed); test
   re-baseline ✓ (packet allowed_paths widened pre-submit, recorded in packet + this check).
2. **R167 checklist:** all 6 steps evidenced (report sections 1–3). **R168 checklist:** all 4
   steps evidenced (sections 3–7): child canaries on new binary, Gate 0/MCP/settings/hooks/
   fixtures re-run, regression recorded not silenced, no activation on version success.
3. **Tests:** `test_agent_supervisor_capability_probe.py` 18 passed (incl. 2 new dual-version/
   masking invariants; the old tooth demonstrably fired RED on real drift before re-baseline —
   a live mutation proof); statusline/telemetry/contracts/runtime suites 228 passed, 0 failed.
4. **Scope:** writes confined to allowed_paths (report, fixtures dir, the widened test file) +
   orchestrator control-plane records. `git diff` shows no other change; settings/hooks/deps
   untouched.
5. **Masking:** post fixture 0 username hits; report uses `[HOME]`; session list masked.
6. **Honest limitations disclosed (section 8):** live 2.1.246 statusLine payload deferred to
   the first fresh interactive session (next-session discharge pattern); unit C/D/E/G live
   fixtures unchanged; owner-visible advisory: broken leftover npm shim (uninstall is an
   owner-machine action); session `777b09da` display-state artifact documented with recovery
   command, process alive, untouched by us.

Self-check verdict: ready for independent review. Requesting `awaiting_gate`.
