# owner_allow_astra.ps1 — OWNER-RUN, ELEVATED (right-click > Run as administrator,
# or from an elevated PowerShell:  powershell -ExecutionPolicy Bypass -File <this file>)
#
# D-032 R002 (owner directive 2026-09-05): adds gpt-6-astra to the codex allowed_models
# allowlist in the immutable controller config. The file is deliberately admin-locked
# (Administrators FullControl; user read-only), so this single mutation is owner-executed.
# It makes a timestamped backup first and prints the exact before/after line.
#
# After this succeeds, the orchestrator (or you) applies the switch through the audited
# runtime path:
#   python -m tools.agent_supervisor set-codex-model gpt-6-astra --checkout C:\SupervisorController `
#     --config "C:\Program Files\SupervisorConfig\config.toml" --model-selection C:\SupervisorController\model_selection.toml
# (a running loop picks it up at the next checkpoint boundary; add --at-checkpoint there).

$ErrorActionPreference = 'Stop'
$p = 'C:\Program Files\SupervisorConfig\config.toml'
$old = 'allowed_models = ["gpt-5.6-sol", "gpt-5.6-terra"]'
$new = 'allowed_models = ["gpt-6-astra", "gpt-5.6-sol", "gpt-5.6-terra"]'

$t = [System.IO.File]::ReadAllText($p)
if ($t.Contains($new)) { Write-Host 'ALREADY APPLIED — nothing to do.'; exit 0 }
if (-not $t.Contains($old)) { throw "codex allowed_models line not found verbatim; refusing (file drifted?)" }

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Copy-Item $p ($p + '.bak-' + $stamp)
$idx = $t.IndexOf($old)
$t2 = $t.Substring(0, $idx) + $new + $t.Substring($idx + $old.Length)
[System.IO.File]::WriteAllText($p, $t2, (New-Object System.Text.UTF8Encoding $false))
Write-Host ('BACKUP:  ' + $p + '.bak-' + $stamp)
Write-Host ('BEFORE:  ' + $old)
Write-Host ('AFTER:   ' + $new)
Write-Host 'CONFIG UPDATED — gpt-6-astra is now allowlisted for the codex reviewer.'
