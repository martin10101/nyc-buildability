<!-- Saved VERBATIM by the orchestrator from the G5 security-reviewer agent-return channel
     (transport entity-decoding only). Review head a0c48b0, material identity 7d8195b. -->

I have completed the independent verification. All structural claims are confirmed and the security-relevant tests pass under my own execution. Here is the complete G5 report.

---

# G5 SECURITY GATE REPORT — M0-T120 (D-024 Amendment 14, shell-routing compatibility)

**Reviewer:** security-reviewer (independent, read-only)
**Task:** M0-T120 — shell-routing compatibility unit (Amendment-14 rows R289–R297)
**Reviewed identity:** control head `a0c48b0`, material identity `7d8195b` (14-file delta)
**Repo:** `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`
**Directive regime:** in-regime (`directive_refs: D-024:ALL`); prohibition under test is **R293**
**Gate:** G5 (security); scope = do-not-modify, review clean diff, run security checks

## Verdict

**G5 VERDICT: PASS**

No SEC-BLOCKER and no SEC-MAJOR findings. Five SEC-INFO / one SEC-MINOR observations, all recommendation-only (consistent with R293's no-change-this-unit constraint). The core prohibition (broker/classifier/owner-gates untouched, never AUTO) holds byte-for-byte; the gate fold is fail-closed and not worker-dodgeable; the live probe has no reachable effect and is not certified-run-reachable; shipped artifacts are PII-clean.

---

## What I verified independently (read-only commands run)

```
git log --oneline -5 a0c48b0
git show --stat 7d8195b                       # 14 files, +2165/-8
git show 7d8195b --name-only --format=""       # exact delta file list
git show 7d8195b -- <each production file>     # per-file diffs
ls tools/agent_supervisor/*.py | grep -iE "policy|broker|classif|command|cli"
grep -rn "MODE_LIMITED_AUTO" tools/agent_supervisor/*.py
grep -n "OWNER_ACTIVATION|HARD_DENY_ARGUMENTS" tools/agent_supervisor/process.py
grep -rn "record_routing_evidence|seed_routing_evidence|routing_probe" tools/
grep -rn "import golden_run|golden_run import" tools/ --include=*.py
Read: routing_probe.py, probe_result.py, claude_native_tools.md, the fixture,
      start_gate.py, recovery_probes.py diff, claude_runner.py diff, golden_run.py diff
python -m pytest tools/test_agent_supervisor_command_authority.py::WindowsShapeCoverageTests \
      tools/test_agent_supervisor_bounded_mode.py -q      => 104 passed
python -m pytest tools/test_agent_supervisor_recovery_probes.py -k "routing|drift|Journal|stale|evidence" -q  => 23 passed
python -m pytest tools/test_agent_supervisor_routing_probe.py \
      tools/test_agent_supervisor_golden_run.py -q         => 77 passed
```

I did not run the full 2782-test suite (Python 3.11 sandbox; repo targets 3.12); I ran the 204 security-relevant deterministic tests directly and they pass, consistent with the recorded 2780/2/0.

---

## Item-by-item security review

### 1. R293 compliance — the core prohibition — PASS

**Classifier/policy/broker byte-untouched:** the 14-file delta list (`git show --name-only`) contains **no** `policy.py`, `broker.py`, `cli.py`, or `workload_classifier.py`. Those modules exist in the tree but are outside the delta — conclusively byte-identical at `7d8195b`. The only classifier-adjacent change is **test assertions** in `tools/test_agent_supervisor_command_authority.py`.

**No new AUTO classification:** `WindowsShapeCoverageTests` (`test_agent_supervisor_command_authority.py`, `WindowsShapeCoverageTests.assertNeverAuto`) drives the **real** classifier via `classify(command, fixture_authority())` and asserts `tier ∈ (ASK, HARD_DENY)` plus `assertNotEqual(tier, AUTO)` for all 13 shapes (here-strings, `&`/`&&` chains, redirection, `;`/`&&` compounds, pipelines, scratch-copy, ambiguous `$env:` read → ASK; `iex`/`-EncodedCommand`, `.netrc` read, `del /s`, `--no-verify` → HARD_DENY). I ran these: **104 passed**.

**The two recorded permissiveness findings are honestly recorded, gated, and test-locked** (`test_finding_f1_pipe_to_interpreter_is_ask_not_hard_deny`, `test_finding_f2_powershell_wrapped_delete_is_ask_not_hard_deny`, lines 157–168 of the diff): `python gen.py | sh` → ASK `undocumented_command`; `powershell -Command "Remove-Item -Recurse -Force ..."` → ASK `undocumented_command`. Neither is silently fixed (classifier frozen per R293) nor silently accepted (both carry pinning tests). See my ASK-shape opinion below.

### 2. The gate fold as a security control — PASS (not dodgeable)

**Mode-string provenance (owner-typed vs synthesizable):** the fold gates only when `getattr(args, "mode", "") == MODE_LIMITED_AUTO` (`start_gate.py:228`). `MODE_LIMITED_AUTO = "limited-auto"` (`config.py:53`) is the **same constant that authorizes unattended self-forwarding** — `loop.py:354` `unattended` is true iff `mode == MODE_LIMITED_AUTO`, and `loop.py:304` additionally requires `owner_enabled_bounded_auto` (else `LimitedAutoRefused`). `args.mode` is an operator argparse value, not worker-reachable/synthesizable. Because "the mode that enables unattended dispatch" and "the mode the gate checks" are the identical string, **there is no mode value that yields unattended dispatch while skipping the gate**. Shadow forwards nothing; supervised holds every prompt for a digest-bound human approval (`loop.py:342` `forwards`); only limited-auto self-forwards AUTO-tier prompts — and that is exactly what the gate covers.

**Stored config/argv pre-answering the probe:** evidence is read from the shipped fixtures dir + durable journal (`recovery_probes.probe_shell_routing_evidence`). In the production fold, `installed_cli_identity=_claude_identity_digest(args.claude_executable)` is supplied, so a match **requires `fx_identity == installed digest`**; a different/stale identity yields `routing_evidence_stale` (fail). The weaker version-string fallback runs only when `identity==""`, and an empty identity produces `cli_version_undetermined` → fail-closed. No argv/config value can assert a passing digest that doesn't equal the actual binary hash.

**Journal-seeded evidence write path (production reachability):** `record_routing_evidence` has exactly **one** non-test caller in the whole tree — `golden_run.seed_routing_evidence` — and `golden_run` is imported **only** by `test_agent_supervisor_golden_run.py`. It is not referenced by `cli.py`, `loop.py`, or `start_gate.py`. **A worker (or any worker-controlled input) cannot cause a routing-evidence record to be written in production.** Forging the shipped `fixtures/` dir would require package/repo write access — the same trust boundary as editing the classifier itself, not a worker path.

**Digest-keying consistency (no weaker parallel path):** `start_gate._claude_identity_digest` calls `process.executable_identity(executable, name="claude").digest` — byte-for-byte the same call `cli._claude_cli_identity` uses (`cli.py:590`) and the same identity the capability manifest pins. The routing tooth reuses the pinned-CLI drift machinery rather than introducing a parallel, weaker check.

**Fail-closed proof:** `probe_result.ProbeResult.passes = ok AND known`; `_unknown`/`_fail` → `passes=False`. The fold ANDs `answers["shell_routing"].passes` into `cli_capability_manifest`, which `recovery.classify` turns into `UNSAFE_OR_DRIFTED` before any provider contact. `shell_routing` is a `FOLDED_PROBE` (not in `STEP_PROBES`), so its only gating effect is this explicit AND. Removal-sensitivity confirmed by my run of the drift-tooth tests (**23 passed**) and the golden tooth-bites test (`test_the_routing_tooth_bites_a_certified_start_without_evidence`, in the **77 passed** run).

### 3. Live probe surface — PASS (no effect, not certified-run-reachable)

`routing_probe.py` launches the real `claude` under `deny_everything` (`claude_runner.py:957`, returns `behavior="deny"`, `reason_code="no_broker"`; "a runner without a broker never allows"). `_DenyRecorder.__call__` records then delegates to `deny_everything`, so it cannot accidentally allow. The measured fixture confirms the one mutating tool (Edit) was **brokered and DENIED** and `no_worker_file_write_observed: true` (dir-snapshot equality before/after each unit). Bounds are structural: `MAX_PROVIDER_CALLS=3` enforced by the CLI's own `--max-turns` (1+2), a per-unit wall timeout, the minimal `claude_child_env` allowlist, and assignments that reference **only** a `tempfile` dir — never a repository path. **Not worker-reachable:** `grep` for importers/callers of `routing_probe`/`probe_routing` returns only the module's own `main()` and its test file — no `cli.py`/`loop.py`/`start_gate.py` reference. It is an operator/producer CLI action (`python -m tools.agent_supervisor.routing_probe`), unreachable from inside a certified run.

### 4. Fixture / prompt hygiene — PASS

**Fixture + prompt PII-clean:** `grep` for `MLFLL`/`C:\Users`/`/Users/` over `fixtures/shell_routing_2026-08-29_m0t120_2_1_251.json` and `prompts/claude_native_tools.md` returns nothing. The fixture redacts all machine paths to `<tmp>` / `<home>` / `routing_probe_<id>` (`routing_probe._redact`); `cli_identity` is a sha256 digest (non-sensitive). No secrets/tokens.

**Prompt cannot be an injection channel:** `claude_native_tools.md` is a static, supervisor-owned package file, loaded at import (`claude_runner._load_native_tools_guidance`) and appended **to** the worker prompt inside `build_checkpoint_contract` — controller→worker direction, not worker→controller. It is not worker-writable, and its content is captured in the supervisor tree hash / the single M0-T119 recertification identity (so it cannot drift without changing the certified identity). Worker-text-clean preserved: the file explicitly states it carries no token quota/percentage/countdown (D-024-R045), and `assert_worker_text_clean` covers it (producer test `test_the_guidance_is_worker_text_clean`).

### 5. Owner-gate integrity — PASS

`process.py` (holding `HARD_DENY_ARGUMENTS` and `OWNER_ACTIVATION_ARGUMENTS`, with the "owner activation flags are a per-launch human act and are denied in any [synthesized argv]" hard-deny) is **not in the delta** — byte-untouched. No change to activation flags, approval surfaces, or R257 exclusions. The only new durable journal write key is `SHELL_ROUTING_EVIDENCE_KEY`, written solely by the harness path. Golden seeding is confined to harness setup: `golden_run` is imported only by its test module and is absent from every production dispatch file (verified by grep).

---

## Security opinion on the mode-scoping ruling

**I concur; the ruling is defensible.** The gate protects exactly the one *silent* path: `limited-auto` is the sole mode that forwards AUTO-tier prompts without a human (`loop.py` `forwards`/`unattended`). Shadow forwards nothing; supervised blocks on digest-bound human approval for every forward (and if an operator "walks away," a supervised run stalls — it does not proceed unattended). The tooth still **runs and reports** its verdict in every mode (it is a `FOLDED_PROBE`, present in the report payload), so a supervised operator additionally sees the routing verdict — only the hard *gating* effect is scoped. This is faithful to R295's exact words ("changed shell-routing behavior cannot silently enter a **certified** run") and it avoids editing three test harnesses outside allowed paths.

**One forward-looking caveat (SEC-INFO-3):** the safety of the scoping rests entirely on the invariant *"limited-auto is the only unattended, self-forwarding mode."* Today that invariant holds and is enforced by `loop.py`. If a future change ever adds another unattended-forwarding mode, this gate would silently fail to cover it. Recommend a regression guard asserting `{modes gated by the routing tooth} == {modes where loop.unattended/self-forward is true}`, so the scoping cannot become unsafe unnoticed.

## Security opinion on the two ASK-shapes

For **both** F1 and F2, ASK is **sufficient to prevent silent unattended execution**: an ASK-tier command is never AUTO-forwarded in `limited-auto` (only AUTO-tier self-forwards; ASK stops the run for the owner), so neither can execute in the certified loop without a human. The residual exposure is only a human explicitly approving a visible command in supervised mode. So neither is a gate blocker.

- **F1 (`… | sh`):** piping runtime-generated output into an interpreter is functionally equivalent to `iex`/concealed dynamic execution, which the classifier *does* HARD_DENY. **Recommendation (follow-up, not this unit):** consider promoting `| sh|bash|pwsh|python|node` to `HARD_DENY concealed_execution`.
- **F2 (`powershell -Command "Remove-Item -Recurse -Force …"`):** this is the more material of the two — it is a **wrapper-evasion of an existing HARD_DENY**: the bare forms `del /s` and `rm -rf` are HARD_DENY `recursive_or_wildcard_delete`, but the identical destructive verb wrapped in a quoted `-Command`/`-c` string drops to ASK because the segment program reads as `powershell`. **Recommendation (follow-up):** have the classifier look inside `powershell -Command "…"` / `pwsh -c` / `cmd /c "…"` / `bash -c "…"` argument strings for destructive-segment and concealed-execution markers. I tag F2 SEC-MINOR for that reason; ASK still gates it out of the unattended path, so it is not blocking.

---

## Findings

| ID | Severity | File:line | Finding | Disposition |
|----|----------|-----------|---------|-------------|
| SEC-1 | SEC-MINOR | `tools/test_agent_supervisor_command_authority.py` (F2 test, diff L163-168); classifier in `policy.py` (untouched) | `powershell -Command "Remove-Item -Recurse -Force …"` classifies ASK, evading the recursive-delete HARD_DENY that fires on bare `del /s`/`rm -rf`. Wrapper-evasion of an existing HARD_DENY. | Honestly recorded + test-locked per R293. Still gated (never AUTO; stops unattended run). **Recommend follow-up** defect-lane task to inspect wrapper argument strings. No change this unit. |
| SEC-2 | SEC-INFO | F1 test (diff L157-162) | `… | sh` classifies ASK, not HARD_DENY concealed_execution, despite being equivalent to `iex`. | Recorded + test-locked; gated. Recommend follow-up HARD_DENY for pipe-to-interpreter. |
| SEC-3 | SEC-INFO | `start_gate.py:228` | Mode-scoping safety depends on the invariant "limited-auto is the only unattended self-forwarding mode." | Add a regression guard binding gated-modes to unattended-forwarding-modes so scoping can't silently become unsafe. |
| SEC-4 | SEC-INFO | `cli.py:389` (`_check_prompts` expected set) | New `claude_native_tools.md` is not in the doctor prompt-existence set. | Harmless: `_load_native_tools_guidance` has a sentinel-bearing fallback and the content is covered by the recertified tree hash. Optional: add it to the expected set for completeness. |
| SEC-5 | SEC-INFO | `project-control/reports/M0-T120-routing-evidence.md:7,15` | Report embeds the owner's absolute path `C:\Users\MLFLL\.local\bin\claude.exe` (username). | Report-only; username already pervades the repo; the load-bearing shipped fixture is properly redacted. Not a new leak. |
| SEC-6 | SEC-INFO | live finding F-LIVE-1 (routing-evidence.md §1) | 2.1.251 reports `permissionMode=default` despite `--permission-mode manual`; read-only tools auto-allowed (never reach broker); **mutating tools still brokered+denied, no write** (verified in fixture). | Provider-CLI behavior, out of R293/this-unit scope, honestly flagged. Recommend tracking as its own item; write-protection is intact. |

## Regression / suite state

Independently ran the security-relevant deterministic tests at `7d8195b`: **204 passed** (104 WindowsShape+bounded-mode gate-fold; 23 drift-tooth removal-sensitivity; 77 routing_probe+golden_run incl. tooth-bites). Consistent with the recorded full-suite state 2782 collected / 2780 passed / 2 skipped / 0 failed. Classifier/policy/broker/process/cli confirmed outside the delta (untouched).

**G5 VERDICT: PASS**

Relevant files (absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\routing_probe.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\recovery_probes.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\start_gate.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\claude_runner.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\golden_run.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\prompts\claude_native_tools.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\shell_routing_2026-08-29_m0t120_2_1_251.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\probe_result.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_command_authority.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T120-routing-evidence.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M0-T120.json`
