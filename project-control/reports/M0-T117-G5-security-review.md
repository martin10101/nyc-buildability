<!-- Saved VERBATIM by the orchestrator from the G5 security-reviewer agent-return channel
     (transport entity-decoding only; the reviewer sandbox returns report content instead of
     writing files, per the evidence-capture division of labor). Review head 0324342, material
     identity fa16560. -->

I have completed my independent verification. All evidence is gathered. Here is my G5 report.

---

# G5 Security Review Report — M0-T117

**Task:** M0-T117 — D-024 Amendment 13 unit Q: forced `DISABLE_AUTOUPDATER=1` on controller-launched Claude children + admission-event discipline docs
**Reviewer role:** security-reviewer (G5), read-only
**Checkout:** `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` (branch `control/D-024-fable-codex-loop`)
**Reviewed identity:** frozen control head `0324342` / material-identity commit `fa16560` (8 files, +598/-3)
**Identity check:** `git diff --stat fa16560 HEAD` shows only control-plane files (gates/reports/state/task) changed after `fa16560`; `git diff fa16560 HEAD -- tools/agent_supervisor/process.py tools/agent_supervisor/claude_runner.py` is **empty** — the reviewed production code at HEAD is byte-identical to the material identity. Verification is valid.

## Read-only commands run
- `git -C … show --stat fa16560` and `git -C … show fa16560` (full diff)
- `git -C … diff --stat fa16560 HEAD` / `git -C … diff fa16560 HEAD -- <prod files>` (identity confirmation)
- `Grep` for `minimal_env|claude_child_env|FORCED_CLAUDE_CHILD_ENV|DISABLE_AUTOUPDATER|DISABLE_UPDATES` under `tools/agent_supervisor`
- `Grep` for `SetEnvironmentVariable|setx|reg add|winreg|RegSetValue` under `tools/`
- `Grep` for `DISABLE_UPDATES` repo-wide, and secret-like tokens (`sk-|token|secret|api_key|bearer|password|ANTHROPIC`) in both T117 reports
- `Read` of `process.py` (150–269), both `claude_runner.py` call sites (1090–1119, 1535–1559), `preflight.py`, `evidence.py`, `operator_ask.py`, `turnover_adapters.py`, `cli.py` (1305–1329), the task packet, and `source-013-amendment.md`
- `python tools/modularity_check.py --check` → `failures 0; warnings 9`, EXIT=0
- `wc -l` on the three modified/added Python files

## Findings by review dimension

**1. Environment-surface integrity — CLEAN.** `minimal_env` (process.py:200-210) is untouched: only allowlisted names inherited, `extra` merged on top, values never logged (docstring reaffirmed). `claude_child_env` (process.py:224-247) delegates to `minimal_env` then applies the forced pair last into the freshly-built dict — no aliasing, no allowlist bypass, no value logging. `FORCED_CLAUDE_CHILD_ENV` is a hardcoded literal `{"DISABLE_AUTOUPDATER": "1"}` (process.py:221); grep confirms no code reads it from config or mutates it. See SEC-INFO-1 on its mutability.

**2. Fail-closed semantics — SOUND.** AS-6 forced-pair-wins (process.py:245-246) is the correct posture for a *presence* invariant: `env.update(FORCED_CLAUDE_CHILD_ENV)` guarantees the child always carries the disable regardless of any parent-env/allowlist/config input, with no error path that could regress to fail-open. A typed refusal would be strictly weaker. The config `extra_env` is digest-bound by the manifest, so a tampered `DISABLE_AUTOUPDATER=0` is both caught upstream and neutralized here — the override is not a real masking concern. Residual observability note in SEC-INFO-2.

**3. Scope containment — CLEAN.** Full-diff read confirms the two modified production modules carry no collateral behavior change: `process.py` only adds the constant + helper (`minimal_env` unchanged); `claude_runner.py` is limited to the import swap (line 64) and the two call-site swaps (1103 worker, 1549 probe), each annotated. Codex children are untouched — `codex_channel.py:404` still uses `minimal_env`, and `operator_ask.py`/`codex_reviewer.py` use the codex `build_argv`. See SEC-MINOR-1 for two *other* Claude launch sites outside this packet's file scope.

