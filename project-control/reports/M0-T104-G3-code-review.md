# M0-T104 G3 code review (round 1) — VERBATIM reviewer return

Orchestrator note: saved verbatim from the code-reviewer agent-return channel (transport
entity-decoding only: `&lt;` → `<`). Review conducted at deliverable identity `ac305ae`
(HEAD `b8ce5cb`, control records only). Reviewer preamble line retained.

---

Full agent_supervisor suite: **2204 passed, 2 skipped, 0 failed** (558s) — freeze baseline re-established, no regression. I have everything needed. Here is my gate report.

---

# G3 Gate Report — M0-T104 (D-024 Amendment 3 unit C: native runtime adapter)

**Reviewer:** code-reviewer (independent, read-only)
**Task:** M0-T104 · **Gate:** G3 · **Deliverable identity:** commit `ac305ae` (HEAD `b8ce5cb` adds only control-plane records; scoped files identical)
**Verdict: PASS** (one MEDIUM required-correction carried to the consuming unit; four ADVISORY)

## Scope reviewed (exact files)
- `tools/agent_supervisor/native_runtime.py` (NEW, 614 pl)
- `tools/agent_supervisor/runtime_backend.py` (NEW, 270 pl)
- `tools/test_agent_supervisor_native_adapter.py` (NEW, 53 tests)
- `tools/test_agent_supervisor_capability_probe.py` (MODIFIED — drift-tooth re-baseline)
- 4 fixtures (`*_2026-08-27_m0t104.json`)

## Reproduction (commands run, read-only)
| Command | Result |
|---|---|
| `python -m pytest tools/test_agent_supervisor_native_adapter.py tools/test_agent_supervisor_capability_probe.py -q` | **72 passed in 20.29s** (live rows executed against installed claude 2.1.247) |
| `python tools/modularity_check.py --check` | **failures 0; warnings 5** — 5 warnings are pre-existing files; neither new module flagged |
| `python -m pytest tools/ -k agent_supervisor -q` | **2204 passed, 2 skipped, 560 deselected in 558s** — supervisor-freeze baseline (≥1165/0 failures) re-established |
| Fixture inventory | `capability_probe_live_2026-08-25.json` (2.1.220) + `..._m0t103_post_update.json` (2.1.246) still present and invariant-checked; new `..._m0t104.json` (2.1.247) added |
| Consumer grep | new modules imported ONLY by their own test file — no production caller yet (consistent with R180 sequencing) |

## Correctness verified against the MEASURED facts (report §3)
Confirmed in source, not from producer claims:
1. **`--bg` ignores `--session-id`** — `build_background_argv` (native_runtime.py:408-433) never emits `--session-id`; identity rides on `--name`; `find_by_identity` (566-575) matches UUID-first then name (the name-fallback is what actually maps real daemon-assigned UUIDs). Pinned by `test_build_background_argv_canary_measured_constraints`.
2. **Variadic `--tools` swallows the prompt → literal `--` separator** — prompt always appended after `"--"` (line 428). Pinned by `test_build_background_argv_exact` (exact-tuple assertion; removing `--` reddens it) and the empty-`--tools` case.
3. **Unknown subcommand `--help` exits 0 with general usage** — `_classify_verb` (160-172) classifies by the verb-specific `Usage: claude <verb>` first line, never by exit code. Pinned by `test_unknown_verb_general_help_is_not_supported` (all four branches).
4. **UTF-8 vs cp1252** — `run_command` pins `encoding="utf-8", errors="replace"` (line 103); never raises.
5. **status/state literal inventory** — `_classify_row` (490-514): `state` outranks `status`; parked `waiting`+`failed` → FAILED; `idle` alone → blocked-input; unmeasured combos → UNKNOWN. Pinned by the parse/completed/idle-stopped/unknown tests.

**Fail-closed behavior confirmed everywhere it matters:** selection degrades to controller on any non-`supported` capability incl. `unknown`/probe-failure/absent (`background_gaps`, `select_runtime_backend`); `parse_agents_json` raises a typed error on malformed/non-array/missing-sessionId; `reconcile_after_restart` re-buckets any non-listed classification (incl. UNKNOWN) to blocked-input and only ever exposes `unexpected_exit` as `safe_to_dispatch` — the no-duplicate core. One-backend invariant (`RuntimeSession.activate`) refuses a second activation with a typed error. All strongly pinned.

**Determinism:** no timestamps/caching in `BackendSelection`, `build_detection_fixture`, `build_agents_fixture` (drops pid/startedAt); detection is measured-at-use every call (`test_detection_measures_at_every_call`, 2.1.247→2.1.248). Good.

