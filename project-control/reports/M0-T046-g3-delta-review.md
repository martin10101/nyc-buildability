# G3 DELTA RE-REVIEW — M0-T046

**Reviewer:** code-reviewer (read-only, independent) · **Lane:** G3 (correctness/contracts/tests)
**Delta:** `git diff 569d1a7..a27068d` · **New head confirmed:** `a27068db17ff20426a587fd04ed00eea827c909d` on `task/M0-T046-preactivation`
**Delta surface (name-status):** 6 files — `os_acl.py`, `harden_controller_config.ps1`, `README.md`, `test_agent_supervisor_os_acl.py`, `test_agent_supervisor_audit_fork_lock.py`, producer report (M). **Scope-1 `loop.py`/`cli.py` and `audit_log.py` source untouched** (confirmed by name-status). Stdlib-only preserved; no new deps; no forbidden paths.
**Reproduction (sandbox):** `pytest tools/test_agent_supervisor_os_acl.py tools/test_agent_supervisor_audit_fork_lock.py -q` → **38 passed** (matches orchestrator's targeted run; full suite 1363/2 accepted as captured).

## Delta findings (G3 lane)

**(1) C1 — absolute System32 path resolution — CORRECT at all invocation sites.**
`_system32(exe)` = `os.path.join(SystemRoot, "System32", exe)` with `C:\Windows` fallback. Both Python subprocess sites use it: `_run_icacls` → `…\System32\icacls.exe` (os_acl.py:274); `_query_owner` → `…\System32\WindowsPowerShell\v1.0\powershell.exe` (os_acl.py:299). Grep confirms **no bare-name tool invocation remains** in os_acl.py. The ps1 applies the same fix (`$Icacls`/`$Takeown` from `$env:SystemRoot\System32`) across all its icacls/takeown sites (G5 L-2). Any resolution failure → `FileNotFoundError`/nonzero → fail-closed error → UNKNOWN. On WOW64 the redirected path still resolves; env-var poisoning is a strictly higher-privilege threat than the CWD-hijack this removes. Correct.

**(2) L-1 — owner query + `_confirm_owner_elevated` wiring — CORRECT, fail-closed, no unguarded PROTECTED.**
I traced **every** PROTECTED construction reachable from the live entry points: `evaluate_file` builds its `PROTECTED` `candidate` only after (ACL-clean ∧ probe==denied) and then returns `_confirm_owner_elevated(...)`; `evaluate_directory` returns `acl_verdict` unless PROTECTED, in which case it returns `_confirm_owner_elevated(...)`; `evaluate_controller_config_acl`/`_combine` require BOTH already-confirmed. **No live path yields PROTECTED without the owner check.** Directions correct: user/non-elevated owner → NOT_PROTECTED (owner recorded in evidence); owner-query error or empty owner → UNKNOWN; elevated owner → PROTECTED. Bounded, read-only `Get-Acl -LiteralPath` with single-quote escaping. Consistent with the harden script (`takeown /A` → Administrators owns → post-apply doctor will satisfy the owner clause).

**(3) S3-1 — safe-subset inversion — RESOLVED.** `dangerous_rights = frozenset(r for r in self.rights if r not in READ_ONLY_RIGHTS)` (inheritance flags already stripped in parse). READ_ONLY_RIGHTS enumerates the standard read/execute/list codes (R, RX, RD, REA, RA, RC, X, S, GR, GE, L); any unknown/new/modify token now fails **toward NOT_PROTECTED**. No false NOT_PROTECTED on legitimate read-only ACLs: the hardened `(RX)` fixture and elevated `(F)` principals still yield PROTECTED at the ACL level (VerdictLogicTests unchanged and green). `DANGEROUS_RIGHTS` is now illustrative-only, correctly documented as non-gating.

**(4) S2-1 — non-adjacent duplicate test — RESOLVED.** `test_1_non_adjacent_duplicate_is_also_detected` re-appends a copy of sequence 2 after sequence 5 and asserts `verify_chain` → `duplicate_sequence` at `failed_sequence=2`, `load_error` set, and `append` → `append_to_damaged_chain`. Correctly exercises the whole-file `seen`-set path (I verified verify_chain hits the `seq in seen` branch before the gap/prev_digest checks). Locks the behavior my S2-1 flagged.

**(5) README — RESOLVED.** The garbled "The Phase-4 set. Three of the earlier ones are worth explaining:" is replaced with "Three of the Phase-4 tests are worth explaining:". Reads cleanly.

**(6) No regression / no scope widening.** Scope-1 approval-binding code untouched; `audit_log.py` source unchanged (only its test grew). No existing PROTECTED-asserting test is broken by the owner check — every prior PROTECTED assertion is either at the pure `evaluate_acl_entries` level (owner check not applicable) or short-circuits before the owner check (probe==writable/error, or direct mocking). Confirmed by 38/38 targeted and the reproduced 1363/2 full suite.

**(7) The 7 new tests test what they claim** (each read): `AbsoluteToolPathTests` (2, capture argv → absolute System32 path for icacls + powershell), `OwnerVerdictTests` (3, elevated→PROTECTED / user→NOT_PROTECTED / query-error→UNKNOWN, platform-independent via mocks), `test_unrecognised_token_fails_toward_not_protected` (ZZ→NOT_PROTECTED), `test_1_non_adjacent_duplicate_is_also_detected`. Deterministic, no network/credentials.

## Per-finding status update

| Finding | Prior | Status at `a27068d` |
|---|---|---|
| G5 C1 (System32 abs path) | BLOCKING (G5) | **Resolved** — all Python + ps1 sites; 2 tests |
| G5 L-1 (elevated-owner assertion) | — | **Resolved** — wired both verdicts, fail-closed; 3 tests |
| S3-1 (safe-subset inversion) | MINOR (open) | **Resolved** — inverted + 1 test |
| S2-1 (non-adjacent dup coverage) | MINOR/INFO (open) | **Resolved** — 1 test |
| README garbled sentence | INFO (open) | **Resolved** |
| S3-2 (locale/SID sensitivity) | MINOR/INFO | **Still INFO** — now also affects `_owner_is_elevated` (same English-name set); direction stays fail-closed (localized/SID owner → NOT_PROTECTED). Non-blocking. |
| S3-3 (rollback ownership / dry-run elevation) | INFO | Unchanged INFO, non-blocking |

## Acceptance conditions (carried, unchanged by this delta)

1. **DCV R124 adjudication** (BLOCKING for acceptance) — the AS-1/R124 literal-wording question (operator names the S13.5 approval digest; forwarded bytes bound to a park-time anchor) is untouched by this delta and remains for the directive-compliance-verifier/owner.
2. **Post-apply live PROTECTED proof** (orchestrator follow-up) — still required after the owner's elevated `harden_controller_config.ps1` run; the delta strengthens it (doctor must now also see an elevated owner, which the script's `takeown /A` provides).

No new BLOCKING or MAJOR G3 defects introduced by the delta. All targeted fixes are correct, fail-closed, and covered by tests.

**G3 DELTA VERDICT: PASS at a27068d**
