# M0-T126 — G3 report (independent code-reviewer, read-only + read-only pytest) — VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31 by the unnamed roster code-reviewer spawn;
verdict FAIL with three blocking defects (G3-1 rotated-orientation wiring; G3-2 property-3
enforcement + a FALSE claim in the orchestrator-assembled evidence-map R378 row; G3-3 D15
runbook regeneration incomplete) and observations O1-O3. Recorded as gate FAIL; task moved
to rework; remediation bundles with the G4 verdict into one fresh-producer pass (R395).

---VERBATIM-BEGIN---
I have completed my independent review. Material identity is stable (empty diff for allowed paths from e029c8a to HEAD), scope is contained, and I reproduced the test packs (67 new + 324 modified-file regression tests green; command-doc tooth exit 0; modularity 335 files / 0 failures). Below is my gate report.

---

# G3 (code-reviewer) Gate Report — M0-T126

**Task:** M0-T126 — durable checkpoint design (7 properties) + all in-scope defect corrections + adversarial replay coverage + simulated multi-unit advancement (D-024 Amendment 22, R372-R394)
**Reviewed identity:** `e029c8a` (verified: `git diff e029c8a HEAD -- tools/ .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` empty; HEAD `e0f6cf8`)
**Review diff:** `git diff 1bb7735 e029c8a`
**Reviewer:** code-reviewer (independent, read-only + read-only pytest)

## (a) VERDICT: **FAIL** — 3 reproducible blocking defects on the seven-property core and the R385 "all defects at one identity" bar

The bulk of the work is strong: all 17 register defects have real, spot-checkable, removal-sensitive corrections at the cited seams (verified in code, not just tests), the command-document tooth is genuine/offline/CI-wired, security surfaces are clean, scope is fully contained, and modularity passes. **However**, two of the seven mandated properties are not fully realized as the amendment enumerates them, one carries a **false claim in the acceptance evidence-map**, and one register defect (D15) is only partially corrected. Under R385 ("correct ALL in-scope defects at ONE final frozen identity") and the property mandate ("every fresh **or rotated** worker"; property 3), these must be fixed before the identity is certified. The rework is narrowly scoped (the per-defect table shows what stands).

---

## (b) Per-dimension findings

### Dimension 2 — Seven-property design — **2 defects**

**G3-1 (BLOCKING) — Property 1 orientation is wired for FRESH workers only; the ROTATED path is not wired to the new packet.**
- `orientation.oriented_first_prompt` is invoked at exactly one site: `cli.py:2903` (the fresh-worker first prompt). It is called nowhere in `loop.py` or `loop_turnover.py` (confirmed by package-wide grep).
- The rotated/reoriented path in `loop.run()` uses the pre-existing `loop_turnover.with_reorientation` (`loop_turnover.py:351`), whose `seam.reorientation_prompt` (built at `loop_turnover.py:~44-88`) carries task_id/stage/branch/worktree but **not** the new packet's sized checkpoint **cadence** (early/incremental/reserved-final), **allowed_paths file list**, or **exact-required-output** schema demand.
- The amendment property 1 is explicit: "front-loads … for every fresh **or rotated** worker, including its task, lineage, worktree, current progress, relevant files and exact required output." The most important new element — the **sized cadence that directly addresses D3's "no early checkpoint" failure** — is absent for rotated workers.
- The coverage is misleading: `test_agent_supervisor_orientation.py::FreshVsRotatedTests` (lines 75-94) call `orient.build_orientation_packet(..., rotated=True)` **directly**, testing the module's rotated branch in isolation; no test proves a rotated worker's dispatched prompt actually carries the packet. R387 scenario 1 ("fresh + rotated orientation") is thus only half-wired.
- **Required:** wire `orientation.with_orientation(..., rotated=True)` (or an equivalent enrichment) into the reorientation seam, with a test asserting the dispatched rotated prompt contains the sized cadence + allowed_paths + required-output; or document and justify at the frozen identity why the lighter reorientation satisfies property 1 for rotated workers.

