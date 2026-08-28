# M0-T096 — G2 producer self-check (orchestrator-recorded)

Task: M0-T096 (unit I: two-unit golden run, fault-injected canaries, activation package,
Amendment-7 watcher + pending_live_observation register).
Producer: fable-orchestrator-session. Reviewed identity: deliverable `5ff7f08`
(code) + `f8ad557` (report evidence through section 4).
Supervisor-freeze qualifying evidence: **D-024-R106**.

1. **Matrix** — `python -m pytest tools/test_agent_supervisor_golden_run.py`:
   **40 tests, 0 failures** (~28 s): the two-unit golden run from the exact owner
   command crossing one safe rotation; the injected controller restart
   (exact-once); ambiguous-effect block; injected refusal/quota through the REAL
   CLI-built loop; double-start typed refusal; status-while-running; the watcher
   matrix (passivity, CAS idempotency, labeling, no-verified-live, comparison,
   sanitization, start-epilogue wiring); the composition gaps (multi-epoch ×
   forced rotation, extended pause, accelerated overnight + restart, bounded
   soak, autonomous selection/advance, on-demand-after-compact); and the three
   executable registers (16.9 a–m, R186 steps 1–15, R118 ladder — meta-verified
   citations).
2. **Prove-first (R018)** — the registers are executable: every cited existing
   proof is verified against the cited file's real test names; only the genuine
   gaps (staged pack §0 table) were built. No existing loop/rotation/recovery/
   effect logic was rebuilt.
3. **Mutation** — **12/12 hand-picked non-equivalent mutants KILLED** (serial,
   run only after every suite chunk finished; originals restored byte-exact and
   re-verified; matrix in report §4.4, incl. the bridge-wiring-nulled and
   epilogue-dropped CLI mutants).
4. **Modularity** — `python tools/modularity_check.py --check` after `git add`:
   **failures 0**; no new file warns (golden_run.py 407 ln, live_observation.py
   451 ln, test pack 1,017 ln; cli.py +38/−8 net).
5. **Lint** — `ruff check` on every new/changed file: clean.
6. **Composed suite** — foreground chunks (background python is externally
   killed on this box): supervisor packs 303 + 317 + 590 + 546 + 828 =
   **2,584 passed / 2 skipped / 0 failed** (≥ the 1,165-test M0-T039 baseline);
   non-supervisor packs 373 (+2 directive-compliance tests that failed only
   under the mid-suite Amendment-8 registry race, both PASS re-run on the
   settled tree) + 184 passed / 1 skipped. CI on the pushed HEAD `f8ad557` is
   the confirming whole-suite run (supervisor-bridge job).
7. **Registry validator** — `python tools/validate_directive_compliance.py
   --check`: **EXIT=0** (after the Amendment-8 capture, 249 rows).
8. **Scope** — the unit's file changes are strictly the packet's allowed_paths
   (`tools/agent_supervisor/{golden_run,live_observation,cli}.py`,
   `tools/test_agent_supervisor_golden_run.py`, the two packet reports) plus
   orchestrator control-plane artifacts (G0/claim/progress, the Amendment-8
   capture set, evidence map, amendment owner reports). `.claude/hooks`,
   settings, and every forbidden path untouched. GitHub effects: none beyond
   campaign-branch pushes; PR #241 untouched; all golden-run git effects live
   in disposable checkouts.
9. **Lane discipline (Amendment 7)** — zero live provider calls; every
   fixture/record labels itself INJECTED; the register holds
   `pending_live_observation` with zero live candidates; R187/R595 untouched.

Verdict: **PASS** (producer self-check; independent review at G3/G4/G5 + DCV).
