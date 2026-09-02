# M0-T138 G3 independent code review (verbatim reviewer return)

Reviewer: `code-reviewer` (independent read-only agent; not the producer). Returned via the
agent-return channel and saved verbatim by the orchestrator (transport entity-decoding only).
An orchestrator addendum discharging the reviewer's one execution request follows the verbatim
return, clearly labeled.

---

## G3 CODE REVIEW — M0-T138 (D-024 Amendment 41: controller-update source binding)

**VERDICT: PASS** (with one execution caveat requiring orchestrator reconfirmation; no blocking defects)

### Identity verified (measured, not trusted)
- HEAD = `99cd3dad…`, branch `candidate/D-024-mrl-option-b`, tree clean (`git status --porcelain` empty).
- `435531de..99cd3dad` = project-control evidence/status only (no code/test/doc changes). `435531de` (impl) vs parent `ec4ac9a3` touches ONLY `docs/CONTROLLER_UPDATE_RUNBOOK.md`, `docs/SESSION_HANDOFF.md`, `tools/controller_update/**`. `tools/agent_supervisor/**` and `.github/workflows` untouched (R616; no frozen-identity recert triggered).
- Frozen commit `1489879e` is type=commit, tree `0babc469…`, subtree `tools/agent_supervisor`=`79af11a2…`. Binding `source_binding.json` pins all three exactly. `config.toml` confirmed ABSENT from the frozen subtree (`git cat-file -e` fatal); only `config.example.toml` present.