**G3-2 (BLOCKING) — Property 3 "reserved final turn" has no technical enforcement, and the evidence-map claims an injection that does not exist in code.**
- The reserved final turn is realized purely as (a) budget arithmetic `total = working + RESERVED_FINAL_TURNS` (`turn_budget.py:72, 242-254`) and (b) orientation **prompt text** telling the worker "do not start new exploratory tool use in it" (`orientation.py:137-150`). Nothing technically prevents the worker from consuming the "reserved" turn with tool use — the exact live failure mode (12/12 turns all read-only tools, no checkpoint).
- `run_unit` **has** an `extra_turns` stdin channel (`claude_runner.py:1209`, written at `1347-1349`) — the very mechanism the register's D3 line prescribed ("inject a final 'emit the checkpoint NOW' user turn at max_turns-1 via the extra-turns/stdin channel"). But `loop.py:1619` calls `self.runner.run_unit(prompt, permission_handler=…)` **without `extra_turns`** (confirmed: no caller passes `extra_turns` anywhere in the package). No reserved-turn emission is injected.
- The acceptance evidence-map **overclaims**: `M0-T126-evidence-map.json` R378 states "emission turn injected at the reserved boundary via the extra-turns/stdin channel in claude_runner; exploratory tool use prevented where technically enforceable." **This is not reproducible in the code.** (The design-record property-3 row is honest — it only claims sizing + orientation text — but the evidence-map the orchestrator/DCV consume is false.)
- Note: the amendment hedges "wherever technically enforceable," and reactive injection at the turn boundary is genuinely non-trivial with the `--max-turns` streaming model. The safety net (property 4/6: exhaustion → `missing_checkpoint` → PAUSED_RECOVERY, verified by `checkpoint_journey::TurnExhaustionReplayTests`) does hold. So the fix may be evidence-only.
- **Required:** either implement a real reserved-turn enforcement, or restate property 3 honestly (sizing + orientation guidance + fail-closed exhaustion) AND correct evidence-map R378 to not claim a nonexistent injection.

### Dimension 1 — Correctness of the 17 corrections — **1 defect (D15 incomplete)**

