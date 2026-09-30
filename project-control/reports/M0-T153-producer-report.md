# M0-T153 Producer Report — D-033 T-B (reduced; current-state resubmission, 2026-09-08)

**Why this revision.** The prior report inlined full source in a "section 7" that fell
PAST the collector's per-section bound (`evidence.py:46 DEFAULT_SECTION_BYTES = 16_384`),
so that inlined source never reached the packet. This report is reduced to sit inside one
16,384-byte section; the actual current digest-bound source and the complete code/test
diffs are **routed to the orchestrator** to capture into the packet's own bounded
sections (the orchestrator-owned spans via `untracked_content`, the `git diff HEAD`
sections, and `command_transcripts`) — each its own ≤16,384-byte section within the
262,144-byte packet total. Producers cannot commit, write spans, or change the collector
config (ADR-005); this unit did none of those and reruns alone do not close the gap — the
section-4 capture, done by the orchestrator, does.

## 1. Identity + authority boundaries (measured this unit)

- Task M0-T153 (governance, M0), stage **claimed**. Producer `supervised-loop-fable-worker`
  (not a reviewer / gate recorder; ADR-005). Qualifying evidence **D-033-R002**
  (supervisor-run acceptance) + **D-033-R006** (machine-enforced separation).
- Branch `task/M0-T153-accept-engine`; HEAD `cc4972fde7df91739f29cffb0da73dd0a70e81aa`
  (`git rev-parse HEAD`, full 40-hex, this unit).
- `git status --porcelain` (this unit): EXACTLY five tracked-modified (`M`) paths + seven
  untracked (`??`) orchestrator-owned spans —
  `M project-control/reports/M0-T153-producer-report.md`,
  `M tools/agent_supervisor/accept_engine.py`, `M tools/agent_supervisor/gate_wave.py`,
  `M tools/test_agent_supervisor_accept_engine.py`,
  `M tools/test_agent_supervisor_gate_wave.py`, and
  `?? project-control/reports/M0-T153-span-{ae-01,ae-02,ae-03,aetest-01,aetest-02,aetest-03,aetest-04}.md`.
- **DEFAULT OFF + boundaries preserved.** Both D-033 stage switches DEFAULT OFF; with the
  flag absent the seam IS the T-A call byte-for-byte; supervisor SHADOW-ONLY; the R595
  activation path, Tier D / Section 20 hard stops, and every owner hold are unchanged
  (D-033-R005). This unit performed NO gate/submit/accept, NO commit, NO registry/directive
  write, NO span edit, and NO collector-config change; it edited only this report.

## 2. The inspectability gap and how the packet closes it

- The seven spans bind the **stale** snapshot `1cda79d784ba39f6e1a2a3e61f0f7d5834da112c`
  (accept_engine.py 1,189 lines / test 1,399 lines). The working tree carries uncommitted
  refinements on top of HEAD (`git diff --stat HEAD`: accept_engine.py 130, gate_wave.py
  62, test_..accept_engine.py 141, test_..gate_wave.py 108), so a reviewer reading only the
  stale spans sees materially different source than the green commands ran against.
- **Closure route (orchestrator).** Capture the CURRENT source into the packet within
  bounds: refresh the seven orchestrator-owned spans at the committed identity from the
  section-4 ranges (each span is one ≤16,384-byte section, so `untracked_content` carries
  it and its digest binds the full file), and rely on the `git diff HEAD` sections plus
  `command_transcripts`. The producer must not touch the spans or `evidence.py`; §7 routes
  this to the orchestrator.

## 3. Worker-reported hashes vs supervisor-authenticated source (distinguished)

- **WORKER-REPORTED (producer CLAIM — NOT authenticated).** The digest table below was
  computed by a temporary in-suite probe in a PRIOR unit (disclosure §6). It is a claim to
  be cross-checked, never authenticated evidence, and no fresh probe was run this unit.
- **SUPERVISOR-AUTHENTICATED (the real binding).** At capture the collector recomputes
  `models.digest_of` over the ACTUAL working tree (`evidence.py:404` convention:
  `read_text(encoding="utf-8-sig", errors="replace")`, universal-newline) in
  `untracked_content`/`command_transcripts`, and `git hash-object` blob ids at commit. The
  reviewer verifies the current source against THOSE, not against this table.
- Line counts below were re-confirmed THIS unit (`wc -l` + symbol grep); the sha values are
  the prior-unit worker-reported claims, carried for cross-check only:

| File | lines (confirmed) | worker-reported raw sha256 / collector digest_of (prior-unit claim) |
|---|---|---|
| accept_engine.py | 1,199 (SLOC 997) | `cd93c185…5739c8` / `7508ae16…fb04a8` |
| gate_wave.py | 1,180 (SLOC 975) | `cb227036…6258a5` / `17458121…df32a4` |
| cli.py | 3,602 | `148a4641…6894b1` / `64a40b58…797a494` |
| test_..accept_engine.py | 1,532 | `bca76459…5de7faf` / `6d8e60c1…07cefb5` |
| test_..gate_wave.py | 1,204 (restored) | host-limited; collector recompute at capture is authoritative |