**Drift-tooth re-baseline:** historical invariants intact — `test_upgrade_pair_records_expected_versions` still freezes 2.1.220 (live) and 2.1.246 (post) with codex unchanged; `test_post_update_fixture_masked_and_shaped` unchanged. Only the two live drift teeth were re-pointed to the 2.1.247 `current` fixture, and `test_current_fixture_records_2_1_247_masked_and_shaped` was added. Matches the packet exactly. The frozen `capability_probe.py` module is byte-unchanged (adapter carries its own detection). Correct.

## Findings

**1. MEDIUM — fail-open child-environment default in `NativeBackgroundBackend.dispatch`** (`runtime_backend.py:139-150`).
When the backend is constructed without `base_env` (the default, and the exact pattern used by the non-dispatch tests — e.g. `test_observe_*`, `test_stop_logs_respawn_attach_argv` build `NativeBackgroundBackend(run)`), `dispatch` computes `env = ... if self._base_env is not None else None` and passes `env=None` to `run_command`, so the subprocess **inherits the full parent environment** — the `CLAUDECODE` / `CLAUDE_CODE_*` session markers are NOT stripped. This directly contradicts the module's stated invariant (`native_runtime.py:24-29`: "the child environment is therefore always explicit, never inherited as-is") and the R162-discharge §4.3 transcript-suppression control. `child_environment()` itself is correct and tested, but nothing pins that `dispatch` ALWAYS applies it — S13's test exercises only the pure helper and the base_env-provided path.
*Failure scenario:* a future consumer (units F–H) wiring native dispatch via `NativeBackgroundBackend(run)` (no `base_env`) dispatches a background producer that inherits `CLAUDE_CODE_CHILD_SESSION`/`CLAUDECODE`, silently suppressing its transcript — the precise hazard this module documents.
*Not exploitable in this deliverable* (no production caller; dispatch invoked only in tests with explicit `base_env` — grep confirms zero non-test consumers). Recommended fix: make `base_env` mandatory for `dispatch` (raise `NativeRuntimeError` when `None`) or default to `child_environment(os.environ)`. **Must be resolved before any unit wires native dispatch**; it does not break the seam-only scope delivered here.

**2. ADVISORY — responsibility mixing in `native_runtime.py`.** The 614-line module mixes external I/O (`run_command`/subprocess), domain logic (identity, classification, validation, argv builders), and serialization/presentation (`build_detection_fixture`, `mask_session_row`, `build_agents_fixture`). `code-architecture.md` rule 3 asks these be separated. It passes the checker (SLOC well under warn; not flagged) and is cohesive around "the native CLI surface," and the R145/R180 one-bounded-seam intent argues against over-splitting — but the fixture/masking serialization group is a clean extraction candidate if the file grows.

**3. ADVISORY — `--session-id` in `REQUIRED_BACKGROUND_FLAGS`** (`native_runtime.py:129`) is required for native readiness yet deliberately never emitted by the builder (measured: `--bg` ignores it). The gate is conservative/fail-closed (a future CLI dropping it from help falls back to the proven controller), but the "required-in-help but never-emitted" coupling deserves an inline comment so a maintainer doesn't read it as a bug.

**4. ADVISORY — classifier literal inventory diverges from report §3.5.** `_classify_row` recognizes literals beyond the report's measured set (status: `completed/done/finished/running/working`; state: `completed`). All map to the semantically-obvious class, none flip a live/blocked session into a "safe-to-ignore" state, and unmeasured combos still fall to UNKNOWN (parked as blocked-input in reconcile) — direction is safe. Align the code docstring inventory (line 490-497) with the report's measured inventory to keep provenance honest.

**5. ADVISORY — packet lacks structured seven-answer modularity block.** `M0-T104.json` addresses modularity only narratively (report/self-check) though the checker passes. Process note, not a code defect.

## Not applicable
No DB schema / migration / RLS / hard-coded legal values in this tooling task (schema strings are self-consistent fixture-version tags). Independent directive verification (R153/R154/R156/R172 → `verification.json`) is the `directive-compliance-verifier`'s deliverable, not this G3 pass; I confirmed the report §6 evidence map is reproducible against source but did not produce the DCV row.

## Rationale for PASS
The delivered scope — a bounded, un-wired native-runtime adapter seam — is correct, deterministic, fail-closed in selection/parse/reconcile/identity, honestly records the measured CLI limitations, preserves the frozen 2.1.220/2.1.246 probe invariants while correctly re-baselining the live drift teeth to 2.1.247, and carries strong mutation-resistant tests (exact-argv, state-wins-conflict, one-backend refusal, capability-gap fallback). All 72 in-scope tests and the full 2204-test supervisor freeze suite pass with zero failures. The single MEDIUM is a fail-open default on a control that has no production caller in this change and is a required correction for the consuming unit, not a defect in the seam delivered.

**VERDICT: PASS** — with finding #1 (MEDIUM) recorded as a blocking correction for whichever unit first wires native dispatch, and findings #2–#5 as advisories.
