<!-- Saved VERBATIM by the orchestrator from the G3 code-reviewer agent-return channel
     (transport entity-decoding only). Review head a0c48b0, material identity 7d8195b. -->

I have completed a thorough independent review. All production files, the fold, the tooth logic, the probe, the seeding path, the tests, and the classifier-untouched claim have been verified against the actual source at the frozen identity. Here is my complete G3 report.

---

# G3 GATE REPORT — M0-T120 (D-024 Amendment 14: shell-routing compatibility)

**Reviewer:** independent read-only G3 (code-reviewer + security-reviewer pass)
**Reviewed identity:** control head `a0c48b0`, material identity commit `7d8195b` (14 files, +2165/-8), checkout `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch `control/D-024-fable-codex-loop`. Tree clean; no uncommitted deltas.
**Directive regime:** in-regime (`directive_refs: D-024 ALL`). Qualifying evidence **D-024-R291** cited in both packet and commit message (supervisor-freeze §2/§3 satisfied).

## Commands run + key output

```
git rev-parse HEAD                       -> a0c48b08528c...  (clean)
git show --name-only 7d8195b             -> 14 files; production changes limited to
   claude_runner.py, golden_run.py, recovery_probes.py, routing_probe.py, start_gate.py,
   prompts/claude_native_tools.md (NEW), fixtures/shell_routing_...json (NEW)
   -> policy.py, broker.py, cli.py, command_authority(prod), process.py, checkpoint.md NOT in diff

python -m pytest tools/test_agent_supervisor_golden_run.py tools/test_agent_supervisor_bounded_mode.py \
  tools/test_agent_supervisor_routing_probe.py tools/test_agent_supervisor_recovery_probes.py \
  tools/test_agent_supervisor_command_authority.py -q
   -> 301 passed in 40.14s   (exit 0)   [producer estimate ~253; packs grew — 301 is the actual]