**4. Owner-boundary compliance — CLEAN.** No code or test performs a Windows environment mutation. Grep for `SetEnvironmentVariable|setx|reg add|winreg` across `tools/` returns only a **pre-existing** guard test (`tools/test_readonly_agent_guard_powershell.py:139`, not in this commit and not in `allowed_paths`). The PowerShell command pack exists only as recorded text, labeled owner-executed, in `docs/CONTROLLER_UPDATE_RUNBOOK.md:61-70` and `project-control/reports/M0-T117-autoupdater-evidence.md:249-258` (R288). `DISABLE_UPDATES` appears **nowhere as an applied control** — only as documentary "deliberately NOT used" text (process.py:217, README.md:399, runbook:230) (R280).

**5. Secrets / logging hygiene — CLEAN.** The new code logs no env values. Secret-token scan of both reports returns only the word "tokens" inside the phrase "no tokens." Nothing in the diff touches the command broker, digest binding, isolation, or approval surfaces — it adds exactly one forced key to Claude children.

**6. Docs accuracy as a security control — CLEAN.** README §"Claude Code version admission events" (394-430) and runbook §13 (30-75) describe the correct ordering — upgrade → recapture → recertify → **only then** repin — and explicitly forbid repin-first, silent drift, and `DISABLE_UPDATES`. No bypass narrative.

## Tagged findings

**SEC-MINOR-1 — Per-child injection does not cover two other controller-launched Claude children (completeness vs R278/R286).**
Owner R278 scopes the control to "the controller-launched Claude **processes** and the certification window." The forced injection covers the worker launch (`claude_runner.py:1103`) and the model-availability probe (`claude_runner.py:1549`), but two additional controller-launched **Claude** children still build their env with plain `minimal_env` and therefore lack `DISABLE_AUTOUPDATER=1`:
- the `doctor --live` / preflight control-response live probe — `cli.py:1314` resolves the canonical Claude executable and calls `control_response_round_trip(executable, live=True)` (`cli.py:1319`), which launches it with `minimal_env()` at `preflight.py:136`;
- the turnover successor launch — `turnover_adapters.py:397` builds the WORKER/ORCHESTRATOR successor env (confirmed Claude worker argv, docstring 304-306) with `minimal_env({...})`.
Both files are **outside M0-T117's `allowed_paths`**, so this is a packet-scoping gap, not a producer error, and the acute certification-window risk is covered when the owner sets the optional R288 machine-scope variable. Remediation: a follow-up task to route these two Claude-child launches through `claude_child_env` (or document the exclusion and make the R288 machine-scope var non-optional for the certification window). **Does not block M0-T117** — the task delivered exactly its scoped seams and the README/runbook language matches that scope.

**SEC-INFO-1 — `FORCED_CLAUDE_CHILD_ENV` is a mutable module-level dict.** No data- or config-driven mutation path exists (hardcoded literal, never read from config, no writers in grep); extending it would require arbitrary code execution in the supervisor process — a strictly larger compromise than env injection. Optional hardening: expose it as an immutable mapping (e.g. `MappingProxyType`) so even in-process code cannot extend it. Not a reachable risk.

**SEC-INFO-2 — Silent override of a conflicting `extra_env` is not observable.** `claude_child_env` neutralizes a conflicting `DISABLE_AUTOUPDATER` with no log/audit event. Not a security concern (config is digest-bound; the forced pair wins regardless), but an optional audit note on override (key name only, never the value) would improve tamper visibility.

## Pre-existing drift teeth (not this task's defect)
Three live drift-tooth tests fail at installed `2.1.251` vs fixture `2.1.248` (`capability_probe`, `event_bus`, `native_adapter`) — pre-existing, M0-T118 fixture-recapture scope, untouched by this change. Confirmed as documented. No other unexpected failures.

## Modularity
`python tools/modularity_check.py --check` → `failures 0; warnings 9`, EXIT=0. `process.py` (813 lines) is a warning-level `review_signal` file; the 37-line addition is cohesive (child-environment construction, the same responsibility as the adjacent `minimal_env`), not a dumping-ground. `claude_runner.py` change is a net +5-line swap that moved shared logic into `process.py` rather than duplicating it — extraction-before-growth satisfied.

---

**G5 VERDICT: PASS** — The change is a tightly scoped, correctly fail-closed Claude-child environment control with no secrets/logging/isolation weakening, correct owner-boundary compliance (no agent-executed environment mutation; `DISABLE_UPDATES` never applied), and accurate non-bypass docs; the single SEC-MINOR is an out-of-packet scope-completeness gap (two other Claude launch sites) that is mitigated by the R288 machine-scope control and warrants a follow-up task, not a block.