`accept_engine.py` SLOC **997 ≤ 1000** (hard) is proven live this unit by `ModuleSizeTests`
(green in the 84-passed suite) and `modularity_check.py --check` (`review_signal`,
failures 0); `gate_wave.py` 975 and `cli.py` 2,951 are under their limits (§6).

## 4. Exact current source/test ranges needing supervisor capture (the map)

Current working-tree line anchors, all verified this unit. The orchestrator captures these
into the spans / diff sections; the producer supplies the map, not the inlined bytes.

**`accept_engine.py` (1,199 lines):**
- **Switch + CLI wiring** — constants + switches `:54`–`:340`: `add_owner_switch_argument`
  `:172`, `assert_acceptance_enabled` `:193`, `managed_acceptance_start_gate` `:204`,
  `register_stage_switches` `:268`, `stage_start_gate` `:281`, `record_enable` `:296`.
  CLI side (`cli.py`): import `:227`, `register_stage_switches(start)` `:3376`,
  `stage_start_gate` `:2964`–`:2966`, seam call `:2939`–`:2943`.
- **Checkpoint guard** — `plan_verifier_dispatch` `:386`–`:416`, `checkpoint_unresolved`
  guard body `:393`–`:397`.
- **Verifier contract + separation** — `VERIFIER_CONTRACT` `:117`, `VerifierDispatch`
  `:318`, `_assert_verifier_separated` `:343`, `verifier_for_packet` `:380`,
  `dispatch_verification` `:418`, `_assert_record_bound` `:452`.
- **Directive registry supply** — call site `:887`–`:897` (`cited_directive_requirements`);
  collector `gate_wave.collect_directive_registry` (below).
- **Decision admission** — `_row_rank` `:477`, `_parse_sentinel_row` `:481`, `extract_rows`
  `:514`, `worst_of_merge` `:599`, `assert_rows_clean` `:633`.
- **Transcription** — `verification_path_for` `:669`, `build_task_verification` `:682`,
  `transcribe_task_verification` `:734`.
- **HEAD-drift (I3)** — `assert_identity_fresh` `:803`, `_submission_identity` `:995`,
  `_live_head` `:1022`, typed `restamp_required` branch `:1125`–`:1129`.
- **Accept invocation** — `AcceptRecorder` `:834` (allow-set `_assert_subcommand_allowed`
  `:860`, queue bound `_assert_current_queue_task` `:870`, `build_argv` `:879`,
  `record_accept` `:901`), `AcceptDeps` `:915`, `AcceptResult` `:929`, `_parked` `:947`,
  `_assert_wave_satisfies` `:952`, `run_acceptance_stage` `:1029`–`:1145`.
- **Terminal-checkpoint bind** — seam `run_with_post_complete_stage` `:1153`–`:1199`, bound
  to `gate_wave.terminal_checkpoint_id(run)` at `:1190`.

**`gate_wave.py` (1,180 lines):**
- **Directive registry supply** — `collect_directive_registry` `:741`–`:761`
  (`DIRECTIVE_REGISTRY_FILES`).
- **Terminal checkpoint** — `terminal_checkpoint_id` `:1090`–`:1117`.
- **Advisory closure G5 L1 (redact-before-persist)** — `write_g2_report` `:794`–`:826`.
- **Advisory closure G3 D-2 (live read-back)** — `admit_verdict_file` `:524`–`:547`,
  `verify_verdict_report` `:549`–`:579`, wired in `run_gate_wave` `:1030`–`:1041`.

**Tests:**
- `test_..accept_engine.py` (1,532 lines): `ModuleSizeTests` `:387`, `StageSwitchTests`
  `:412`, `VerifierDispatchTests` `:555`, `RowExtractionTests` `:668`,
  `RealDecisionBoundaryTests` `:814`, `VerifierBoundaryAssemblyTests` `:870`,
  `WorstOfMergeTests` `:955`, `TranscriptionTests` `:1020`, `WavePreconditionTests` `:1139`,
  `AcceptRecorderTests` `:1202`, `AcceptanceStageTests` `:1263`, `CliSeamTests` `:1380`.
  Load-bearing MUTATION tests inside: OFF==today, verifier≠producer separation,
  `checkpoint_unresolved`, rank-blind-merge, forged-wave, allow-set, queue-bound,
  freshness-guard, seam re-assert.
