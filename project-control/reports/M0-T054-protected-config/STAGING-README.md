# M0-T054 — Staged protected-config change: add `claude-opus-4-8` to `[claude].allowed_models`

Owner authorization: **D-010 source-028, R311–R314** (narrowly supersedes R297 for this exact
allowlist addition only). Prepared by the orchestrator; **awaiting the owner's elevated apply**.
Nothing live was modified to produce this package.

## 1. What changes (and proof only one value changes)

Exactly one line changes in `C:\Program Files\SupervisorConfig\config.toml`:

```diff
 [claude]
 # Empty list = only the account/CLI default may be used; no explicit Claude
 # selection is permitted (directive §3.1). Most conservative pilot posture.
-allowed_models = []
+allowed_models = ["claude-opus-4-8"]
```

No other line changes. `[controller].default_mode = "shadow"`, `[codex].allowed_models`, and every
other value are byte-identical. (The `[claude]` comment above is intentionally left unchanged so the
diff shows exactly one value change per R313; it is now slightly stale and can be refreshed in a
later non-protected pass if desired.)

## 2. Hashes

| | SHA-256 |
|---|---|
| **current** config.toml (712 bytes, LF) | `29eb765eabce05b81dcbea33fd4d28800479596e9b23fd4d4fa334f6ee7da1cb` |
| **staged** config.toml (729 bytes, LF) — the new expected value | `9560f901e40e64cc320698c6cea9d5996e9e8495fb3ed22c6e681a6ebf1581e5` |

Complete staged file: `config.staged.toml` (in this directory). This is the exact content the
elevated command copies into place.

## 3. Pre-apply validation (already run, read-only)

- Staged config **parses**: `claude_allowed_models = ('claude-opus-4-8',)`.
- `validate_selection` against the staged config with `[claude] model = "claude-opus-4-8"` →
  **ok = True, errors = []** (the selection that is currently `selection_rejected` will be accepted
  once this is applied).

## 4. Full-vector dry-run (the exact ACL operations the tested hardening script will run)

The tested procedure is `tools/agent_supervisor/harden_controller_config.ps1` (M0-T046/T049/T050/T051,
already reviewed + regression-tested). It **never edits config content** — it only rewrites the DACL
deterministically (`/reset` → `/inheritance:r` → explicit three-ACE grant) for the file and its
dedicated parent. It **refuses to run unelevated**, which is why I could not execute the dry-run
myself; the exact vector it will print/execute (file = `C:\Program Files\SupervisorConfig\config.toml`,
dir = `C:\Program Files\SupervisorConfig`, user = `LAPTOP-M7D730QA\MLFLL`) is:

```
takeown.exe /F "C:\Program Files\SupervisorConfig\config.toml" /A
takeown.exe /F "C:\Program Files\SupervisorConfig" /A
icacls.exe "C:\Program Files\SupervisorConfig\config.toml" /reset
icacls.exe "C:\Program Files\SupervisorConfig\config.toml" /inheritance:r
icacls.exe "C:\Program Files\SupervisorConfig\config.toml" /grant:r BUILTIN\Administrators:(F) "NT AUTHORITY\SYSTEM:(F)" LAPTOP-M7D730QA\MLFLL:(RX)
icacls.exe "C:\Program Files\SupervisorConfig" /reset
icacls.exe "C:\Program Files\SupervisorConfig" /inheritance:r
icacls.exe "C:\Program Files\SupervisorConfig" /grant:r BUILTIN\Administrators:(OI)(CI)(F) "NT AUTHORITY\SYSTEM:(OI)(CI)(F)" LAPTOP-M7D730QA\MLFLL:(RX)
icacls.exe "C:\Program Files\SupervisorConfig\config.toml"   (show resulting ACL)
icacls.exe "C:\Program Files\SupervisorConfig"               (show resulting ACL)
```

Result: file + parent owned by `BUILTIN\Administrators`, unelevated `MLFLL` = **Read+Execute only**
(no Write/Delete/rename/WriteDAC/AddFile/DeleteChild) — i.e. **PROTECTED**, unchanged from today.

**Optional** — you may run the live dry-run first (elevated; changes nothing):

```
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\harden_controller_config.ps1" -ConfigPath "C:\Program Files\SupervisorConfig\config.toml" -DryRun
```

## 5. THE ONE elevated command to apply (paste into an ELEVATED PowerShell)

Copies the staged content into place (elevated write; the content change), then re-runs the tested
hardening script (re-applies the deterministic PROTECTED DACL). No manual TOML editing, no
hand-written icacls:

```
Copy-Item -LiteralPath "C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T054-protected-config\config.staged.toml" -Destination "C:\Program Files\SupervisorConfig\config.toml" -Force; powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\harden_controller_config.ps1" -ConfigPath "C:\Program Files\SupervisorConfig\config.toml"
```

Then tell me it's applied. **Stop here for the owner.**

## 6. Post-apply doctor proof I will run (R314; unelevated)

- config content == `config.staged.toml`; SHA-256 == `9560f901…1581e5`;
- protected FILE ACL = PROTECTED; protected PARENT ACL = PROTECTED;
- intended three-principal DACL only (Administrators:F, SYSTEM:F, MLFLL:RX);
- config readable; `model_selection.toml` still writable by the ordinary account;
- explicit `claude-opus-4-8` selection **accepted** by `validate_selection`;
- `default_mode = shadow`; active runtime = supervised; LIMITED-AUTO off.

If any check is unexpected, I stop and report — no product execution continues.

## 7. RESOLUTION — applied 2026-08-09, owner decision "A" (accept)

The owner applied the elevated command. The R314 doctor proof (`doctor_proof.py`,
output `doctor_proof_output.txt`) initially showed **9/10 PASS** with one miss: the live
SHA was `6aef12a9…`, not the pre-registered LF `9560f901…`. Root cause: **line-ending-only** —
git autocrlf converted the staged file (this `reports/` path lacked the `eol=lf` pin the
`directives/` path has) from LF (729 B) to CRLF (746 B), and `Copy-Item` copied the CRLF form.
Proven benign: the applied file with `\r\n` stripped hashes to exactly the pre-registered
`9560f901…`. CRLF is valid TOML; the supervisor parses and accepts it.

**Owner chose (A): accept the applied CRLF file as correct.** The recorded expected SHA is
therefore the applied value **`6aef12a9f60a6a64d7af77de3c071289c35dfe60977239e901df8d642c3fffde`**.
Re-run verdict: **ALL PASS (12/12)** — content correct, PROTECTED file+parent, exact
three-principal DACL, `claude-opus-4-8` accepted against the LIVE config, `default_mode=shadow`,
codex unchanged, allowlist exactly `[claude-opus-4-8]`, and the CR-stripped content == the
pre-registered LF SHA. The mutable worker `model_selection.toml` `[claude] model` was then set to
`claude-opus-4-8` (R296/R308) and validated against the live config (`validate_selection` ok=True).
