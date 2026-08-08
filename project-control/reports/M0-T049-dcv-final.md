# M0-T049 — Directive-compliance verification (FINAL) — VERBATIM verifier return

Orchestrator preservation note: saved verbatim from the directive-compliance-verifier
agent-return channel (no transport entities present). Frozen head
`e942b28e6f10525b179c6af43134358e73a7ff31`. Recorded by the orchestrator 2026-08-08.

---

I have reproduced all primary evidence. Compiling the verification report now.

---

# M0-T049 — Independent Directive-Compliance Verification (D-010 source-019, R173–R183)

**Verifier:** directive-compliance-verifier (read-only). **Producer:** backend-engineer. **Reviewers:** code-reviewer (G3), security-reviewer (G5) — all four roles distinct.
**Frozen head:** `e942b28e6f10525b179c6af43134358e73a7ff31` (branch `control/M0-T049-hardening-parse-fix`).
**Reviewed engineering identity:** script blob `ca3811cd7e38a044bd0e01056e95b5028b6ce615`; test blob `6854d9b6b42b58905bd714f3d33df54150e2eca9`; content_manifest_sha256 `0821cb81…` (identical at G3 and G5).
**Environment:** Windows 11, Windows PowerShell **5.1.26100.8875**, unelevated (IsAdmin=False). Every claim below was reproduced by me from primary evidence; producer/reviewer reports were treated as unverified claims.

**OVERALL VERDICT: PASS** (10/11 SATISFIED at the frozen head; R181 is a return duty that is compliant-to-date with its final act intrinsically post-merge — no VIOLATED / UNVERIFIABLE result).

---

## 1. Applicable-set confirmation (resolver, run myself)

`DirectiveRegistry().load().derive_applicable(M0-T049.json)` → exactly **11** IDs: R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183. `evaluate_task_refs` → `ok=True`, cited==applicable, `missing_ids=[]`, `invalid_refs=[]`, `unresolved=[]`. D-010 `is_active=True`, zero integrity errors. All 11 carry `applicability.task_ids=["M0-T037","M0-T049"]`, `lifecycle_events=["accept"]`, `amendment_sequence=19`; grep confirms **exactly 11** rows at `amendment_sequence 19` (no extras). Matches the packet's declared applicable set precisely.

## 2. Intake review (source-019 vs matrix)

- **Digest:** I recomputed `sha256(source-019-amendment.md)` = `9c5a24bf0d88125cbefb502a2a1bbc525087dec6979e9f01e9428b70b70e8c05` = manifest `sources[19].content_digest_sha256`. **Match.** Chain: source-019 amends source-018, sequence 19. `locked_requirement_ids` count 183 includes all R173–R183; R001–R172 untouched (append-only preserved).
- **Validator:** `python tools/validate_directive_compliance.py --check` → **exit 0**.
- **Forward trace (every source obligation → a row):** "STOP activation / do not move config again / do not modify contents" → R173; "treat as narrowly bounded pre-activation defect fix" → R174; "FIRST read-only inspect file+parent ACLs, report honestly, do not assume PROTECTED" → R175; "correct ONLY the interpolation defect via `${…}` at every affected occurrence" → R176; "add a test that PARSES the entire script under WinPS 5.1" → R177; "re-run existing OS-ACL/hardening tests plus new parse test" → R178; "require independent G3+G5 before elevated execution" → R179; "produce a NEW blob; old 0f01d649 barred" → R180; "return only after committed/reviewed/merged with exact blob + rerun command" → R181; "preserve model_selection.toml unchanged and mutable" → R182; "do not broaden into ACL redesign/supervisor work" → R183.
- **Reverse trace:** all 11 rows anchor to `source-019-amendment.md#parser-defect`; none invented.
- **Missing/weakened/combined/invented:** none. R173 enumerates three standstill sub-clauses (no activation / no re-move / no content change) inside one HOLD row — each preserved verbatim and independently verifiable, so this is atomic grouping, not a lossy merge. No requirement softens its source wording (R176 keeps "ONLY … EVERY affected occurrence"; R178 keeps "existing tests plus the new parse test"; R181 keeps "committed, reviewed, merged").

**Intake verdict: PASS.**

## 3. Identity integrity

- Frozen head `e942b28`: script `ca3811cd`, test `6854d9b`. Task commit `47a2721` blobs identical.
- Main defective blob (`c298159`) = `0f01d649a64a4fcb1f96b805564cc40889d9a389` (the barred blob) — confirmed.
- G3 reviewed_sha `d6c501d` and G5 reviewed_sha `58db7a0` both carry script `ca3811cd` + test `6854d9b` + `content_manifest_sha256 0821cb81…` (byte-identical reviewed material).
- Between G5 review commit and frozen head, the **only** changed allowed-path file is `tasks/M0-T049.json` (progress 85→95, updated_at) — pure control-plane churn; script, test, and producer report are byte-identical. **Material identity stable.**

## 4. Reviewer independence

