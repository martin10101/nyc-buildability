# G4 DELTA RE-REVIEW — M0-T046 rework increment

**Reviewer:** qa-engineer (independent, read-only). **New code identity (git rev-parse):** `a27068db17ff20426a587fd04ed00eea827c909d` on `task/M0-T046-preactivation` (prior reviewed `569d1a7`). **Delta surface:** `git diff 569d1a7..a27068d` = 6 files (os_acl.py, harden_controller_config.ps1, README.md, test_os_acl.py, test_audit_fork_lock.py, producer-report.md) — all inside `allowed_paths`; no forbidden path, no manifest/lockfile, no dependency added. SCOPE-1 (loop.py/cli.py) and SCOPE-2 production (audit_log.py) untouched; SCOPE-2 gained only a test. Confirmed against the earlier-frozen G4 PASS baseline.

Reproduction summary (from the return preamble): full suite independently reproduced **1363 passed, 2 skipped** (matches producer and 1356+7=1363); targeted set deterministic at 38.

## Item-by-item verification

**(1) Count arithmetic — reproduced.**
- Targeted `pytest test_os_acl.py test_audit_fork_lock.py -q` → **38 passed** (os_acl **31** = 25+6, audit_fork_lock **7** = 6+1); re-run → 38 again (deterministic).
- Full `pytest tools/test_agent_supervisor_*.py -q` → **1363 passed, 2 skipped** (92s), independently reproduced. 1356 + 7 = 1363 ✅. Zero regressions; the 2 skips are the same POSIX guards.

**(2) The 7 new tests are deterministic, independent, non-vacuous.** All hermetic (own `TemporaryDirectory`; `subprocess.run` / `_query_owner` / `_run_icacls` / `sys.platform` monkeypatched and restored in `finally`; no ordering coupling — the interleaved full-suite pass confirms no contamination). In-process mutation (no repo edit):
- **abs-path (C1):** revert `_system32` → bare name ⇒ **2/2** `AbsoluteToolPathTests` RED (`argv[0]` not absolute: `icacls.exe`, `WindowsPowerShell\v1.0\powershell.exe`). → *Yes, they fail if reverted to bare-name.*
- **owner (L-1):** unwire `_confirm_owner_elevated` (pre-fix passthrough) ⇒ **2/3** `OwnerVerdictTests` RED (user-owner `PROTECTED`≠`NOT_PROTECTED`; owner-query-error `PROTECTED`≠`UNKNOWN`); elevated-owner correctly stays GREEN. → *Yes, they fail if the owner check is unwired.*
- **unknown-token (S3-1):** revert `dangerous_rights` to old `rights & DANGEROUS_RIGHTS` ⇒ **1/1** RED (`(RX,ZZ)` → `PROTECTED`≠`NOT_PROTECTED`).

**(3) S2-1 non-adjacent genuinely exercises a different shape.** The adjacent lock dups the TAIL (seq 5, `failed_sequence=5`); the new test re-appends `records[1]` (seq 2) AFTER seq 5 — a non-adjacent early-sequence recurrence, `failed_sequence=2`, plus `load_error` + append-refuses assertions. Mutation to an **adjacency-only** `_load_head_from_log` ⇒ adjacent `test_1` stays GREEN (0 fail) while the non-adjacent test turns RED (`load_error unexpectedly None`). Confirms it pins the whole-file `seen`-set span, not neighbour comparison.

**(4) No pre-existing assertion weakened.** The `test_os_acl.py` delta is pure additions (unknown-token method + `AbsoluteToolPathTests` + `OwnerVerdictTests`); no existing fixture or assertion removed/modified. All 7 pre-existing `VerdictLogicTests` fixtures produce identical verdicts under the S3-1 inversion (I re-derived each: RX/RX-only → PROTECTED; M/W/DC/M,DC/Everyone-W → NOT_PROTECTED) and still pass within the 31.

**(5) Gaps.** **G1 (AS-4 live PROTECTED deferred) — IMPROVED:** the boundary is now materially stronger (L-1 rejects a user-owner-with-clean-DACL that the first increment would have called PROTECTED; C1/L-2 close the CWD/PATH tool-hijack under both the inspector and the elevated apply script). Verdict logic and the harden script remain consistent (script's `takeown /A` yields `BUILTIN\Administrators` owner, which `_owner_is_elevated` accepts), so the deferred post-apply live proof still resolves PROTECTED. Remains an orchestrator pre-activation verification item, not a defect. **G2 (deleting audit.jsonl resets the fork lock) — unchanged**, informational/low, untouched by this rework. **G3 (BEFORE=1317 not re-run) — IMPROVED:** both delta endpoints (1356 and 1363) are now independently reproduced, so the +7 delta is fully verified end-to-end.

**Evidence integrity:** the producer-report "Rework increment" append accurately describes all six items (C1, L-1, L-2, S3-1, S2-1, README) with correct file:line anchors, correct test names, correct counts (os_acl 31 / audit_fork_lock 7 / targeted 38 / full 1363-2), a correct changed-files list, and an honest "SCOPE-1 binding untouched / G5 C2 deferred to owner" note — all of which reproduce.

No blocking corrections. The rework is a clean, well-tested strengthening of SCOPE-3 with a complementary SCOPE-2 regression lock; nothing in the prior G4 PASS is undermined.

**G4 DELTA VERDICT: PASS at a27068d**

Requested action for orchestrator: record G4 = PASS at reviewed identity `a27068d`; carry gap **G1** forward as the pre-activation (not pre-acceptance) live-PROTECTED verification.