**G3-3 (BLOCKING) — D15 runbook regeneration is only partially done.** The register's D15 correction is "regenerate §1/§5/§11 from live sources." The diff to `docs/CONTROLLER_UPDATE_RUNBOOK.md` only adds `--checkout` to the §11 start command. Still present at the reviewed identity:
- §1 stale digests: protected-config `6aef12a9…` (line 18) and model-selection `0e2432c0…` (line 21) — the exact values the register flagged as stale vs live `A1F99501…`/`FCBBF70F…`.
- §5 manifest written **inside** the repo tree: `--out tools\agent_supervisor\controller_manifest.json` (line 90) — the register says certified practice stores it **outside** (`%LOCALAPPDATA%\…\ctl24-activation\`).
- §11 **retired M0-T063** campaign identities: `--branch task/M0-T063…`, `--run-id run_M0_T063_A1` (lines 229-231).
The command-doc tooth validates arg **contracts**, not digests/output-location/retired-identity, so it passes without catching these. At minimum §5 and §11-identity are pure doc edits within the producer's allowed_paths and were not made. **Required:** complete §1/§5/§11 regeneration (or explicitly scope-defer with justification the digest facet if the live config is owner-machine-local).

### Dimension 3 — Regression risk — **PASS**
The frozen-supervisor edits are careful and additive:
- D6 `classify` AMBIGUOUS_EFFECT branch (`recovery.py:428-440`) is gated on `dispatch_intent_pending` (defaults False; `RecoveryContext` at `recovery.py:344-348`), placed after the drift/pending-effect checks and before SAFE_CHECKPOINT, so more-severe classifications still win; the reconciled-control test (`recovery.py` test 299-305) proves it fires only on an unreconciled crash. `reconcile_dispatch_intent` is called unconditionally after `run_unit` returns (`loop.py:1621`).
- D8 routes ROTATE_SESSION via the **pre-existing** `cycle_closed` edge (`state_machine.py:236`, POLICY_CHECK→PREFLIGHT — state_machine.py unchanged) + `rotation.observe_mid_unit` + `rotate_session` added to `CONTEXT_SHEDDING_REASONS`; the run still `stop("rotate_session", …)`. Legal and removal-sensitive (`test_agent_supervisor_loop.py:436`).
- D11/D12 `_intent_stop` uses `may_dispatch_new_work`, which returns True (no stop) only for `INTENT_NONE` (`stop_intent.py:144-149`), so a normal run is never falsely stopped; `effective_intent` default is `none`.
- D5 `_ceiling_context_tokens` falls back to cumulative when live is unknown (conservative direction preserved). D4 field/audit-key rename is clean — **no stale references** to `native_tools_guidance_appended` remain anywhere.
- D13 `machine.assert_can_act()` correctly precedes `budget_ledger.start()` (`cli.py:2752-2758`).
- Owner gates, R595/bounded-mode gate, broker allowlists, audit chain, and in-process exactly-once forwarding are untouched. All 324 loop/recovery/runner/launch_seam tests reproduce green.

### Dimension 4 — Security surfaces — **PASS**
- `command_docs.py` / `supervisor_command_doc_check.py` **never execute** presented commands: they only `shlex.split` (tokenize) and `argparse.parse_args` (dry-run) — no `subprocess`/`os.system`/`exec`/`eval`/`Popen` (grep-confirmed). `_parse_quietly` traps `SystemExit`/stderr; templates with `<placeholder>` and non-supervisor lines are skipped.
- `.github/workflows/ci.yml` adds one fixed `run: python tools/supervisor_command_doc_check.py` step (no interpolation/injection surface, no new `uses:` action to pin, no permissions change), placed in the existing supervisor-test job.
- Fixtures `m0t107_journey_facts.json` / `m0t107_stream_d5.json` carry no secrets/tokens/PII (only a UUID session id and numeric facts; the sole "secret" grep hit is the provenance note "secrets-free"). Public-repo safe.

### Dimension 5 — Scope containment — **PASS**
All 24 changed production/test/doc files are inside `allowed_paths` (`git diff 1bb7735 e029c8a --name-only`). Control-plane files (directives, reports, state.json, tasks/M0-T126.json) were committed separately by the orchestrator — permitted.

### Dimension 6 — Quality / G3-T125 citation fixes — **PASS**
- `python tools/modularity_check.py --check` → selected 335 files; failures 0; warnings 10 (pre-existing, unrelated). New modules are focused, well-documented leaves. loop.py 2030/2088 (headroom); claude_runner/cli net-zero at limit.
- G3-T125 citations bound in the design record are accurate: D9 enter-COMPLETE at loop.py:2041-2042; the 604772 figure recorded at `rotation_figure_seq 21` in `m0t107_journey_facts.json`; D7 R595 note cites `remote_approvals.py:295/307`.
- No dead code / misleading names in the new modules; the `import re` removal and `# noqa: F401` re-export facades are justified.

---

## (c) Per-defect correctness table (D1-D17)

| Defect | Verdict | Basis |
|---|---|---|
| D1 command-derivation drift | CORRECT (note) | `command_docs.py` tooth + CI + `test_removing_each_pinned_flag_fails`; scope narrowed to living runbook (certification reports not scanned) — documented deviation, see Observation O1 |
| D2 `--repo` primary-checkout leak | CORRECT | `launch_seam.evaluate_repo_binding`/`enforce_launch_bindings` (launch_seam.py:242-289) wired at cli.py:2657; `CliRepoBindingGateD2` |
| D3 fixed 12-turn / sizing unwired | CORRECT (sizing) | `turn_budget` class-based sizing wired via `sized_max_turns` (cli.py:2668-2712); reserved-turn **enforcement** caveat → G3-2 |
| D4 degenerate native flag | CORRECT | renamed `native_tools_guidance_present`, sentinel-presence after both appends (claude_runner.py:1226-1237); no stale refs; 3-shape test |
| D5 cumulative-vs-live tokens | CORRECT | `live_context_tokens` (claude_runner.py:730-740), separate fields, `_ceiling_context_tokens` consumes live (loop.py:555-568); 72546 vs 694251 + exact-400000 tests |
| D6 journal-order / START_CLAUDE rest | CORRECT | `record/reconcile_dispatch_intent` + AMBIGUOUS_EFFECT branch; 3 crash rows + reconciled control |
| D7 dead safe_auto_resume / epilogue | CORRECT | R595-gated doc (recovery.py:462-471) + operator-start epilogue annotation (cli.py:3147) |
| D8 PREPARE_ROTATION strand | CORRECT | routed through `cycle_closed`→PREFLIGHT + rotation_pending + shedding-reason; removal-sensitive test |
| D9 COMPLETE strand / next-task | CORRECT (note) | `plan_close_run` wired at cli.py:2687; exactly-once `next_task` machinery proven against real journal; live autonomous selection intentionally simulation-only (Observation O2) |
| D10 forwarded-prompt loss / dup-id | CORRECT | `_persist/_consume_next_unit_prompt` + advancing cycle wired in `loop.run`; cross-process removal-sensitive test; golden restart row corrected |
| D11 between-cycle stop/pause | CORRECT | `_intent_stop` between-cycle seam (loop.py:2696-2716, 2799-2806) |
| D12 graceful-stop no consumer | CORRECT | folded into `_intent_stop` via `may_dispatch_new_work` |
| D13 budget-before-gate | CORRECT | `assert_can_act()` before `budget_ledger.start()` (cli.py:2752-2758) |
| D14 argparse requires nothing | CORRECT | tooth pins 5 flags + dispatch inputs; `missing_pinned_flag`/`dispatch_inputs_missing` verdicts |
| **D15 runbook drift** | **INCOMPLETE** | only §11 `--checkout` pinned; §1 stale digests (lines 18/21), §5 manifest-inside-tree (line 90), §11 retired M0-T063 identities (lines 229-231) remain → **G3-3** |
| D16 legacy/dead-child sweep | CORRECT | `sweep_dead_child_records` archives with provenance (recovery.py); D5 live-figure fold for (i); test |
| D17 no test consumes presented commands | CORRECT | the tooth + CI step is the removal-sensitive test |

## (d) New defects found
- **G3-1, G3-2, G3-3** above (property 1 rotated wiring; property 3 enforcement + false evidence-map R378; D15 incomplete).
- **O1 (observation, non-blocking):** the command-doc tooth scans only `docs/CONTROLLER_UPDATE_RUNBOOK.md`; the register's D1 said "certification docs + runbook." Documented deviation in `supervisor_command_doc_check.py`. Note the original live defect lived in a *certification report* (M0-T124 §5) — the tooth as-scoped would not catch a bad presented command in a future certification report. Recommend the certification checklist re-derive presented commands from the (now-validated) runbook.
- **O2 (observation, non-blocking):** D9's `record_advancement`/`select_next_packet`/`advance_and_select` are exercised only in simulation (`test_agent_supervisor_next_task.py`), not wired into the live loop (only `plan_close_run` is). This is defensible and consistent with R388 ("simulated") and R595/no-live-launch; the "feeding a fresh start_command" autonomous tail is intentionally deferred to the R393 live commissioning. Recorded for the orchestrator's awareness.
- **O3 (observation):** the full ~3h13m `test_agent_supervisor_golden_run.py` (R247/R390 recert) was not run in-window (packet-assigned to M0-T127). The producer changed one golden restart row that "passed only via the D10 bug" — the change is legitimate and disclosed, but the full golden pack must be re-run at the certified identity before M0-T127 recert PASS.

---

**Requested gate result: FAIL.** Reproducible defects G3-1/G3-2/G3-3 with the commands and file:line above. The 17-defect corrections are otherwise sound and independently verified, so a fresh producer pass can remediate narrowly (wire rotated orientation + a dispatch-level test; reconcile property 3 vs evidence-map R378; finish D15 §1/§5/§11) at a new frozen identity, then re-gate. I made no writes outside `.claude/agent-memory/code-reviewer/`, and ran no `project_control.py`/git-write/`gh`/supervisor write verb (read-only `git diff/log/show`, grep, `pytest`, `modularity_check.py --check`, and the offline `supervisor_command_doc_check.py` only).
---VERBATIM-END---