python tools/modularity_check.py --check -> exit 0, failures 0 (warnings pre-existing)
```

## Item-by-item findings

### 1. The R295 gate fold — load-bearing (VERIFIED)
- The fold in `start_gate.live_revalidation` (`tools/agent_supervisor/start_gate.py:228-231`) ANDs `cli_capability_manifest` with `answers["shell_routing"].passes`. A failing/undetermined routing tooth drifts `cli_capability_manifest`, which `recovery.classify` turns into `UNSAFE_OR_DRIFTED` before any provider contact. Proven end-to-end: `dispatched=False`, `provider_calls_made=0`, `recovery.classification == UNSAFE_OR_DRIFTED`, `exit 11` (golden test asserts all four).
- **Identity source is a file DIGEST, no spawn:** `_claude_identity_digest` (`start_gate.py:94-109`) returns `executable_identity(executable).digest` (binary hash); an unresolvable identity returns `""` → `probe_shell_routing_evidence` yields `cli_version_undetermined` → fail closed (`recovery_probes.py:757-761`). Test `test_the_gate_helper_sources_identity_by_file_hash_not_a_spawn` (`test_agent_supervisor_bounded_mode.py:1404-1412`) confirms it equals `executable_identity(...).digest` and `""` for empty input.
- **Not bypassable by config/synthesized argv:** the digest is computed from binary content (argv only names the path); there is no skip flag; pointing `--claude-executable` elsewhere yields no matching evidence → fail closed. No config key disables the fold.
- **Tooth-bite golden test exercises the REAL production path:** `TwoUnitGoldenRunTests::test_the_routing_tooth_bites_a_certified_start_without_evidence` (`test_agent_supervisor_golden_run.py`, added in diff) drives the real `cli.main(["start", …])`, whose `cmd_start` calls `live_revalidation` (`cli.py:2898`) → `recover_boot` (`cli.py:2906-2908`) → `recovery.classify`. Not a hand-built map — the genuine dispatch path.

### 2. ADJUDICATION OF THE MODE-SCOPING RULING — **CONCUR / SATISFIES R295**
The gating effect applies only when `mode == MODE_LIMITED_AUTO` (`start_gate.py:228`); the tooth still runs and reports in every mode (`recovery_probes.py:908-915`, `FOLDED_PROBES` includes `shell_routing`).
- `MODE_LIMITED_AUTO = "limited-auto"` (`loop.py:131`) is the **only** `OWNER_GATED_MODES` entry (`loop.py:143`) and the **only** mode for which `LoopConfig.unattended` is True — *"nobody is watching"* (`loop.py:344-354`). `LoopConfig.forwards` (`loop.py:333-342`): **shadow forwards nothing, ever**; **supervised forwards but "holds every prompt for an operator approval bound to its digest."** Therefore neither shadow nor supervised is a *silent* entry path. R295 protects *"changed shell-routing behavior cannot silently enter a **certified** run"* — the certified/unattended run is exactly `limited-auto`. The scoping is faithful to the requirement's text.
- **Mode guard cannot be spoofed to dodge the gate:** to reach the unattended/certified loop you must pass `--mode limited-auto` and `--owner-enable-bounded-auto`; `LoopConfig.__post_init__` (`loop.py:303-320`) makes `limited-auto` the only owner-gated/unattended mode. "Dodging" the gate means *not* being limited-auto, which is not a certified run — there is no ungated certified path. Comparison is `==` against the imported module constant (clean provenance).
- The recovery_probes end-to-end tests were updated to `[s for s in failed if s != "shell_routing"] == []`, which is the correct, narrow acknowledgement that in shadow/supervised the folded tooth reports its failure but does not gate — not a weakening (all other probes must still pass).
- **VERDICT ON THE RULING: it satisfies R295 and the mode guard is implemented safely.**

### 3. Seeding is not a bypass (VERIFIED)
- `record_routing_evidence` (`recovery_probes.py:618-639`) writes only the **durable journal** key `SHELL_ROUTING_EVIDENCE_KEY`, never the shipped `fixtures/` dir. Its sole caller is `golden_run.seed_routing_evidence` (`golden_run.py:420-443`, test harness). No production start path (`cli.py`/`loop.py`/`start_gate.py`) seeds evidence — `start_gate.py:216` is a comment only. `golden_run.py` is imported by no production module (the `telegram_sink.py` grep hit is the string literal `"golden_run_complete"`, not an import).
- No production code special-cases fake/golden digests — all grep hits are docstrings; `probe_shell_routing_evidence` matches whatever identity is passed against whatever records exist — identical logic for real and fake.
- Shipped fixtures dir is not written by any test (grep clean).
- Committed real fixture `cli_identity d6f6c29a…` matches only the exact digest (`_dir_routing_records` + exact-string match, `recovery_probes.py:768-783`); `test_the_committed_fixture_passes_for_the_real_claude_digest` (`test_agent_supervisor_routing_probe.py:246`) confirms.

### 4. Probe honesty and bounds (VERIFIED)
- Deny-everything: `_DenyRecorder.__call__` delegates to `deny_everything` (`routing_probe.py:157`) — cannot accidentally allow.
- ≤3 provider calls, structural: `DISCOVERY_MAX_TURNS=1` + `EDIT_MAX_TURNS=2` via the CLI's own `--max-turns`; explicit post-run backstop (`routing_probe.py:436-439`). Measured fixture records `provider_calls_made: 3`, ceiling 3.
- No repository paths: assignments run in a `tempfile.TemporaryDirectory` (`routing_probe.py:409-411`); prompts reference only "THIS directory."
- No file writes: `_dir_snapshot` before/after each assignment (`routing_probe.py:260-276`); fixture `no_worker_file_write_observed: true`.
- Honest labels: `measured` flag + `measured_note`; a launch failure records `measured=False` with `error` and is explicitly "NOT evidence."

### 5. Prompt guidance seam (VERIFIED)
- `claude_native_tools.md` loaded from disk (sentinel-slice, fallback copy) and **folded into `build_checkpoint_contract`** (`claude_runner.py:909-913`) so it rides the single existing append seam; `with_native_tools_guidance` (`claude_runner.py:923-935`) and `run_unit` (`claude_runner.py:1170-1175`) are sentinel-guarded → idempotent, never duplicated.
- `assert_worker_text_clean` preserved: the guidance carries no quota/percentage/countdown/pressure (prompt file states this for D-024-R045); test `test_the_guidance_is_worker_text_clean`.
- Broker untouched: `policy.py`, `broker.py`, `cli.py`, and the production classifier are byte-untouched (not in diff). The 13 command-authority additions call the real `pol.evaluate` (`test_...command_authority.py:58,85`) and are **assertions only** (`WindowsShapeCoverageTests`), each asserting ASK or HARD_DENY, never AUTO.

### 6. Tests re-run + removal sensitivity (VERIFIED)
- Five required packs: **301 passed, exit 0** (reported actual vs the ~253 estimate).
- Removal sensitivity is real, not asserted: un-seeding via `clear_routing_evidence` re-reds the certified start through the real CLI (golden tooth-bite test); producer RED evidence (routing-evidence §3) shows the R295 tooth stubbed → 3 fails and the R294 guidance no-op → 1 fail. Registration/fold coverage: `test_the_shell_routing_tooth_is_registered_and_folded` and `test_a_stale_cli_version_fails_the_routing_tooth_in_the_sweep` (recovery_probes pack).

### 7. F1/F2 classifier-permissiveness findings — CONCUR with recording; two follow-ups recommended (non-blocking)
Both are recorded-not-fixed and remain **ASK, never AUTO**, captured as explicit tests (`test_finding_f1_*`, `test_finding_f2_*`). Leaving them ASK is correct for THIS unit — R293 explicitly forbids any classifier change here, and an ASK in the certified/unattended loop **parks the run for a human; it never auto-executes**, so there is no silent-proceed hole. Concurrence with the recorded disposition:
- **F1** (`python gen.py | sh` → ASK, not HARD_DENY concealed_execution): acceptable to leave ASK; a follow-up to consider hardening bare pipe-to-interpreter to HARD_DENY is reasonable but low priority. (INFO)
- **F2** (`powershell -Command "Remove-Item -Recurse -Force …"` → ASK, not HARD_DENY recursive_or_wildcard_delete): more notable — a destructive delete that is HARD_DENY when bare is only ASK when wrapped in a quoted `-Command`/`cmd /c` argument, meaning a human *could* approve it whereas HARD_DENY never can. Still gated (never AUTO/silent), so not a blocker, but I recommend a **follow-up ledger task** to extend destructive-segment/credential detection inside quoted interpreter arguments. (MINOR)

## Numbered findings

1. **INFO — R295 fold correct and fail-closed.** `start_gate.py:228-231` + `_claude_identity_digest` (`start_gate.py:94-109`); end-to-end tooth-bite via real `cli.main` (golden test). No defect.
2. **INFO — mode-scoping ruling adjudicated: SATISFIES R295, safely implemented.** `loop.py:131/143/333-354`, `start_gate.py:228`. No ungated certified path exists.
3. **INFO — seeding confined to test harness; no production bypass, no fake-digest special-casing, shipped fixtures dir never written by tests.** `recovery_probes.py:618-639`, `golden_run.py:420-456`.
4. **MINOR — F2 classifier gap (powershell-wrapped destructive delete downgrades HARD_DENY→ASK).** Recorded-not-fixed correctly per R293; still gated (never AUTO). Recommend a follow-up task to close the quoted-argument gap. `test_...command_authority.py` F2 test; classifier `policy.py` unchanged (correct for this unit).
5. **MINOR — F-LIVE-1: installed 2.1.251 reports `permissionMode=default` despite `--permission-mode manual`; read-only tools auto-allowed and never reach the broker.** Verified benign for writes — mutating tools (Edit/Write) still emit control_requests and were DENIED (fixture: Edit brokered+denied, `no_worker_file_write_observed: true`). Out of R293 scope; recommend a follow-up to track the CLI flag-handling. `routing-evidence.md §1`.
6. **INFO — F1 (`| sh` → ASK not HARD_DENY).** Gated, never AUTO; candidate follow-up. Recorded-not-fixed correctly.
7. **INFO — `recovery_probes.py` now 947 SLOC, crossing the 750 justification threshold (warn; under the 1000 hard limit).** `modularity_check --check` exit 0, failures 0. Placement is cohesive: the shell-routing tooth is a genuine S11.5 pre-dispatch revalidation probe living beside `probe_cli_capability_manifest`, whose pinned-identity story it strengthens. Recommend recording a one-line cohesion justification (or considering a future extraction of the tooth section); not blocking.
8. **INFO — pre-existing `F401` unused import (`AuditLog`) in `test_agent_supervisor_recovery_probes.py`** originates from M0-T115, not this diff; `tools/**` is not CI-linted (CI ruff scopes `services/api/`). No action for this unit.

No BLOCKER or MAJOR findings. The load-bearing R295 fold is correct, fail-closed, non-spawning, and non-bypassable; the mode-scoping ruling is faithful to R295 and safely implemented; seeding is test-harness-only; the probe is bounded and honest; the broker/classifier are byte-untouched; the tests are removal-sensitive through the real production path.

**Relevant absolute paths:**
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/start_gate.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/recovery_probes.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/routing_probe.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/claude_runner.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/golden_run.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/prompts/claude_native_tools.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/fixtures/shell_routing_2026-08-29_m0t120_2_1_251.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/loop.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/cli.py`
- Test packs: `test_agent_supervisor_{golden_run,bounded_mode,routing_probe,recovery_probes,command_authority}.py`

Recommended orchestrator follow-ups (new tasks, not reopening M0-T120): (a) classifier hardening for quoted-argument destructive/interpreter shapes (F2, then F1); (b) track 2.1.251 `--permission-mode manual` handling (F-LIVE-1); (c) record the recovery_probes.py cohesion justification or plan an extraction.

**G3 VERDICT: PASS**
