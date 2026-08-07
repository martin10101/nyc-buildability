@echo off
rem M0-T045 R595 rehearsal - Phase R4b (fixed code): the owner's digest-bound approval of the
rem parked pending prompt (fires owner_approved_pending_prompt -> FORWARD_PROMPT
rem and consumes the record), then the resume `start` that forwards the approved
rem prompt unchanged and actuates the ARMED rotation seam live.
cd /d C:\Users\MLFLL\Downloads\nyc-zoning\orch
echo R595 Phase R4b (fixed code) step 1: approving the exact parked prompt digest...
python -m tools.agent_supervisor resume-pending-prompt --checkout "C:/Users/MLFLL/AppData/Local/Temp/r595/synthrepo" --runtime-base "C:/Users/MLFLL/AppData/Local/Temp/r595/runtime-r595b" --approve-prompt-digest a4c3d170e7a0558d9ea6a50877bfcd7827101dc55c92168f963e292e6fec31af --json > "C:\Users\MLFLL\AppData\Local\Temp\r595\r4b-resume-output.json" 2> "C:\Users\MLFLL\AppData\Local\Temp\r595\r4b-resume-stderr.txt"
if errorlevel 1 (
  echo APPROVAL REFUSED - see r4b-resume-stderr.txt. Stopping here.
  echo exit-approve %ERRORLEVEL% > "C:\Users\MLFLL\AppData\Local\Temp\r595\r4b-exit.txt"
  pause
  exit /b 1
)
echo Approval recorded; journal now at FORWARD_PROMPT. Step 2: resuming the run
echo (forward the approved prompt unchanged; the armed seam actuates live)...
python -m tools.agent_supervisor start --mode supervised --checkout "C:/Users/MLFLL/AppData/Local/Temp/r595/synthrepo" --runtime-base "C:/Users/MLFLL/AppData/Local/Temp/r595/runtime-r595b" --claude-executable "C:/Users/MLFLL/.local/bin/claude.exe" --codex-executable "C:/Users/MLFLL/AppData/Roaming/npm/codex.cmd" --task-packet "C:/Users/MLFLL/AppData/Local/Temp/r595/packet.json" --config "C:/SupervisorController/config.toml" --model-selection "C:/SupervisorController/model_selection.toml" --repo "C:/Users/MLFLL/AppData/Local/Temp/r595/synthrepo" --worktree "C:/Users/MLFLL/AppData/Local/Temp/r595/wt-probe" --branch synthetic/probe-r595 --stage docs-continuity --run-id run_r595_rehearsal_b --prompt "Append one short dated line to docs/continuity-log.md summarizing the README's current state, then report a structured checkpoint for the current authorized stage." --max-cycles 2 --max-turns 12 --unit-timeout 900 --context-rotation-threshold 1 --json > "C:\Users\MLFLL\AppData\Local\Temp\r595\r4b-start-output.json" 2> "C:\Users\MLFLL\AppData\Local\Temp\r595\r4b-start-stderr.txt"
echo exit %ERRORLEVEL% > "C:\Users\MLFLL\AppData\Local\Temp\r595\r4b-exit.txt"
echo.
echo R4 finished - exit code recorded to r4b-exit.txt. You may close this window.
pause
