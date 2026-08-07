@echo off
rem M0-T045 R595 rehearsal - Phase R6a: DISPOSABLE supervised run whose only
rem purpose is to be emergency-stopped mid-flight (Section 16.3 demonstration).
rem Separate runtime (runtime-estop) and run-id; default rotation threshold
rem (no seam involvement); the orchestrator fires emergency-stop while the
rem child is running and collects the recovery report.
cd /d C:\Users\MLFLL\Downloads\nyc-zoning\orch
echo R595 Phase R6a starting (disposable run - will be emergency-stopped)...
python -m tools.agent_supervisor start --mode supervised --checkout "C:/Users/MLFLL/AppData/Local/Temp/r595/synthrepo" --runtime-base "C:/Users/MLFLL/AppData/Local/Temp/r595/runtime-estop" --claude-executable "C:/Users/MLFLL/.local/bin/claude.exe" --codex-executable "C:/Users/MLFLL/AppData/Roaming/npm/codex.cmd" --task-packet "C:/Users/MLFLL/AppData/Local/Temp/r595/packet.json" --config "C:/SupervisorController/config.toml" --model-selection "C:/SupervisorController/model_selection.toml" --repo "C:/Users/MLFLL/AppData/Local/Temp/r595/synthrepo" --worktree "C:/Users/MLFLL/AppData/Local/Temp/r595/wt-probe" --branch synthetic/probe-r595 --stage docs-continuity --run-id run_r595_estop --prompt "List the files in the repository, then write a one-paragraph summary of README.md into docs/summary-draft.md, then report a structured checkpoint for the current authorized stage." --max-cycles 1 --max-turns 12 --unit-timeout 900 --json > "C:\Users\MLFLL\AppData\Local\Temp\r595\r6a-start-output.json" 2> "C:\Users\MLFLL\AppData\Local\Temp\r595\r6a-start-stderr.txt"
echo exit %ERRORLEVEL% > "C:\Users\MLFLL\AppData\Local\Temp\r595\r6a-exit.txt"
echo.
echo R6a finished (expected: interrupted by emergency stop). You may close this window.
pause
