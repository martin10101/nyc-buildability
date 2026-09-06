# overnight_product_run.ps1 — OWNER-RUN overnight loop driver (D-032 Amendment 2, 2026-09-06).
#
# Paste into a NEW PowerShell window (not the one already running the warm-up run) and leave it
# open overnight. It:
#   1. waits for the currently-running supervisor run to finish (single-instance lock frees),
#   2. launches the PRODUCT run (M2-T020: live spatial data wiring) with overnight-sized bounds,
#   3. relaunches ONLY across clean rotation seams (fresh worker session after a 400k rotation),
#      at most $MaxLaunches times; ANY other stop (review wall, budget breaker, refusal needing a
#      human) ends the script and leaves the exit report on screen.
# Every launch still passes the controller's full preflight/recovery classification — this script
# cannot bulldoze a safety stop; it only saves you from retyping the start at 3am.

$ErrorActionPreference = 'Continue'
$MaxLaunches = 8
$RunId = 'persistent-local-03'
$Repo = 'C:\Users\MLFLL\Downloads\nyc-zoning\ctl24'
Set-Location $Repo

for ($i = 1; $i -le $MaxLaunches; $i++) {
    Write-Host ("`n=== overnight launch {0} of max {1} - {2} ===" -f $i, $MaxLaunches, (Get-Date -Format 'HH:mm:ss'))
    $out = python -m tools.agent_supervisor start `
        --mode limited-auto --owner-enable-bounded-auto `
        --checkout C:\SupervisorController `
        --claude-executable C:\Users\MLFLL\.local\bin\claude.exe `
        --codex-executable C:\Users\MLFLL\AppData\Roaming\npm\codex.cmd `
        --config "C:\Program Files\SupervisorConfig\config.toml" `
        --model-selection C:\SupervisorController\model_selection.toml `
        --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json" `
        --task-packet C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M2-T020.json `
        --repo C:\Users\MLFLL\Downloads\nyc-zoning\wt-m2t020 `
        --worktree C:\Users\MLFLL\Downloads\nyc-zoning\wt-m2t020 `
        --branch task/M2-T020-live-spatial-provider `
        --packet-queue C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\campaigns\D-032-product-queue-v2.json `
        --max-tasks 2 --max-cycles 24 --unit-timeout 2700 `
        --run-id $RunId `
        --prompt "Full 40-character SHAs in every checkpoint SHA field (git rev-parse HEAD), never abbreviated. Use only packet-documented test commands; avoid PowerShell and undocumented shell commands. Follow the packet acceptance scenarios S1-S4 exactly: settings-gated live provider, default OFF, all fail-safes preserved." 2>&1 | Out-String
    Write-Host $out

    if ($out -match 'could not be acquired|another supervisor instance') { Write-Host 'previous run still holds the lock; waiting 120s...'; Start-Sleep -Seconds 120; $i--; continue }
    if ($out -match 'stopped=rotate_session') { Write-Host 'clean rotation seam - relaunching fresh worker in 20s...'; Start-Sleep -Seconds 20; continue }
    if ($out -match 'pending_requests|unsafe_or_drifted|stale_state') {
        # Claude's watcher cleans these up between attempts; be patient (max ~2h of 5-min waits),
        # counted separately from real launches. Each retry is just another refused start until
        # the cleanup lands - no state is changed, nothing is bulldozed.
        if (-not $script:patience) { $script:patience = 0 }
        $script:patience++
        if ($script:patience -le 24) { Write-Host ("cleanup needed (attempt {0}/24); waiting 300s for Claude's watcher..." -f $script:patience); Start-Sleep -Seconds 300; $i--; continue }
    }
    Write-Host "`nRun ended on a condition that needs a human (or is simply done). Leave this output for Claude. Good night."
    break
}
