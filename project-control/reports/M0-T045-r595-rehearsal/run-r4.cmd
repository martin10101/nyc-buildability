@echo off
rem M0-T045 R595 rehearsal - Phase R4: the owner's digest-bound approval of the
rem parked pending prompt (fires owner_approved_pending_prompt -> FORWARD_PROMPT
rem and consumes the record), then the resume `start` that forwards the approved
rem prompt unchanged and actuates the ARMED rotation seam live.
cd /d C:\Users\MLFLL\Downloads\nyc-zoning\orch
echo R595 Phase R4 step 1: approving the exact parked prompt digest...
python -m tools.agent_supervisor resume-pending-prompt --checkout "C:/Users/MLFLL/AppData/Local/Temp/r595/synthrepo" --runtime-base "C:/Users/MLFLL/AppData/Local/Temp/r595/runtime-r595" --approve-prompt-digest e6f112c60334b5692082bb50c3e25a1b86e19e33be475b46489f8a2e3587cdb7 --json > "C:\Users\MLFLL\AppData\Local\Temp\r595\r4-resume-output.json" 2> "C:\Users\MLFLL\AppData\Local\Temp\r595\r4-resume-stderr.txt"
if errorlevel 1 (
  echo APPROVAL REFUSED - see r4-resume-stderr.txt. Stopping here.
  echo exit-approve %ERRORLEVEL% > "C:\Users\MLFLL\AppData\Local\Temp\r595\r4-exit.txt"
  pause
  exit /b 1
)
echo Approval recorded; journal now at FORWARD_PROMPT. Step 2: resuming the run
echo (forward the approved prompt unchanged; the armed seam actuates live)...
python -m tools.agent_supervisor start --mode supervised --checkout "C:/Users/MLFLL/AppData/Local/Temp/r595/synthrepo" --runtime-base "C:/Users/MLFLL/AppData/Local/Temp/r595/runtime-r595" --claude-executable "C:/Users/MLFLL/.local/bin/claude.exe" --codex-executable "C:/Users/MLFLL/AppData/Roaming/npm/codex.cmd" --task-packet "C:/Users/MLFLL/AppData/Local/Temp/r595/packet.json" --config "C:/SupervisorController/config.toml" --model-selection "C:/SupervisorController/model_selection.toml" --repo "C:/Users/MLFLL/AppData/Local/Temp/r595/synthrepo" --worktree "C:/Users/MLFLL/AppData/Local/Temp/r595/wt-probe" --branch synthetic/probe-r595 --stage docs-continuity --run-id run_r595_rehearsal --prompt "Append one short dated line to docs/continuity-log.md summarizing the README's current state, then report a structured checkpoint for the current authorized stage." --max-cycles 2 --max-turns 12 --unit-timeout 900 --context-rotation-threshold 1 --json > "C:\Users\MLFLL\AppData\Local\Temp\r595\r4-start-output.json" 2> "C:\Users\MLFLL\AppData\Local\Temp\r595\r4-start-stderr.txt"
echo exit %ERRORLEVEL% > "C:\Users\MLFLL\AppData\Local\Temp\r595\r4-exit.txt"
echo.
echo R4 finished - exit code recorded to r4-exit.txt. You may close this window.
pause