Producer = backend-engineer; G3 = code-reviewer; G5 = security-reviewer; verifier = me. All distinct. `verification.json` contains **no** pre-existing M0-T049 rows (`task_verifications` empty of M0-T049) — no pre-recorded verdict.

## 5. Prohibited-action evidence (nothing merged/accepted/dispatched/deployed/installed/purchased/closed/activated)

- **Not merged:** local `main` = `origin/main` = `c298159`; script on origin/main still `0f01d649` (defective). `git branch --contains e942b28` = only the control branch; merge-base = c298159. Fix lives only on the control branch.
- **Not accepted:** task `status=awaiting_gate`, `progress=95`; not in the accepted count.
- **No PR:** `gh pr list --head control/M0-T049-hardening-parse-fix` returns empty.
- **Not activated / config not re-moved / contents intact:** config still at `C:\Program Files\SupervisorConfig\config.toml`; I re-measured SHA-256 = `29EB765E…DA1CB` (intact); file ACL still `Authenticated Users:(M)` i.e. NOT hardened → the elevated hardening never ran → nothing activated (shadow-only).

## 6. Per-requirement findings (reproduced primary evidence)

| ID | Class | Verdict | Reproduced evidence |
|----|-------|---------|---------------------|
| **R173** | hold | **PASS** | Config not re-moved (still at `…\SupervisorConfig\config.toml`); I re-measured contents SHA-256 `29EB765E…DA1CB` = recorded pre-move digest → contents unmodified. Nothing activated: measured file ACL `Authenticated Users:(M)` proves hardening never ran; whole-branch engineering delta (`c298159..e942b28`) touches no config content / move / activation surface. Hold respected. |
| **R174** | obligation | **PASS** | Defect reproduced under WinPS 5.1: defective blob `0f01d649` → `parse_errors=4` at lines 130/132/154/165 ("Variable reference is not valid…"); fixed blob `ca3811cd` → `parse_errors=0`. Fix is the bounded 4-token brace change; unelevated run reaches its own elevation refusal post-parse (`test_script_refuses_to_run_unelevated` PASSED). |
| **R175** | obligation | **PASS** | I independently re-ran `icacls`/`Get-Acl`/`Get-FileHash`. FILE: `Authenticated Users:(M)`, `SYSTEM:(F)`, `Administrators:(F)`, `Users:(RX)`, owner `LAPTOP-M7D730QA\MLFLL` → NOT protected. PARENT: inherited Program Files DACL (TrustedInstaller/SYSTEM/Admins/Users:RX/CREATOR OWNER/App pkgs), owner `BUILTIN\Administrators` → protected. SHA `29EB765E…DA1CB` intact. `M0-T049-acl-posture-inspection.md` reports exactly this (NOT protected, parent protected, SHA intact) — honest, not assumed PROTECTED. |
| **R176** | obligation | **PASS** | `git diff c298159 47a2721` on the script = exactly 4 changes (`$UnelevatedUser:` → `${UnelevatedUser}:`) at lines 130/132/154/165 (+4/-4), nothing else. `git show e942b28:…ps1 | grep '\$UnelevatedUser:'` → no matches (all braced); remaining `$env:` uses parse cleanly (`parse_errors=0`). Every affected occurrence fixed; only those. |
| **R177** | obligation | **PASS** | New `test_script_parses_cleanly_under_windows_powershell_51` uses `[System.Management.Automation.Language.Parser]::ParseFile` via `powershell.exe` (WinPS 5.1) asserting `parse_errors=0`; it RAN (not skipped) and PASSED. I reproduced the same parser class: fixed→0, defective→4, so the test is provably RED-on-defective/GREEN-on-fixed (error-list based, not exit-code). Refusal test hardened with `assertNotIn("variable reference is not valid", …)` to reject a parse-error masquerade. |
| **R178** | obligation | **PASS** | I ran `pytest tools/test_agent_supervisor_os_acl.py` → **32 passed** (both PS tests executed, not skipped). Full `tools/test_agent_supervisor_*.py` → **1381 passed, 2 skipped, 0 failures**. Matches the claimed baseline at the frozen identity. |
| **R179** | sequencing | **PASS** | G3 PASS (code-reviewer, reviewed_sha `d6c501d`, blob `ca3811cd`) and G5 PASS (security-reviewer, reviewed_sha `58db7a0`, blob `ca3811cd`) both recorded; both reviewed the exact frozen blobs, both independent. Elevated execution has NOT occurred (config still unprotected; not merged). Both independent reviews are recorded PASS BEFORE any elevation → sequencing honored. The owner's actual elevated run remains a correctly-gated future post-merge act. |
| **R180** | obligation | **PASS** | New reviewed blob `ca3811cd7e38a044bd0e01056e95b5028b6ce615` at frozen head (and at both gate SHAs). Old `0f01d649` confirmed defective (parse_errors=4), remains only on unmerged main, not used for elevation (nothing elevated). Carry-forward (G3-A3, reproduced): `requirements.json:5723` (immutable source-017 preflight) still names `0f01d649` as "expected" — R180 supersedes it; orchestrator must pin `ca3811cd` in the activation package. Disclosed, not a violation. |
| **R181** | return | **PASS (conduct-to-date; return act pending post-merge)** | Classification `return` ∉ `LIFECYCLE_ELIGIBLE_CLASSIFICATIONS={obligation,sequencing}` → **not mechanically deferrable**; ruled on conduct-to-date per packet instruction. Committed ✓ (`ca3811cd` on control branch); reviewed ✓ (G3+G5 PASS); merged — not yet (correct at a pre-merge head); exact new blob `ca3811cd7e38a044bd0e01056e95b5028b6ce615` and exact elevated rerun command are prepared/available (G5 §6: `powershell -ExecutionPolicy Bypass -File "tools\agent_supervisor\harden_controller_config.ps1" -ConfigPath "C:\Program Files\SupervisorConfig\config.toml"`; recommended `-DryRun` first; `-UnelevatedUser` per L-2). **No premature return issued** (compliant — the requirement forbids returning before merge). **Remaining act:** after merge, issue the owner-facing return with the merged blob + command (plus pre/post-run SHA re-verification). Neither VIOLATED nor UNVERIFIABLE. |
| **R182** | prohibition | **PASS** | `C:\SupervisorController\model_selection.toml` present; LastWriteUtc `2026-08-04T04:55:45Z` (4 days before the 2026-08-08 task) → unchanged during the task; ACL `Authenticated Users:(I)(M)` → mutable. Whole-branch engineering delta touches no `.toml`/model_selection. |
| **R183** | prohibition | **PASS** | Task commit `47a2721` = 3 files (script 4-token fix, test +43, producer report). Whole-branch engineering delta `c298159..e942b28` (excluding project-control) = **exactly 2 files**: `harden_controller_config.ps1`, `test_agent_supervisor_os_acl.py`. No supervisor `.py`, no ACL redesign, no config/activation change. Not broadened. |

