<!-- Saved VERBATIM by the orchestrator from the G5 security-reviewer agent-return channel
     (delta re-attestation; transport entity-decoding only). Corrected identity d6a2ac8,
     control head 0a647cd. -->

All delta checks pass. Here is my delta re-attestation report.

---

# G5 DELTA Re-Attestation — M0-T117

**Reviewed delta identity:** `d6a2ac8` (control head `0a647cd`); production code identical `d6a2ac8..HEAD` (verified empty diff over `tools/`). Delta vs originally-reviewed `fa16560` spans preflight.py, turnover_adapters.py, the env test module (+4 tests), README/runbook, and reports.

**Read-only commands run:** `git diff --stat fa16560 d6a2ac8`; `git diff d6a2ac8 HEAD -- tools/`; `git diff fa16560 d6a2ac8 --` on the two prod files, the test module, README + runbook; `Read` of `capability_probe.py:88-114` and `native_runtime.py`; `python -c` on the packet JSON (allowed_paths/status); `python tools/modularity_check.py --check`; targeted grep for env-mutation/DISABLE_UPDATES/logging in the delta.

## Delta findings (against the four requested points)

**(1) Two new env routings — no new security surface. CONFIRMED.**
`preflight.control_response_round_trip` now builds the live-probe env via `claude_child_env()` (preflight.py:136) and the turnover successor via `claude_child_env({SUPERVISOR_SUCCESSOR_EFFORT, SUPERVISOR_SESSION_ROLE})` (turnover_adapters.py:397). Both delegate to the already-reviewed helper: `minimal_env` builds the base, the extras merge, the forced pair applies last. The effort/role extras pass through unchanged and cannot be clobbered (the forced pair contains only `DISABLE_AUTOUPDATER`) — `test_worker_successor_env_injects_and_preserves_existing_pairs` asserts `effort="xhigh"`, `role="worker"` survive alongside `DISABLE_AUTOUPDATER="1"`, and the orchestrator-layer test covers the other branch. No value logging is introduced (grep of the delta additions for `print(`/`log`/`env[` is empty). The added `test_g4f6_allowlist_reenable_vector_is_overridden` further closes the "widen the allowlist so the parent re-enables it" vector — a genuine hardening.

**(2) No owner-boundary regression. CONFIRMED.**
The production delta is limited to an import swap + an `env=` swap + comments in the two files; grep of the delta for `SetEnvironmentVariable|setx|DISABLE_UPDATES|env mutation` returns nothing applied. `DISABLE_UPDATES` remains documentary-only ("deliberately NOT used", R280). No agent-executed environment mutation anywhere.

**(3) Corrected docs honestly bound the guarantee — non-bypass. CONFIRMED.**
README and runbook now rename the guarantee from "controller-launched workers" to "every claude child the supervisor launches with a CONSTRUCTED environment," enumerate the exact four forced launches (worker, model-availability probe, `doctor --live` control-response probe, turnover successor both layers), and explicitly name the two seams that are NOT forced — `capability_probe.py::_run` (line 99, no `env=`) and `native_runtime.py::_run` (line 104, `env=None`), which I independently confirmed inherit the full parent environment as bare `--version`/`--help` probes — with the correct rationale (they need the real PATH; owner machine-scope belt covers them). The docs also add the accurate G3-Finding-4 insight that `minimal_env`'s allowlist strips `DISABLE_AUTOUPDATER` (not on `DEFAULT_ENV_ALLOWLIST`, verified by the AS-1 assertion), so the code-side injection is necessary and complementary to the machine-scope belt. This is an honest, precisely-bounded description with no bypass narrative.

**(4) SEC-MINOR-1 disposition — ACCEPTABLE / RESOLVED.**
The two in-supervisor seams I flagged are now code-fixed through `claude_child_env`, and `allowed_paths` was correctly expanded to include `preflight.py` and `turnover_adapters.py` (edits are in-scope). The two remaining bare probes are genuinely a different class (full parent inheritance in a shared multi-provider runner, outside this packet, owner-belt-covered) and are honestly documented rather than silently omitted; routing them through `claude_child_env` would strip the PATH a `--version` check needs. The residual (a near-instant `claude --version`/`--help` running without the code-side control when the owner has not set the machine-scope belt) is negligible and drift-tooth-caught, and is now an explicitly documented exclusion — an acceptable non-blocking residual. SEC-MINOR-1 is closed.

**Carried notes:** SEC-INFO-1 (mutable module-level `FORCED_CLAUDE_CHILD_ENV`) and SEC-INFO-2 (silent forced-pair override not audit-logged) remain untouched and non-blocking, exactly as my original report allowed.

**Modularity / regressions:** `python tools/modularity_check.py --check` → `failures 0` at the corrected state (preflight/turnover edits are 1-line swaps, no threshold movement). The three pre-existing `2.1.251`-vs-`2.1.248` live drift teeth remain out of scope (M0-T118).

---

**G5 DELTA VERDICT: PASS at d6a2ac8** — the correction routes both flagged in-supervisor Claude launch seams through `claude_child_env` with the effort/role extras preserved and no new logging or owner-boundary surface, and the docs now honestly and precisely bound the covered set versus the two deliberately owner-belt-covered bare probes; SEC-MINOR-1 is resolved and no new defect is introduced.
