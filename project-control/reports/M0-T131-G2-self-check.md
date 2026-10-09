# M0-T131 G2 self-check (producer: orchestrator-defect-runner)

Recorded 2026-08-31 by the successor orchestrator session at HEAD `57f1b70d` (the
implementation landed pre-claim at `58df90c2`; `git diff 58df90c2..HEAD` over the three
allowed paths is EMPTY, so the reviewed content is byte-identical). Full design +
coverage narrative: `M0-T131-reviewer-access-fix.md` (committed alongside the change).
Every exit code below read UNPIPED (M0-T130 lesson).

- **Green (re-run THIS session at HEAD):** reviewer pack
  `tools/test_agent_supervisor_reviewer.py` **85 passed** in 36.63s (81 prior + 4 new
  `ReviewStdinContractTests` nodes; no existing test removed or modified — the fake
  gained only the opt-in `FAKE_STDIN_TARGET` stdin-recording hook). REVIEWER_EXIT=0.
- **Affected loop-level packs** (reviewer + ephemeral_review + golden_run, one
  process): **158 passed, 0 failed** in 80.30s. AFFECTED_EXIT=0.
- **Whole supervisor suite** (all 70 `tools/test_agent_supervisor*.py` files, one
  process): **3,040 passed, 2 skipped, 3 failed** in 550.03s. The ONLY 3 failures are
  the SEPARATE 2.1.251->2.1.252 CLI-drift live-fixture tests
  (`capability_probe::test_live_reprobe_claude_version_matches_fixture`,
  `event_bus::test_s8_live_version_matches_catalog_fixture`,
  `native_adapter::test_live_detection_matches_committed_fixture`) — the R286/R287
  admission event, owner-only lane, NOT this task; they SKIP on CI, so CI stays green.
  Baseline reconciliation: 3,039 (M0-T130 recertification) + 4 new reviewer nodes = 3,043
  collected of which 3,040 pass here (the 3 drift tests passed at the M0-T130
  recert because the CLI had not yet auto-updated; the drift happened later in the
  producing session). No test file removed.
- **Red-on-mutant:** proven in the producing session and recorded in the fix report
  section 3 (reverting `_attempt` to plain `json.dumps(payload)` fails
  `test_stdin_is_one_json_object_with_instructions_and_packet`, 1 failed / 3 passed,
  reproduced; mutant reverted). NOT re-run this session — re-proving it would require
  temporarily mutating the frozen reviewed content mid-gate; G3/G4 trace
  removal-sensitivity read-only instead.
- **Teeth (re-run THIS session):** `ruff check tools/agent_supervisor/codex_reviewer.py`
  clean, RUFF_EXIT=0. `modularity_check --check`: **failures 0**, MOD_EXIT=0
  (codex_reviewer.py carries a non-blocking `review_signal` warn — above the 600-SLOC
  warn threshold; cohesion: the file remains the single reviewer transport (argv +
  stdin contract + decision validation); split candidate stands recorded for next
  substantial growth). `supervisor_command_doc_check.py`: 12 commands, 0 drift,
  CMDDOC_EXIT=0. Registry validator `validate_directive_compliance.py --check`:
  **EXIT=0** at this content (re-run this session, background, full output retained).
- **Scope:** commit `58df90c2` touches exactly the three allowed paths PLUS
  `project-control/reports/M0-T130.json` — the previously-omitted M0-T130 submit
  record, an ORCHESTRATOR control-plane artifact written by the control CLI at
  M0-T130's submit and landed here for ledger completeness (disclosed; not producer
  scope). No journal key, flag, schema, broker, or loop/turn_budget change; no argv or
  sandbox change (invariant 10: still `--sandbox read-only`, no write access
  anywhere). Journal untouched (HALTED from journey 4, transitions 35, audit 85);
  wt-m0t109 clean `1c06957`; queue digest `11eaa5a7` unchanged; PR #241 untouched.
- **Preservation note (discovered THIS session, disclosed for G3/G4):** `wt-m0t107`
  is at `c5c6ff7` with two UNTRACKED files — `docs/D024_PORTABILITY_PLAN.md` (17,498 B)
  and `project-control/reports/M0-T107-portability-plan.md` (4,759 B), authored
  2026-08-31 20:01-20:02 UTC, inside the journey-4 worker's ~19:55-20:02Z work window.
  They are the worker's genuine M0-T107 plan-stage deliverable drafts (plan-only,
  citing D-024-R179 at content identity `c5c6ff7`). The journey-4 report's "produced
  no file changes"/"clean" wording covered tracked state only and is corrected by this
  note. Preserved byte-for-byte; not part of M0-T131's scope.
- **Honest residuals** (fix report section 5): (1) the preamble's effect on live
  reviewer BEHAVIOR is design-reasoned, not yet live-proven — the next owner-typed
  journey is the live measurement; (2) `verified_repo_head`/`verified_origin_main`
  become packet-echoed for out-of-root facts (honest narrowing, disclosed in the
  preamble itself); (3) R247 recert deferred to the ONE final identity covering both
  this tree move and the owner-dispositioned CLI identity; (4) the 2.1.252 admission
  lane is OPEN and owner-only.
