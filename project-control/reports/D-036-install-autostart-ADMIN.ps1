# D-036-R001 + R003 - install the supervisor autostart tasks.
# RUN THIS IN AN ELEVATED (Administrator) PowerShell:
#   Right-click Start > "Terminal (Admin)" / "Windows PowerShell (Admin)", then:
#   powershell -ExecutionPolicy Bypass -File "C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\D-036-install-autostart-ADMIN.ps1"
#
# Creates TWO scheduled tasks that both run the pinned wrapper
# C:\SupervisorController\autostart-launch.ps1 (which relaunches the loop only if
# it is not already running), with a retry-every-4-minutes-up-to-50-times policy:
#   1. NYCBuildabilitySupervisorBoot          - at logon (covers reboot / CC late to reopen)
#   2. NYCBuildabilitySupervisorWeeklyThursday - Thursday 21:00 local (the weekly Fable reset)
# Idempotent: re-running replaces both. To remove: see the UNINSTALL block at the bottom.

$ErrorActionPreference = 'Stop'

$wrapper = 'C:\SupervisorController\autostart-launch.ps1'
if (-not (Test-Path $wrapper)) { throw "wrapper not found: $wrapper" }

$psExe  = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$action = New-ScheduledTaskAction -Execute $psExe `
    -Argument "-NonInteractive -ExecutionPolicy Bypass -File `"$wrapper`"" `
    -WorkingDirectory 'C:\Users\MLFLL\Downloads\nyc-zoning\wt-controller-src'

# Run as the current user, with highest privileges, whether or not logged in.
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType S4U -RunLevel Highest

# Retry policy: every 4 minutes, up to 50 times, until the wrapper reports success (exit 0).
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartInterval (New-TimeSpan -Minutes 4) -RestartCount 50 `
    -ExecutionTimeLimit (New-TimeSpan -Hours 4) `
    -MultipleInstances IgnoreNew

# 1. Boot / logon task
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName 'NYCBuildabilitySupervisorBoot' `
    -Action $action -Principal $principal -Settings $settings -Trigger $logonTrigger `
    -Description 'NYC Buildability supervisor: relaunch the loop at logon if not running (D-036-R003).' -Force | Out-Null

# 2. Weekly Thursday 21:00 local task (the normal Fable weekly reset)
$weeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Thursday -At '9:00PM'
Register-ScheduledTask -TaskName 'NYCBuildabilitySupervisorWeeklyThursday' `
    -Action $action -Principal $principal -Settings $settings -Trigger $weeklyTrigger `
    -Description 'NYC Buildability supervisor: relaunch the loop at the weekly Fable reset (Thu 9PM), retry until running (D-036-R001/R003).' -Force | Out-Null

Write-Output "=== installed tasks ==="
foreach ($n in 'NYCBuildabilitySupervisorBoot','NYCBuildabilitySupervisorWeeklyThursday') {
    $t = Get-ScheduledTask -TaskName $n
    Write-Output ("{0}: state={1}; action={2} {3}" -f $t.TaskName, $t.State, $t.Actions[0].Execute, $t.Actions[0].Arguments)
    Write-Output ("   restart: every {0}, up to {1}x; startWhenAvailable={2}" -f $t.Settings.RestartInterval, $t.Settings.RestartCount, $t.Settings.StartWhenAvailable)
    Write-Output ("   triggers: " + (($t.Triggers | ForEach-Object { $_.CimClass.CimClassName }) -join ', '))
}
Write-Output "=== done. The loop will now be (re)launched at logon and every Thursday 9PM, retrying every 4 min up to 50x until it is running. ==="

# --- UNINSTALL (run elevated to remove) ---
# Unregister-ScheduledTask -TaskName 'NYCBuildabilitySupervisorBoot' -Confirm:$false
# Unregister-ScheduledTask -TaskName 'NYCBuildabilitySupervisorWeeklyThursday' -Confirm:$false