### Findings
1. **Source resolution — full-SHA-only (non-blocking, PASS).** Active copy path resolves only `$binding.commit_sha`, gated by `^[0-9a-f]{40}$` (line 155); `worktree add --detach <sha>` (line 300). No origin/main/HEAD/branch/short-SHA resolution anywhere. `rev-parse HEAD`/`symbolic-ref -q HEAD` in `Assert-SourceWorktreeState` (233,238) are post-add worktree-state CHECKS (must be detached, HEAD==pinned, clean) — safe.
2. **Pre-copy gates fail-closed (PASS).** repo toplevel, normalized origin, commit exists+is-commit, commit tree, subtree tree, each required module, and detached-clean worktree each emit a typed `REFUSED <code>` and `exit 1` via `Exit-Refusal`; `Invoke-Native` fail-closes on null exit code (`native_no_exit_code`). `ErrorActionPreference=Continue`, temp-file capture, no piping — PS 5.1 safe. robocopy failure judged at `code >= 8` (correct).
3. **Post-copy proof (PASS).** `Compare-InstalledTree` is complete + bidirectional (missing/unexpected/changed) on RAW SHA-256 (`Get-FileHash`). LF-normalization is confined to the manifest cross-check via `Get-LfNormalizedSha256` (Latin-1 byte-exact round-trip + CRLF→LF), faithfully mirroring `manifest._hash_file` (`read_bytes().replace(b"\r\n",b"\n")` + lowercase `sha256_hex`).
4. **verify-manifest cannot certify a wrong source (PASS).** Cross-check uses the script's OWN canonical `$CoveredPatterns` over the ACCEPTED SOURCE as source-of-truth (defeats manifest self-narrowing), requires bidirectional key-set equality (manifest keys minus `config.toml`) == source covered set, and every covered digest == accepted-source LF digest. The `config.toml` carve-out is correct: it is an EXTERNAL logical binding (`CONFIG_LOGICAL_NAME`), never in the package tree — `manifest.py::verify_manifest_with_config` itself refuses `config_duplicated_in_package`, and `Compare-InstalledTree` would flag any package-tree `config.toml` as unexpected. Independently cross-checked the regex↔fnmatch projection on 17 edge-case paths (case-insensitivity, `*` crossing `/`, anchoring): **NONE diverge**. `EXCLUDED_NAMES`/`EXCLUDED_DIR_PARTS` match manifest.py exactly; `__pycache__` exclusion prevents false mismatch after §5 python runs.
5. **Tests real + mutants fail-closed (PASS).** Real 3-commit git fixtures (incl. self-consistent wrong commit C with B's subtree), fresh `powershell.exe -File` per case, raw `$LASTEXITCODE`, independent python-hashlib/fnmatch manifest crafter. Covers positive install+verify + six typed rejections (not_a_full_sha, tree_mismatch, subtree_mismatch, missing_module, source_worktree_exists, content_mismatch, manifest_digest/key_set_mismatch). Mutant generator asserts each pattern matches exactly once (fail-closed) and pairs each of 4 mutants with a real-script control. All mutations confined to `$env:TEMP` GUID dirs.
6. **Runbook coherent (PASS).** §4 = exactly ONE `-Phase install` fenced block + ONE recovery (`worktree remove --force`) block, concrete pinned SHA, no `<placeholder>`; §5a = one `-Phase verify-manifest`; §3 timestamped backup precedes §4; §10 rollback removes both `controller_manifest.json` and the new `controller_update_evidence.json`. No `origin/main` anywhere in the runbook (grep empty). Handoff seq-73 states the single owner chain (review→owner update s3–s8→canary) with Tranche C not authorized.

**Non-blocking:** (a) origin-URL compare lowercases the whole URL (path case-insensitive) — acceptable, since commit/tree/subtree SHAs are the real gate. (b) The `config.toml` carve-out branch is defensively correct but not positively exercised (fixture manifests carry no external config key).

### Test execution
- Required `run_ps_tests.ps1`: **could not self-execute** — the read-only guard blocks every `powershell.exe` process (the suite writes %TEMP% fixtures), and I must not disable my sandbox. Per `.claude/rules/project-control.md` (evidence-capture division of labor) I verified the orchestrator/`gate_runner.py`-captured record `project-control/reports/M0-T138-gates/m0t138-ps-tests-controller-update.json`: exact argv/cwd, `returncode=0`, `stderr_bytes=0`, `stdout_bytes=3589`, at `repo_head=435531de` — code-identical to HEAD (435531de..HEAD is project-control-only). **Request: orchestrator re-run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\controller_update\ps_tests\run_ps_tests.ps1` and confirm raw exit 0 at HEAD.**
- Independent check I DID run (read-only python, no writes): fnmatch↔regex projection equivalence — 0 divergences on 17 sample paths.

**Conclusion:** The source binding is correct, fail-closed, PS 5.1-compatible, faithful to `manifest.py` and to D-024-R607..R614; no blocking defects — PASS, pending orchestrator reconfirmation of the ps-suite raw exit code at HEAD.

Relevant paths: `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\update_controller_from_candidate.ps1`, `…\source_binding.json`, `…\ps_tests\{fixtures,run_ps_tests,test_source_binding,test_mutants_detected,test_runbook_parse}.ps1`, `…\docs\CONTROLLER_UPDATE_RUNBOOK.md`, `…\docs\SESSION_HANDOFF.md`, frozen `1489879e:tools/agent_supervisor/manifest.py`, captured evidence `…\project-control\reports\M0-T138-gates\m0t138-ps-tests-controller-update.json`.

---

## Orchestrator addendum (evidence-capture division of labor; NOT part of the verbatim return)

The reviewer's single execution request is DISCHARGED: the orchestrating verifier session ran
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\controller_update\ps_tests\run_ps_tests.ps1`
at HEAD `99cd3dad` (implementation trees byte-identical to `435531de`) with RAW EXIT 0 —
all three test files passed: positive control + `not_a_full_sha` / `tree_mismatch` /
`subtree_mismatch` / `missing_module` / `source_worktree_exists` / `content_mismatch` /
`manifest_digest_mismatch` / `manifest_key_set_mismatch` typed refusals, 4/4 mutants DETECTED,
13/13 runbook blocks parse-clean, no `origin/main`. The independent G4 qa-engineer reviewer also
executed the same suite at the reviewed content with raw exit 0 (see `M0-T138-G4-qa-review.md`).
The PASS verdict's pending condition is therefore satisfied at the reviewed SHA.
