# G5 Security Delta Re-Attestation — M0-T149 (v2)

**Reviewed identity:** frozen candidate **45b0572c** on `task/M0-T149-command-profile`, merged at 7804bc03. Verified **content-identical** to current HEAD (7804bc03) and working tree for `policy.py`, `evidence.py`, and both test files (`git diff 45b0572c HEAD` and working-tree diffs empty). Diff basis vs my FAIL identity ed04c4bb: `git diff ed04c4bb 45b0572c` — changes confined to `policy.py` + the two test files + two report files. **`evidence.py` is unchanged**, so my v1 PASS verifications for enforcement-point integrity, fail-visible/no-info-leak, and POLICY_VERSION 1.1.0 strict-digest direction carry over unmodified.

**Commands rerun (independent):** `pytest` both documented files → **247 passed, 1 skipped** (v1: 236; +11 tests, matching orchestrator's 122+125+1s); `ruff check` 4 files → **All checks passed!**; `modularity_check --check` → **selected 357 files; failures 0** (13 warnings incl. the acknowledged `policy.py` symbol_ceiling advisory).

**MED-1 — CLOSED.** `_MUTATING_CHECKER_TOKENS` is now `{--fix, --fix-only, --unsafe-fixes, --add-noqa, --output-file, -o, format, clean}`. Traced: `ruff check --add-noqa .` and `python -m ruff check --add-noqa tools` → `mutating_checker_token:--add-noqa` (refused before execution); `--output-file`/`-o` and `ruff clean` likewise refused. Rationale comment rewritten to be accurate; a closure test (`test_the_mutating_checker_token_set_covers_every_known_writer`) machine-asserts each token is in the set AND refused, so the claim cannot silently drift. Enforcement-point spy proof (`..._never_executed`) confirms the runner is never invoked.

**MED-2 — CLOSED (root cause fixed).** `_refuse_interpreter_target` no longer skips unknown dash tokens. Traced all branches: `-c` and fused `-c<code>` → `inline_python_code`; space `-m <mod>` and fused `-m<mod>` both route through the shared `_refuse_python_module` → the same `SUPERVISOR_EXECUTABLE_PYTHON_MODULES` allowlist, so `-mpip`/`-mcompileall`/`-mpydoc`/`-mwebbrowser` → `python_module_not_allowlisted:<module>` (my network/mutation vectors closed by the allowlist, not by URL parsing); every other dash token → `unrecognized_interpreter_flag:<token>`. The fused allowlisted form (`-mpytest`, `-munittest`, `-mruff …`) still admits, and a ruff module still passes its args through the checker-token gate. Spy proof confirms `python -mcompileall foo.py` is refused and never executed.

**Wording finding — CLOSED.** The M0-T148 annotation no longer claims absolute "never-mutating"; it now states never-git is machine-enforced, enumerated mutating shapes are excluded by layered fail-closed checks, and the profile is "defense-in-depth over a closed enumerated surface, not an absolute never-mutating guarantee." Accurate.

**LOW-1 — addressed** (`ruff clean` now refused; `pytest --cache-clear` remains admitted per my advisory rating). **LOW-3 — closed** (producer report modularity claim corrected to 13 warnings with cohesion justification; a Rework section documents the token-set supersession accurately). **LOW-2** (basename-not-identity argv[0]) unchanged — declared, acceptable residual.

**New-bypass probe:** v2's `_refuse_interpreter_target` is strictly more restrictive than v1 (fail-closes on every dash token; adds no admit path), so the refactor introduces no new bypass. The only behavior change is additional fail-closed refusals: option-with-argument interpreter forms (`py -3 -m pytest`, `python -W ignore -m pytest`) are now refused with `unrecognized_interpreter_flag` — a usability cost that is fail-closed, fail-visible, explicitly documented (G3-F5), and unused by any documented command. Not a finding.

Both blocking MED findings from my FAIL are remediated with reproducible red/green and enforcement-point (never-executed) proofs; no new bypass; core guard, enforcement point, fail-visibility, and strict-version direction all remain sound at 45b0572c.

VERDICT: PASS

---

*Orchestrator preservation note: saved VERBATIM from the security-reviewer agent-return channel (2026-09-07 delta re-attestation; HTML entities decoded, content unaltered). Supersedes the v1 FAIL (M0-T149-G5-security.md) for gate purposes at the v2 identity.*
