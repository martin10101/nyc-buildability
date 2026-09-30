<#
  mission-control.ps1  --  Owner Mission-Control dashboard launcher (READ-ONLY viewer)

  This script runs the internal owner dashboard from a DEDICATED, ISOLATED git worktree.
  It never touches your active development checkout and never commits, pushes, changes task
  state, or modifies the control plane. All git commands are scoped to the viewer worktree.

  USAGE (from anywhere; PowerShell):
      .\mission-control.ps1              # check freshness vs origin/main, then launch
      .\mission-control.ps1 -Refresh     # fast-forward THIS viewer worktree to latest origin/main, then launch
      .\mission-control.ps1 -Check       # only report fresh/stale; do not launch, do not change anything

  Stop the dashboard with Ctrl+C in this window.
#>
[CmdletBinding()]
param(
    [switch]$Refresh,   # update the viewer worktree to the latest origin/main before launching
    [switch]$Check,     # only report freshness; do not launch
    [int]$Port = 3037   # distinct port so it never clashes with your dev server
)

$ErrorActionPreference = 'Stop'

# --- Fixed, known locations (edit only if you move the folders) ---------------
$Worktree = 'C:\Users\MLFLL\Downloads\nyc zoning\mission-control-view'
$WebDir   = Join-Path $Worktree 'apps\web'

function Fail($msg) { Write-Host "ERROR: $msg" -ForegroundColor Red; exit 1 }

if (-not (Test-Path $Worktree)) { Fail "Viewer worktree not found at: $Worktree" }
if (-not (Test-Path $WebDir))   { Fail "apps\web not found in viewer worktree: $WebDir" }

# --- 1) Learn the latest origin/main (fetch updates only remote-tracking refs;
#         it never modifies any worktree's files, index, or branches) ----------
Write-Host "Checking latest origin/main ..." -ForegroundColor Cyan
$fetchOk = $true
try {
    git -C $Worktree fetch origin main --quiet
} catch {
    $fetchOk = $false
    Write-Host "  (could not reach origin -- offline? Showing local state only.)" -ForegroundColor Yellow
}

$localSha  = (git -C $Worktree rev-parse HEAD).Trim()
$localShort = $localSha.Substring(0,7)

$remoteSha = $null
try { $remoteSha = (git -C $Worktree rev-parse origin/main).Trim() } catch { }

$behind = 0
$isStale = $false
if ($remoteSha) {
    if ($remoteSha -ne $localSha) {
        $isStale = $true
        try { $behind = [int](git -C $Worktree rev-list --count "HEAD..origin/main").Trim() } catch { $behind = 0 }
    }
}

# --- 2) Report freshness ------------------------------------------------------
Write-Host ""
Write-Host "Dashboard data source (viewer worktree):" -ForegroundColor White
Write-Host "  Showing SHA : $localShort  ($localSha)"
if ($remoteSha) {
    Write-Host "  origin/main : $($remoteSha.Substring(0,7))  ($remoteSha)"
}
if ($isStale) {
    Write-Host ""
    Write-Host "  >>> STALE: this dashboard is $behind commit(s) BEHIND origin/main." -ForegroundColor Yellow
    Write-Host "      The numbers you see reflect SHA $localShort, not the latest merged work." -ForegroundColor Yellow
    Write-Host "      Run:  .\mission-control.ps1 -Refresh   to update this viewer safely." -ForegroundColor Yellow
} elseif ($remoteSha) {
    Write-Host "  >>> UP TO DATE with origin/main." -ForegroundColor Green
} else {
    Write-Host "  >>> Could not confirm origin/main (offline). Showing local SHA $localShort." -ForegroundColor Yellow
}
Write-Host ""

if ($Check) { exit 0 }

# --- 3) Optional safe refresh (this viewer worktree ONLY) ---------------------
if ($Refresh) {
    if (-not $fetchOk -or -not $remoteSha) { Fail "Cannot refresh while offline / origin unknown." }
    if ($isStale) {
        Write-Host "Refreshing viewer worktree to origin/main ($($remoteSha.Substring(0,7))) ..." -ForegroundColor Cyan
        $oldSha = $localSha
        # Detached checkout: moves this worktree's HEAD only. node_modules/.next are git-ignored,
        # so nothing you need is disturbed. Never affects your dev checkout.
        git -C $Worktree checkout --detach $remoteSha --quiet
        $localSha  = (git -C $Worktree rev-parse HEAD).Trim()
        $localShort = $localSha.Substring(0,7)
        Write-Host "  Now showing SHA: $localShort" -ForegroundColor Green

        # If the dependency lockfile changed between SHAs, reinstall to match.
        $lockChanged = $true
        try { git -C $Worktree diff --quiet $oldSha $localSha -- apps/web/package-lock.json; $lockChanged = ($LASTEXITCODE -ne 0) } catch { $lockChanged = $true }
        if ($lockChanged) {
            Write-Host "  Lockfile changed -- reinstalling dependencies (npm ci) ..." -ForegroundColor Cyan
            Push-Location $WebDir
            $env:PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = '1'
            npm ci
            Pop-Location
        }
        Write-Host ""
    } else {
        Write-Host "Already up to date -- nothing to refresh." -ForegroundColor Green
        Write-Host ""
    }
}

# --- 4) Ensure dependencies exist (self-healing first run) --------------------
if (-not (Test-Path (Join-Path $WebDir 'node_modules'))) {
    Write-Host "Installing dependencies for the first time (npm ci) ..." -ForegroundColor Cyan
    Push-Location $WebDir
    $env:PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = '1'
    npm ci
    Pop-Location
    Write-Host ""
}

# --- 5) Launch the dashboard (read-only; internal flag ON) --------------------
Write-Host "Starting Mission Control ..." -ForegroundColor Cyan
Write-Host ""
Write-Host "  OPEN THIS IN YOUR BROWSER:  http://localhost:$Port/dashboard" -ForegroundColor Green
Write-Host ""
Write-Host "  (Press Ctrl+C in this window to stop.)" -ForegroundColor DarkGray
Write-Host ""

Set-Location $WebDir
$env:INTERNAL_OWNER_DASHBOARD_ENABLED = '1'   # visibility gate ON (internal only)
$env:NEXT_TELEMETRY_DISABLED = '1'
$env:PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = '1'

npx next dev -p $Port
