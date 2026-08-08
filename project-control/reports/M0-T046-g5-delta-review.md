# G5 DELTA RE-REVIEW — M0-T046 @ `a27068d`

**Reviewer:** security-reviewer (independent, read-only). **Delta:** `git diff 569d1a7..a27068d` (6 files).
**Head confirmed:** `a27068db17ff20426a587fd04ed00eea827c909d` on `task/M0-T046-preactivation` ✓.
**Scope-1 (loop.py/cli.py):** untouched (`git diff --name-only` empty) ✓ — C2 disposition preserved.
**Reproduced in-sandbox:** `python -m pytest tools/test_agent_supervisor_os_acl.py tools/test_agent_supervisor_audit_fork_lock.py -q` → **38 passed in 2.31s**. Matches the orchestrator's targeted 38-pass figure; full 1363/2 accepted as captured evidence.

Note (context from the return): the audit-fork addition is a test-only coverage strengthening
(`test_1_non_adjacent_duplicate_is_also_detected`, S2-1) with no production-code change
(audit_log.py absent from the delta).

## Per-correction status

**C1 — CLOSED.** The bare-name `icacls` fail-open is eliminated. `os_acl.py` now routes both subprocesses through `_system32()` (os_acl.py:255-269): `_run_icacls` → `[_system32("icacls.exe"), …]` (os_acl.py:273-274) and the new owner query → `_system32(...\WindowsPowerShell\v1.0\powershell.exe)` (os_acl.py:299). Grep confirms **no remaining bare-name subprocess** in os_acl.py. The argv[0] tests genuinely pin the absolute path — `test_run_icacls_uses_absolute_system32_path` asserts `os.path.isabs(argv0)`, `endswith(\system32\icacls.exe)`, and `startswith(SystemRoot)`; `test_query_owner_uses_absolute_system32_powershell` asserts absolute + `\system32\windowspowershell\v1.0\powershell.exe`. The PS script (L-2) is fixed in parallel.

*SystemRoot fallback (`os.environ.get("SystemRoot", r"C:\Windows")`) — honest severity: LOW/INFO residual, not blocking.* To re-open a hijack an attacker must control the supervisor process's `SystemRoot` env var — a system variable whose authoritative value requires admin to change; a user-scoped override is non-standard and additionally requires (a) persistent HKCU\Environment write, (b) planting `icacls.exe`/`powershell.exe` in the redirected `System32`, and (c) the supervisor launching in that poisoned session. That is a large step up from the eliminated CWD file-drop, affects only the activation-time posture read (never shadow), and is moot on an already-hardened (Admin-owned RX) config. Optional gold-plating: resolve windir via `GetWindowsDirectoryW`/ctypes instead of the env var. Not required.

**L-1 — APPLIED (correct).** `evaluate_file` (after DACL-clean + probe-denied) and `evaluate_directory` (after DACL-clean) now call `_confirm_owner_elevated` (os_acl.py:416-425, 448-455). Fail-closed directions verified by code and tests: elevated owner → PROTECTED; non-elevated owner → NOT_PROTECTED (owner retains implicit WRITE_DAC/WRITE_OWNER); owner-query error/empty → UNKNOWN. The owner query (`_query_owner`, os_acl.py:290-317) is **absolute powershell path**, **injection-safe** (list-arg subprocess, no shell; `-LiteralPath '<path with '' doubled>'` inside a single-quoted PS string where `'` is the only metacharacter and it is escaped; `-LiteralPath` disables globbing), and **bounded/non-destructive** (`-NoProfile -NonInteractive`, 20s timeout, `Get-Acl` read-only). Combined verdict now requires clean DACL **and** elevated owner on **both** file and parent. Tests `OwnerVerdictTests` (elevated→PROTECTED, user→NOT_PROTECTED, error→UNKNOWN) confirm.

**L-2 — APPLIED.** `harden_controller_config.ps1` resolves `$Icacls`/`$Takeown` via `Join-Path $env:SystemRoot "System32"` (lines 76-82) and every `Invoke-Step` uses those absolute paths (apply + rollback). Elevated-context `$env:SystemRoot` tampering is an **acceptable residual**: the script is owner-launched once under UAC from a known context, and poisoning an admin-launched process's environment is a far higher bar than the eliminated bare-name CWD/PATH resolution.

**S3-1 — APPLIED (fail-closed inversion, no new fail-open).** `AceEntry.dangerous_rights` is now `frozenset(r for r in self.rights if r not in READ_ONLY_RIGHTS)` (os_acl.py:111-117): a **safe-subset allowlist** — any right token not a recognised read/execute/list code (inheritance flags already stripped in parsing) is dangerous and fails toward NOT_PROTECTED. Unknown/new/malformed tokens can no longer slip through as "safe" (test `test_unrecognised_token_fails_toward_not_protected`, token `ZZ` → NOT_PROTECTED). Verified strictly more conservative, with no regression to the intended PROTECTED state: the applied grant `(RX)` → token `RX` ∈ READ_ONLY_RIGHTS, and elevated principals' `(F)` is skipped as elevated — so a correctly-hardened config still reads PROTECTED.

## No new surface / dependency / posture change

- New runtime surface is exactly one addition — the bounded, absolute-path, injection-safe, read-only `powershell … Get-Acl` owner query (a required L-1 control), plus no new network/eval/exec/os.system.
- Zero new dependencies (stdlib only; `os`/`subprocess`/`sys`/`pathlib` already imported; no manifest/lockfile edits).
- No posture change: cli.py doctor (posture-not-check), config.py digest gate, SHADOW-ONLY forwarding, and R129 boundary are all untouched (those files absent from the delta). The audit-fork delta is test-only (S2-1 coverage; audit_log.py unchanged). No secrets/PII in the delta.

## C2 status

Unchanged. The Scope-1 park→approve residual (byte anchor is journal-resident; operator-named digest does not cover forwarded bytes) is not touched by this delta and remains the activation-time owner item tracked by the orchestrator (surface residual-3 verbatim in the activation decision line, or close by binding forwarded content to the operator-known `approval_digest` before supervised-auto). No delta-driven change.

**G5 DELTA VERDICT: PASS at a27068d**

Per-correction summary for the ledger: **C1 CLOSED** (absolute System32 paths, argv[0] pinned; SystemRoot-fallback is a LOW/INFO non-blocking residual), **L-1 APPLIED** (fail-closed owner assertion; owner query absolute/injection-safe/bounded), **L-2 APPLIED** (script uses `$env:SystemRoot` absolute paths; elevated-context residual acceptable), **S3-1 APPLIED** (safe-subset inversion, no new fail-open). No new attack surface, dependency, or posture change. **C2 unchanged** — activation-time owner item.
