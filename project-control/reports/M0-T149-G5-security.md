# G5 Independent Security Review — M0-T149

**Task:** M0-T149 — Constrain supervisor-executed documented test commands to a non-mutating program profile (G3 LOW-1 follow-up to M0-T148)
**Gate:** G5 (security), independent, read-only. Producer: `supervised-loop-fable-worker`. Reviewer ≠ producer.
**Reviewed identity:** candidate commit **ed04c4bb** (`git show ed04c4bb`), integrated at f1e6de26; verified **content-identical** to current HEAD 7248aed5 and to the working tree for `tools/agent_supervisor/policy.py`, `tools/agent_supervisor/evidence.py`, and both test files (`git diff ed04c4bb 7248aed5 -- <files>` empty; working-tree diff empty). All findings and reproductions below are against ed04c4bb content.
**Directive regime:** in-regime, `directive_refs` D-032:ALL. Supervisor-freeze lane: qualifying evidence AD-093 (demonstrated security risk, M0-T148 G3 LOW-1) cited in both packet and commit — satisfied. Supervisor remains SHADOW-ONLY (R595 not activated), so all findings are latent, not live.

## Commands run (read-only sandbox; test execution allowed)

| Command | Result |
|---|---|
| `python -m pytest tools/test_agent_supervisor_policy.py tools/test_agent_supervisor_reviewer.py -q` | **236 passed, 1 skipped** (80s) — matches producer's 113+1s / 123 |
| `python -m ruff check <4 edited files>` | **All checks passed!** |
| `python tools/modularity_check.py --check` | **selected 357 files; failures 0; warnings 13; exit 0** (producer reported 12 — see LOW-3) |
| Classifier bypass probe (`python -c` / stdin) | **Blocked by the read-only guard** — correct reviewer discipline; only test runners execute. Hypotheses instead confirmed by deterministic source-tracing of `supervisor_execution_refusal` + `_refuse_interpreter_target` + `assert_argv_safe`. |

I did **not** run the full supervisor suite (>=1165 tests / freeze re-baseline) — that is the orchestrator's separately-captured step, and the R247 recertification + source_binding re-pin noted in the producer report.

## Assessment against the requested surface

**1. Bypass hunting (`supervisor_execution_refusal`).** Order is correct and fail-closed: shape validity → `_is_destructive_segment` (fires **before** the allowlist, confirmed) → closed program allowlist `{python, python3, py, pytest, ruff}` via basename/`.exe`-normalized `_program_name` → interpreter target checks / mutating-checker tokens. The common LOW-1 shapes are genuinely closed (traced): `git push origin b` and `git status` → `program_not_allowlisted:git`; `GIT.EXE`/case/backslash normalized; `rm -rf tools` → `destructive_segment:recursive_or_wildcard_delete`; `python -m pip install`, `python -m venv`, `python -c`, absolute/`..` script paths, bare interpreters, `uv run`, `python3.12` (fail-closed) → all refused. **"never-git" is truly machine-enforced.** However two undeclared shapes pass (MED-1, MED-2 below), and `assert_argv_safe` (which runs after the refusal check) does **not** catch them — it only blocks bypass/effort/activation flags — so they reach `self._run` = execution.

**2. Enforcement-point integrity (`evidence.run_command`, lines 488–511).** VERIFIED. Refusal returns `_failure(command, "non_mutating_profile_refused", ...)` positioned after the single-clean-segment precheck and **before** `assert_argv_safe` and the sole `self._run` call. No timeout/exception/retry path executes a refused command; the refusal is a `CollectionResult(ok=False)`, not a warning, and cannot be downgraded.

**3. Fail-visible refusal / info leak.** VERIFIED no leak. Refusal renders as an `ok:false` `command_transcripts` entry carrying only `name`=the command string (already visible), `error_category="non_mutating_profile_refused"`, and `detail` = the reason code (tokens drawn from that same command). `minimal_env` values are never logged. No environment/secret/path exposure beyond the command string.

**4. Declared residuals.** Honest and acceptable: repo-content trust for admitted `python tools/x.py`; worker-AUTO / `_auto_test_command` untouched (supervisor-freeze S1 respected); future non-python runners refused fail-visibly; `format`-anywhere fail-closed cost. **But** two undeclared gaps (MED-1/MED-2) are NOT stated, and the corrected M0-T148 wording "never-git/**never-mutating** is machine-enforced" overclaims given those gaps.

**5. POLICY_VERSION 1.0.0 → 1.1.0 strict direction.** VERIFIED. `POLICY_VERSION` is bound into `ApprovalRequest.binding()['policy_version']` → request digest. `verify_before_execute` recomputes `request.refreshed().digest()` from the **live** request (whose `policy_version` defaults to the current module constant) and DENYs on any mismatch with the stored digest (`digest_changed_before_execution`, HARD_DENY). An approval granted under 1.0.0 cannot be consumed under 1.1.0 — re-verified, never grandfathered. (Pre-existing S13.5 mechanism; the bump correctly leverages it; no test pins the literal.)

**Product-plane checklist (cross-tenant isolation, service-role secrecy, private storage, upload controls, prompt-injection, log redaction):** N/A to this diff — the change is confined to the supervisor's documented-command execution classifier and touches no tenant data, storage, DB, or product I/O. Least privilege is *improved* (default-deny allowlist, `minimal_env`, cwd=worktree). The one product-adjacent angle (SSRF/network) surfaces via MED-2.

## Findings