## 7. Advisories weighed (none blocks any requirement wording)

- **G3-A1 (LOW):** refusal test's English-message negative assertion is weaker on localized Windows; the authoritative guard is the locale-independent parse test. Non-blocking.
- **G3-A2 (LOW):** parse test embeds the script path single-quoted; a path containing `'` would break it; repo path is safe. Test-only nit.
- **G3-A3 (reproduced):** stale barred-blob reference at `requirements.json:5723` (immutable source-017 preflight) — orchestrator must pin `ca3811cd`, never `0f01d649`, in the activation package. Carry-forward.
- **G5-L-1 (LOW):** parse test `skipUnless(IS_WINDOWS and which("powershell"))` silently skips where WinPS is absent; report notes the `supervisor-bridge` CI leg runs on `windows-latest` where it executes. Recommend enforcing a Windows CI leg. Non-blocking.
- **G5-L-2 (LOW, pre-existing):** `-UnelevatedUser` default may not match the real unelevated supervisor account — verify via `-DryRun` before the elevated run. Operational.

## 8. Harness (run by me, at frozen identity)

`validate_directive_compliance.py --check` → exit 0; `test_directive_compliance.py` → 102 OK; `test_project_control.py` → all 22 groups OK; `test_directive_reminder.py` → 12 OK; `test_agent_supervisor_os_acl.py` → 32 passed; full `test_agent_supervisor_*.py` → 1381 passed / 2 skipped.

## 9. Discrepancies

None material. The one process nuance: **R181 (return) is not mechanically deferral-eligible**, yet its final act (the owner-facing return) can occur only after merge, which is post-acceptance. The orchestrator must therefore **not treat acceptance as discharging R181** — it must issue the merge, then the owner return with blob `ca3811cd` + the documented command, and only then is the directive fully DONE. (Minor cosmetic: line 5723's text contains a pre-existing `\a` mojibake in an immutable source-017 row — out of M0-T049 scope, no action here.)

## 10. Recommendation

**PASS.** All 11 applicable requirements are compliant on reproduced primary evidence; no VIOLATED or UNVERIFIABLE result. Recommended orchestrator actions: (1) record the 11-row `verification.json` at reviewed identity (script `ca3811cd`, manifest `0821cb81`) with `reviewed_sha == HEAD e942b28` at accept time, mapping R181 as conduct-to-date compliant with the post-merge return outstanding; (2) proceed to merge under Tier A after green checks; (3) **immediately post-merge, discharge R181** — issue the owner return with blob `ca3811cd7e38a044bd0e01056e95b5028b6ce615` and the exact elevated rerun command; (4) carry forward G3-A3 (pin the new blob, never `0f01d649`, in the activation package) and the G5 pre/post-run SHA re-verification (`29eb765e…`) plus `-DryRun` principal check before the owner's elevated run; (5) R179 sequencing (reviews-before-elevation) is already satisfied — do not permit elevation before merge.

Key evidence files (absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\harden_controller_config.ps1`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\test_agent_supervisor_os_acl.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T049-acl-posture-inspection.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T049-g3-code-review.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T049-g5-security.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\directives\D-010-autonomous-engineering-restructure\source-019-amendment.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\directives\D-010-autonomous-engineering-restructure\requirements.json` (rows 6111–6494)