- `test_..gate_wave.py` (1,204 lines, restored): `GateClassMirrorTests` `:258`,
  `SwitchTests` `:273`, `DispatchBindingTests` `:427`, `RecorderAllowSetTests` `:573`,
  `G2CaptureTests` `:663`, `CollectDirectiveRegistryTests` `:714`, `ImmunizationTests`
  `:776`, `WaveEngineTests` `:834`, `CliSeamTests` `:944`, `G2ReportRedactionTests` `:1066`
  (G5 L1), `LiveVerdictTamperTests` `:1114` (G3 D-2), `TerminalCheckpointIdTests` `:1165`.

## 5. Cohesion justification (module boundary + collector placement)

- **One responsibility, one fail-closed chain.** `accept_engine.py` (997 SLOC, justify band
  750–1000; recorded `review_signal`, not a failure) holds parsing, serialization,
  persistence, process invocation, and orchestration for ONE trust chain: switch →
  separation → checkpoint bind → extraction → worst-of merge → clean-rows → transcription →
  I3 freshness → bounded recorder. A detached importable "transcription writer" or "accept
  runner" reachable WITHOUT the switch/separation checks would be a new unguarded authority
  surface — exactly what D-033-R006 forbids. Imports are one-way (`accept_engine →
  gate_wave`, no cycle); `AcceptRecorder` is deliberately a separate class from
  `gate_wave.ControlPlaneRecorder` (accept vs gate/submit authority).
- **Why `collect_directive_registry` lives in `gate_wave.py`.** `gate_wave.py` already owns
  the managed lane's evidence-collection surface and its constants (`DIRECTIVE_REGISTRY_FILES`,
  `results_section`); the collector is another bounded, fail-visible evidence renderer over
  that machinery carrying NO acceptance authority. Co-locating it keeps the one-way import
  (`accept_engine` imports `gate_wave`, never the reverse) and lets both stages reuse it. It
  supplies ONLY the dispatch's CITED directives' `requirements.json`/`manifest.json` (the
  bounded AD-083 slice, keyed `cited_directive_requirements`; a missing file is a fail-visible
  entry), never the whole registry. Owning it in `accept_engine` would split the concern,
  invert the dependency, and add ~20 SLOC to a file already at the ceiling.

## 6. Verification — four documented commands (re-run this unit; green; retained, not the closure)

Run verbatim through the Bash tool, no wrapper/cd/chaining, at the current working tree:

1. `python -m pytest tools/test_agent_supervisor_accept_engine.py -q` → **`84 passed`**
   (includes `ModuleSizeTests`, green at 997 ≤ 1000).
2. `python -m pytest tools/test_agent_supervisor_gate_wave.py -q` → **`75 passed`**.
3. `python -m ruff check tools/agent_supervisor/accept_engine.py tools/agent_supervisor/gate_wave.py tools/agent_supervisor/cli.py tools/test_agent_supervisor_accept_engine.py tools/test_agent_supervisor_gate_wave.py` → **`All checks passed!`**
4. `python tools/modularity_check.py --check` → **`selected 359 files; failures 0;
   warnings 15`** (`accept_engine.py` + `gate_wave.py` `review_signal`, `cli.py`
   `symbol_ceiling` — all pre-existing signals, zero failures).

These reruns corroborate the tree is green; they do NOT close the inspectability gap — the
§4 capture routed to the orchestrator (§7) does.

**Digest-probe disclosure (prior unit, not re-run here).** The §3 worker-reported digests
were harvested by a temporary `unittest.TestCase` (`_M0T153DigestProbe`) appended to
`test_..gate_wave.py` that computed raw `sha256` + `models.digest_of` and raised
`AssertionError` so command 2 carried the values; the probe was then REMOVED and the file
byte-restored to 1,204 lines (confirmed this unit). A probe cannot bind its own host file,
so the gate-wave test digest stays host-limited and is authenticated by the collector
recompute at capture.

## 7. Orchestrator duties (routing; ADR-005 — producers cannot commit, gate, accept, or write spans)

1. **Capture the current source into the packet within bounds.** Refresh the seven
   orchestrator-owned spans at the committed identity from the §4 ranges (each span ≤16,384
   bytes → carried by `untracked_content`, digest binds the full file), plus the `git diff
   HEAD` and `command_transcripts` sections. The producer did not, and must not, edit the
   spans or `evidence.py`.
2. **Commit** the five modified paths (message citing D-033-R002 + D-033-R006 — freeze-rule
   duty) to give the reviewed content a committed identity.
3. **Independent gates G0/G2/G3/G5** at the reviewed identity (producer ≠ reviewer;
   reviewer_agents `code-reviewer`, `security-reviewer`, `directive-compliance-verifier`).
4. **DCV rows** transcribed at the reviewed identity — this report is a CLAIM, never proof.
5. **Frozen-candidate supervisor-suite re-baseline** (≥ 1,165 tests, 0 failures; M0-T039
   freeze duty).

---

*End of report. Nothing here accepts the task, records a gate, or changes any control-plane
state; it is producer evidence submitted for independent review.*