**MED-1 — `_MUTATING_CHECKER_TOKENS` is incomplete; a source-mutating ruff command passes the "non-mutating" profile. [BLOCKING]**
Repro (traced): `ruff check --add-noqa .` (also `python -m ruff check --add-noqa .`) → `supervisor_execution_refusal` returns `""` (admit); `assert_argv_safe` passes → executed. `ruff --add-noqa` rewrites tracked source files in place to insert `# noqa` directives — a mutation. The producer names the frozen set "the tokens that turn the admitted checkers into writers (`ruff check --fix`, `ruff format`)"; `--add-noqa` is exactly such a token and is absent. Not caught by tests (grep: no `add-noqa` case). Behind the packet-authorship boundary and shadow-only (hence MED not HIGH), but it directly falsifies the deliverable's named property.
Remediation: add `--add-noqa` (and audit for any other ruff in-place writer) to `_MUTATING_CHECKER_TOKENS`; safer still, invert to a positive allowlist of read-only ruff args. Add a negative test.

**MED-2 — Fused `-m<module>` form bypasses `SUPERVISOR_EXECUTABLE_PYTHON_MODULES` entirely (mutating and network-touching commands pass). [BLOCKING]**
`_refuse_interpreter_target` only recognizes an **exact** `-m` token. A fused token (`-mcompileall`, `-mpydoc`, `-mwebbrowser`, `-mpip`) starts with `-`, is skipped as an unknown flag, and the first `.py` positional then returns `""` (admit). Repros (traced; the space forms are correctly refused, only the fused forms escape):
- `python -mcompileall foo.py` → admit → writes `__pycache__/*.pyc` (mutation). *(vs. `python -m compileall foo.py` → correctly `python_module_not_allowlisted:compileall`.)*
- `python -mpydoc -w tools/foo.py` → admit → writes an `.html` file (mutation).
- `python -mwebbrowser http://host/x.py` → admit → opens/fetches an arbitrary attacker-shaped URL (network egress / SSRF-adjacent). The trailing `.py` requirement is satisfiable inside the URL and defeats the `_ABSOLUTE_PATH_SHAPE`/`..` checks.

This defeats the module allowlist whose stated purpose is precisely "an open `-m` would readmit `python -m pip install`." Not caught by tests (grep: no fused-`-m` case). MED (packet-authorship boundary, shadow-only), but it falsifies the module-allowlist guarantee.
Remediation: in `_refuse_interpreter_target`, treat any token matching `^-m.` as a combined `-m<module>` and route the embedded module through the same allowlist / ruff-token checks (or refuse any interpreter switch token that is not a known-safe form). Add negative tests for the fused form.

**LOW-1 — Cache-mutating checker args admitted (non-blocking).** `ruff clean` and `pytest --cache-clear` are admitted (pytest args, and non-`--fix` ruff args, are not inspected) and delete the tool's own gitignored cache. Ephemeral, low materiality; note only.

**LOW-2 — Allowlist authenticates argv[0] by basename, not identity (non-blocking).** `_program_name` matches on basename, so a path to a rogue executable named `python`/`pytest`/`ruff` (e.g. `/tmp/evil/python -m pytest x.py`) is admitted. This is the declared content-trust residual extended to argv[0]; acceptable under the stated trust model but worth explicit mention (name-based, not identity-based, authentication).

**LOW-3 — Producer self-check accuracy (non-blocking).** At the reviewed HEAD, `modularity_check --check` reports **warnings 13** (including a new `symbol_ceiling: tools/agent_supervisor/policy.py`), not the "warnings 12 — identical warning set to the pre-edit baseline" claimed in the producer report. failures 0 either way, so the gate outcome is unaffected; the new symbol_ceiling signal reflects policy.py's +7 top-level symbols (a cohesive addition, not a failure). The "identical/12" wording is inaccurate.

**Observation (not a finding):** `python3.12`, `pyw`, `uv run`, `node`, `npm`, `powershell`, etc. are refused fail-closed — correct direction; extending the allowlist is a reviewed one-line diff as designed.

## Verdict rationale

The core guard is sound and a large net improvement (from "any documented command including `rm -rf`/`git push` executes" to a default-deny allowlist with layered fail-closed checks), and enforcement-point integrity, fail-visibility/no-leak, and the POLICY_VERSION strict direction all verify PASS. However, the deliverable's central, explicitly-claimed security property — a "non-mutating supervisor-execution profile" that "excludes every destructive or mutating shape" and (task objective) network-touching commands, restated in the corrected M0-T148 report as "never-mutating is machine-enforced" — is **falsified by two reproducible, undeclared commands** (`ruff check --add-noqa`; the fused `-m<module>` form → compileall/pydoc mutations and webbrowser network). A security gate must not certify a security property that is demonstrably false. The fix is small and belongs in this same task (extend `_MUTATING_CHECKER_TOKENS`; handle fused `-m<module>`; correct the "never-mutating" wording), so this is a bounded rework, not a redesign. Because the surface is packet-authorship-gated and the supervisor is shadow-only, the two defects are MED (not HIGH), but they are BLOCKING for acceptance.

Suggested disposition: FAIL → bounded rework (MED-1, MED-2, plus reword the M0-T148 correction to "never-git + no *enumerated* mutating shape") → re-gate G5. LOW-1/-2/-3 are advisory.

VERDICT: FAIL

---

*Orchestrator preservation note: saved VERBATIM from the security-reviewer agent-return channel (2026-09-07 gate wave; transport framing removed, HTML entities decoded, content unaltered).*
