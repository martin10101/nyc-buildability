# M0-T092 — G2 producer self-check (orchestrator-recorded; never an independent gate)

Producer: fable-orchestrator-session. Supervisor-freeze qualifying evidence: D-024-R102.
G2 is the producer's own check (ADR-005 gate classes); the independent verdicts are G3/G4/G5 +
the directive-compliance verification.

## Self-check results

1. **Section-16.3 matrix** — `tools/test_agent_supervisor_controller_succession.py`:
   **70/70 PASS** (15 scenario classes S1–S15; stdlib unittest; injected clocks/rng; no
   network, no providers, no sleeps; temp-dir journals only).
1b. **Provider CLI drift increment** — installed CLI auto-updated 2.1.247 → 2.1.248
   mid-unit; all three live drift teeth fired by design and were re-captured per their
   prescribed remedies (classification/event-set parity proven; producer report §4.4).
2. **Mutation testing** — **13/13 targeted mutants KILLED**, baseline re-established PASS
   after every restore, `__pycache__` cleared around each run (mutant list: report §4.4).
3. **Modularity** — `python tools/modularity_check.py --check`: **0 failures**; the 5
   warnings are pre-existing files outside this unit.
4. **Lint** — ruff (local 0.9.9): **no findings in any touched file**; whole-tree count
   unchanged vs the staged HEAD (the `rotation.py:48` unused-`Sequence` F401 predates this
   unit — verified by stash — and is recorded, not hidden).
5. **Full supervisor-freeze suite baseline** — full `tools/` pytest run: recorded below at
   completion (M0-T039 baseline duty: >= 1165 tests, 0 failures).
6. **Scope** — diff strictly inside allowed_paths (4 new modules, 4 additive extensions, the
   matrix test file, the phase1 count assertion under the recorded scope amendment, this
   report set). Guard packs and every forbidden path untouched. Nothing deleted.
7. **Prohibitions honored** — no PR merged (PR #241 untouched); no activation; no new MCP;
   no new dependencies (stdlib only); no worker-facing token pressure introduced (S14).
8. **Owner-gated residual** — C1 live succession canary NOT executed (R192/R197
   exact-command); queued for the owner; deterministic core verified without it.

## Full-suite baseline (item 5)

- Command: `python -m pytest tools/ -q -p no:cacheprovider` (full log committed:
  `project-control/reports/M0-T092-full-suite-T1.txt`; summary reproduced verbatim below)
- Completed run at tree T1 (all unit-F production code included):
  **`3 failed, 2911 passed, 3 skipped in 1931.27s (0:32:11)`** — the 3 failures were
  exactly the three live drift teeth firing on the 2.1.247→2.1.248 auto-update
  (capability_probe live-reprobe, event_bus catalog tooth, native_adapter detection tooth).
- T1→T2 delta = the drift re-capture only (no production logic); its complete consumer set
  re-ran at T2: **195/195 PASS** (`capability_probe` + `event_bus` + `native_adapter` +
  `phase1`), plus the matrix **70/70 PASS**.
- Two later full-suite background runs were externally stopped before completing (recorded);
  CI on the pushed branch is the independent whole-suite confirmation at the frozen identity.
